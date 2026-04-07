"""
BugLab Environment - OpenEnv environment for debugging Python code.
"""

import random
from typing import Any, Optional
from openenv.core import Environment
from models import DebugAction, DebugObservation, DebugState
from server.grader import run_tests_sandboxed, compute_reward
from bug_bank import PROBLEMS


# Explicit Task Abstraction Layer (Session 8 Improvement)
# Defines 3 distinct objectives with problem mappings
TASKS = {
    "fix_logic_bug": {
        "id": "fix_logic_bug",
        "name": "Fix Logic Bugs",
        "description": "Identify and correct logical errors in control flow (if/else, loops, conditionals)",
        "difficulty_range": ["easy", "medium"],
        "problem_ids": [
            "logic_001", "logic_002", "logic_003", "logic_004",  # logic_error category
            "off_by_one_001", "off_by_one_002", "off_by_one_003", "off_by_one_004",  # off_by_one category
            "edge_001", "edge_002"  # missing_edge_case category (easier ones)
        ],
        "grader": "test_logic_fix",
        "reward_weight": 0.33
    },
    "fix_algorithm_bug": {
        "id": "fix_algorithm_bug",
        "name": "Fix Algorithm Bugs",
        "description": "Correct algorithmic errors in data processing and computation",
        "difficulty_range": ["medium", "hard"],
        "problem_ids": [
            "type_001", "type_002", "type_003", "type_004",  # type_error category
            "loop_001", "loop_002", "loop_003", "loop_004",  # loop_error category
            "shadow_001", "shadow_002",  # variable shadowing
            "return_001"  # wrong_return category (easier ones)
        ],
        "grader": "test_algorithm_fix",
        "reward_weight": 0.33
    },
    "optimize_and_fix": {
        "id": "optimize_and_fix",
        "name": "Optimize Code and Fix",
        "description": "Improve code efficiency, readability, and style while maintaining correctness",
        "difficulty_range": ["hard"],
        "problem_ids": [
            "edge_003", "edge_004",  # harder edge cases
            "recursion_001", "recursion_002", "recursion_003",  # recursion_error category (challenging)
            "shadow_003",  # variable shadowing
            "return_002", "return_003", "return_004"  # wrong_return (harder cases)
        ],
        "grader": "test_optimization",
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
           - 60% automated test pass rate
           - 40% LLM code quality score
        4. Episode ends (single-turn environment)
    
    Attributes:
        problems: List of all available debugging problems
        current_problem: The active problem for this episode
        episode_id: Unique identifier for current episode
        step_count: Number of steps taken in current episode
    """
    
    # Global state for the environment (shared across instances)
    # This is necessary because OpenEnv creates new instances per request
    _global_problem = None
    _global_episode_id = None
    _global_attempt_count = 0
    _global_previous_score = 0.0  # Session 8: Track for reward shaping
    
    def __init__(self):
        """Initialize the environment with problem bank."""
        super().__init__()
        self.problems = PROBLEMS
        # Use class variables for state persistence across requests
        self._step_count = 0
    
    @property
    def current_problem(self):
        return PythonDebugEnvironment._global_problem
    
    @current_problem.setter
    def current_problem(self, value):
        PythonDebugEnvironment._global_problem = value
    
    @property
    def _episode_id(self):
        return PythonDebugEnvironment._global_episode_id
    
    @_episode_id.setter
    def _episode_id(self, value):
        PythonDebugEnvironment._global_episode_id = value
    
    @property
    def _attempt_count(self):
        return PythonDebugEnvironment._global_attempt_count
    
    @_attempt_count.setter
    def _attempt_count(self, value):
        PythonDebugEnvironment._global_attempt_count = value
    
    @property
    def _previous_score(self):
        return PythonDebugEnvironment._global_previous_score
    
    @_previous_score.setter
    def _previous_score(self, value):
        PythonDebugEnvironment._global_previous_score = value
    
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
        self._attempt_count = 0  # Reset attempt count for new episode
        self._previous_score = 0.0  # Session 8: Reset score tracking for reward shaping
        self._episode_id = episode_id or f"ep_{random.randint(10000, 99999)}"
        
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
        self._attempt_count += 1
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
        
        # Combine into final reward: 70% tests + 30% quality
        base_reward = 0.7 * test_score + 0.3 * quality_score
        
        # Session 8: Reward shaping - add improvement bonus
        improvement = base_reward - self._previous_score
        improvement_bonus = 0.0
        
        if improvement > 0.0:
            # 50% bonus for any improvement
            improvement_bonus = improvement * 0.5
            # Significant improvement bonus (>0.1 improvement)
            if improvement > 0.1:
                improvement_bonus += 0.1
        
        # Final reward with improvement bonus, clamped to [0, 1]
        reward = min(1.0, base_reward + improvement_bonus)
        
        # Store current score for next attempt
        self._previous_score = base_reward
        
        # Session 8: Rich Observations - build error summary from test details
        failed_tests = [t for t in test_details if t.get("status") == "fail"]
        error_tests = [t for t in test_details if t.get("status") in ("error", "timeout")]
        failed_count = len(failed_tests) + len(error_tests)
        
        error_summary = ""
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
        
        # Multi-step logic:
        # - Episode ends if score is excellent (>= 0.95) OR we've used all 3 attempts
        # - Otherwise, agent can keep trying
        done = (self._attempt_count >= 3) or (reward >= 0.95)
        
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
            attempt=self._attempt_count,
            max_attempts=3,
            done=done,
            improvement=improvement,
            improvement_bonus=improvement_bonus,
            test_details=test_details,  # Session 8: Rich observations
            error_summary=error_summary  # Session 8: Rich observations
        )
        
        return next_obs
    
    @property
    def state(self) -> DebugState:
        """
        Get current episode state metadata.
        
        Returns:
            DebugState with episode_id, step_count, and current problem
        """
        return DebugState(
            episode_id=self._episode_id,
            step_count=self._step_count,
            current_problem_id=self.current_problem["id"] if self.current_problem else None
        )

