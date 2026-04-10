"""
BugLab Environment - OpenEnv environment for debugging Python code.
"""

import random
import re
import uuid
import logging
from typing import Any, Optional
from openenv.core import Environment
from models import DebugAction, DebugObservation, DebugState
from server.grader import run_tests_sandboxed, compute_reward
from bug_bank import PROBLEMS

logger = logging.getLogger(__name__)

# Common mistake hints for agents (PRIORITY 2)
CATEGORY_HINTS = {
    "logic_error": "Check comparison operators (>, <, >=, <=, ==, !=) - are they correct?",
    "off_by_one": "Check loop ranges and boundary conditions - should be n, n+1, or n-1?",
    "wrong_return": "Are you returning the correct variable? Check function return statements.",
    "type_error": "Check type conversions - do you need str(), int(), float(), list()?",
    "recursion_error": "Check recursion base case - does it stop? Check return statement.",
    "missing_edge_case": "Handle edge cases: empty lists, None values, negative numbers?",
    "variable_shadowing": "Check variable names - are inner/outer variables conflicting?",
}


def validate_episode_id(episode_id: str) -> str:
    """
    Validate episode ID format (PRIORITY 2).
    
    Args:
        episode_id: Episode identifier to validate
        
    Returns:
        str: Validated episode ID
        
    Raises:
        ValueError: If episode ID is invalid
    """
    if not episode_id:
        return None
    if len(episode_id) > 100:
        raise ValueError("Episode ID too long (max 100 characters)")
    if not re.match(r'^[a-zA-Z0-9_\-]+$', episode_id):
        raise ValueError("Episode ID contains invalid characters (allowed: alphanumeric, dash, underscore)")
    return episode_id


# Explicit Task Abstraction Layer (Session 8 Improvement)
# Defines 3 distinct objectives with problem mappings
TASKS = {
    "fix_logic_bug": {
        "id": "fix_logic_bug",
        "name": "Fix Logic Bugs",
        "description": "Identify and correct logical errors in control flow (if/else, loops, conditionals)",
        "difficulty_range": ["easy", "medium"],
        "problem_ids": [
            "logic_001", "logic_002", "logic_003", "logic_004",
            "off_by_one_001", "off_by_one_002", "off_by_one_003", "off_by_one_004",
            "edge_001", "edge_002"
        ],
        "grader": "server.grader:test_logic_fix",
        "reward_weight": 0.33
    },
    "fix_algorithm_bug": {
        "id": "fix_algorithm_bug",
        "name": "Fix Algorithm Bugs",
        "description": "Correct algorithmic errors in data processing and computation",
        "difficulty_range": ["medium", "hard"],
        "problem_ids": [
            "type_001", "type_002", "type_003", "type_004",
            "loop_001", "loop_002", "loop_003", "loop_004",
            "shadow_001", "shadow_002",
            "return_001"
        ],
        "grader": "server.grader:test_algorithm_fix",
        "reward_weight": 0.33
    },
    "optimize_and_fix": {
        "id": "optimize_and_fix",
        "name": "Optimize Code and Fix",
        "description": "Improve code efficiency, readability, and style while maintaining correctness",
        "difficulty_range": ["hard"],
        "problem_ids": [
            "edge_003", "edge_004",
            "recursion_001", "recursion_002", "recursion_003",
            "shadow_003",
            "return_002", "return_003", "return_004"
        ],
        "grader": "server.grader:test_optimization",
        "reward_weight": 0.34
    }
}


class PythonDebugEnvironment(Environment[DebugAction, DebugObservation, DebugState]):
    """
    An RL environment where agents debug broken Python code.
    
    Flow:
        1. reset() returns a buggy code problem
        2. Agent submits fixed code via step(action)
        3. Environment grades using dual reward:
           - 70% automated test pass rate
           - 30% code quality score
        4. Episode ends (single-turn environment)
    
    Attributes:
        problems: List of all available debugging problems
        current_problem: The active problem for this episode
        episode_id: Unique identifier for current episode
        step_count: Number of steps taken in current episode
    """
    
    def __init__(self):
        """Initialize the environment with problem bank (instance state, not class state)."""
        super().__init__()
        self.problems = PROBLEMS
        # PRIORITY 1.1: Convert to instance state for thread-safety
        self.current_problem = None
        self.current_episode_id = None
        self.current_attempt_count = 0
        self.current_previous_score = 0.0
        self._step_count = 0
    
    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs: Any
    ) -> DebugObservation:
        """
        Start a new episode with a debugging problem.
        
        Args:
            seed: Random seed for reproducibility
            episode_id: Custom episode identifier
            difficulty: Filter by difficulty level ('easy', 'medium', 'hard')
                       If None, randomly select from all problems
            task_id: Select from specific task ('fix_logic_bug', 'fix_algorithm_bug', 'optimize_and_fix')
                    If specified, difficulty is ignored
         
        Returns:
            DebugObservation with buggy code and problem metadata
        """
        # Select random problem from bank
        if seed is not None:
            random.seed(seed)
        
        # Determine available problems
        available_problems = self.problems
        selected_task_id = None
        selected_task_name = None
        
        # Priority 1: Task ID (if specified, use task's problem set)
        if task_id and task_id in TASKS:
            task = TASKS[task_id]
            selected_task_id = task_id
            selected_task_name = task["name"]
            available_problems = [p for p in self.problems if p.get("id") in task["problem_ids"]]
        # Priority 2: Difficulty filter
        elif difficulty and difficulty.lower() in ['easy', 'medium', 'hard']:
            available_problems = [p for p in self.problems if p.get('difficulty', '').lower() == difficulty.lower()]
        
        if not available_problems:
            # Fallback to all problems if no matches found
            available_problems = self.problems
        
        self.current_problem = random.choice(available_problems)
        
        # Reset episode state
        self._step_count = 0
        self.current_attempt_count = 0
        self.current_previous_score = 0.0
        # PRIORITY 2.8: Validate episode_id format
        try:
            self.current_episode_id = validate_episode_id(episode_id) if episode_id else f"ep_{uuid.uuid4().hex[:8]}"
        except ValueError as e:
            logger.warning(f"Invalid episode_id provided: {e}, generating new one")
            self.current_episode_id = f"ep_{uuid.uuid4().hex[:8]}"
        
        # Return observation
        return DebugObservation(
            problem_id=self.current_problem["id"],
            buggy_code=self.current_problem["buggy_code"],
            description=self.current_problem["description"],
            test_cases=self.current_problem["test_cases"],
            difficulty=self.current_problem["difficulty"],
            category=self.current_problem.get("category", "unknown"),
            task_id=selected_task_id,
            task_name=selected_task_name,
            reward=0.0,
            attempt=0,
            max_attempts=3,
            done=False
        )
    
    def step(
        self,
        action: DebugAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any
    ) -> DebugObservation:
        """
        Process agent's code fix and compute reward.
        
        Supports multi-step trajectory:
        - Agents get up to 3 attempts per problem
        - Episode ends after 3 attempts OR when score >= 0.95 (excellent solution)
        - Intermediate rewards provided on each attempt
        
        Args:
            action: DebugAction containing the fixed code
            timeout_s: Optional timeout for test execution
        
        Returns:
            DebugObservation with reward, done flag, and attempt tracking
        """
        self._step_count += 1
        self.current_attempt_count += 1
        problem = self.current_problem
        
        # Compute dual reward signals
        # Session 8: Get detailed test results for rich observations
        test_score, test_details = run_tests_sandboxed(
            action.fixed_code,
            problem["test_cases"],
            timeout_s=timeout_s,
            detailed=True  # Get detailed results for observation
        )
        
        # Session 8: Replace LLM scoring with static analysis (0.7/0.3 split)
        from server.grader import analyze_code_quality
        quality_score, quality_feedback = analyze_code_quality(action.fixed_code)
        
        # PRIORITY 2.6: Partial credit system - award points for passing tests
        # Base reward: 70% test score (now partial credit) + 30% quality
        base_reward = 0.7 * test_score + 0.3 * quality_score
        
        # Session 8: Reward shaping - add improvement bonus
        improvement = base_reward - self.current_previous_score
        improvement_bonus = 0.0
        
        # PRIORITY 2.6: Only apply improvement bonus if base_reward > 0
        if base_reward > 0.0:
            if improvement > 0.0:
                # Smaller bonus for improvement (50% of improvement)
                improvement_bonus = improvement * 0.5
                # Significant improvement bonus (>0.1 improvement)
                if improvement > 0.1:
                    improvement_bonus += 0.05
        
        # Final reward with improvement bonus, clamped to [0, 1]
        reward = min(1.0, base_reward + improvement_bonus)
        
        # Store current score for next attempt
        self.current_previous_score = base_reward
        
        # Session 8: Rich Observations - build error summary from test details
        failed_tests = [t for t in test_details if t.get("status") == "fail"]
        error_tests = [t for t in test_details if t.get("status") in ("error", "timeout")]
        failed_count = len(failed_tests) + len(error_tests)
        
        error_summary = ""
        # PRIORITY 2.7: Enhanced error messages - detailed error info
        error_details = {
            "test_failures": [],
            "total_tests": len(problem["test_cases"]),
            "passed_tests": sum(1 for t in test_details if t.get("status") == "pass")
        }
        
        if failed_count > 0:
            if failed_tests:
                # Summarize first failed test
                first_fail = failed_tests[0]
                error_summary = f"Failed test: Input {first_fail.get('input')} - Expected {first_fail.get('expected')}, got {first_fail.get('actual')}"
            if error_tests:
                # Summarize first error
                first_error = error_tests[0]
                error_msg = first_error.get("error", "Unknown error")
                error_summary = f"Error: {error_msg}" if not error_summary else error_summary + f" | {error_msg}"
            
            # Build detailed error info
            for i, tc in enumerate(problem["test_cases"]):
                if i < len(test_details):
                    result = test_details[i]
                    if result.get("status") in ("fail", "error"):
                        error_details["test_failures"].append({
                            "test_number": i + 1,
                            "input": tc.get("input"),
                            "expected": tc.get("expected"),
                            "got": result.get("actual"),
                            "error": result.get("error", "Assertion failed")
                        })
        
        # Multi-step logic:
        # - Episode ends if score is excellent (>= 0.95) OR we've used all 3 attempts
        # - Otherwise, agent can keep trying
        done = (self.current_attempt_count >= 3) or (reward >= 0.95)
        
        # PRIORITY 2.5: Add common mistake hints when answer is wrong
        hint = ""
        if reward < 1.0:
            category = problem.get("category", "unknown")
            hint = CATEGORY_HINTS.get(category, "Review your logic carefully")
        
        # Create observation - return same problem for next attempt if not done
        next_obs = DebugObservation(
            problem_id=problem["id"],
            buggy_code=problem["buggy_code"] if not done else "",  # Re-present problem if continuing
            description=problem["description"] if not done else "Episode complete",
            test_cases=problem["test_cases"] if not done else [],
            difficulty=problem["difficulty"],
            category=problem.get("category", "unknown"),
            task_id=problem.get("task_id"),
            task_name=problem.get("task_name"),
            reward=reward,
            test_score=test_score,
            quality_score=quality_score,
            quality_feedback=quality_feedback,  # Add detailed feedback
            attempt=self.current_attempt_count,
            max_attempts=3,
            done=done,
            improvement=improvement,
            improvement_bonus=improvement_bonus,
            test_details=test_details,  # Session 8: Rich observations
            error_summary=error_summary  # Session 8: Rich observations
        )
        
        # Add hint field if not present, and error_details
        next_obs.hint = hint
        next_obs.error_details = error_details
        
        return next_obs
    
    def enumerate_tasks(self) -> dict:
        """
        Enumerate all available tasks with their graders.
        
        Returns:
            dict: Dictionary with 'tasks' list and 'total' count
        """
        tasks_list = []
        for task_id, task_config in TASKS.items():
            tasks_list.append({
                "id": task_config.get("id"),
                "name": task_config.get("name"),
                "description": task_config.get("description"),
                "difficulty_range": task_config.get("difficulty_range"),
                "grader": task_config.get("grader"),
                "num_problems": len(task_config.get("problem_ids", []))
            })
        return {"tasks": tasks_list, "total": len(tasks_list)}
    
    @property
    def state(self) -> DebugState:
        """
        Get current episode state metadata.
        
        Returns:
            DebugState with episode_id, step_count, and current problem
        """
        return DebugState(
            episode_id=self.current_episode_id,
            step_count=self._step_count,
            current_problem_id=self.current_problem["id"] if self.current_problem else None
        )

