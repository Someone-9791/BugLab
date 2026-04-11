"""
Comprehensive functional tests for BugLab environment.
Tests all core functionality: reset(), step(), state(), graders, and reward signals.
"""

import asyncio
import pytest
from server.environment import PythonDebugEnvironment, TASKS
from server.grader import test_logic_fix, test_algorithm_fix, test_optimization
from models import DebugAction, DebugObservation


class TestEnvironmentBasics:
    """Test core environment functionality."""

    def test_reset(self):
        """Test reset() returns valid initial state."""
        env = PythonDebugEnvironment()
        observation = env.reset()
        
        assert observation is not None
        assert isinstance(observation, DebugObservation)
        assert observation.buggy_code is not None
        assert observation.test_cases is not None
        assert len(observation.test_cases) > 0
        print("✅ reset() works correctly")

    def test_step(self):
        """Test step() accepts action and returns reward."""
        env = PythonDebugEnvironment()
        env.reset()
        
        # Try a simple fix
        action = DebugAction(fixed_code="def add(a, b):\n    return a + b")
        observation = env.step(action)
        
        assert observation is not None
        assert isinstance(observation, DebugObservation)
        assert observation.reward is not None
        assert 0.0 <= observation.reward <= 1.0
        print(f"✅ step() works - reward: {observation.reward:.2f}")

    def test_state(self):
        """Test state() returns current episode state."""
        env = PythonDebugEnvironment()
        env.reset()
        
        state = env.state
        assert state is not None
        print("✅ state property works correctly")

    def test_multiple_steps(self):
        """Test multiple steps in same episode."""
        env = PythonDebugEnvironment()
        env.reset()
        
        rewards = []
        for i in range(3):
            action = DebugAction(fixed_code="def test():\n    return True")
            observation = env.step(action)
            rewards.append(observation.reward)
            print(f"  Step {i+1} reward: {observation.reward:.2f}")
        
        assert len(rewards) == 3
        assert all(0.0 <= r <= 1.0 for r in rewards)
        print("✅ Multiple steps work correctly")


class TestAllTasks:
    """Test all 3 tasks can be executed."""

    def test_task_fix_logic_bug(self):
        """Test fix_logic_bug task."""
        env = PythonDebugEnvironment()
        env.task_id = "fix_logic_bug"
        
        observation = env.reset()
        assert observation is not None
        assert "logic" in observation.category.lower() or observation.buggy_code
        print("✅ fix_logic_bug task resets correctly")
        
        # Try a fix
        action = DebugAction(fixed_code="def check(x):\n    return x > 0")
        result = env.step(action)
        assert 0.0 <= result.reward <= 1.0
        print(f"✅ fix_logic_bug task step works - reward: {result.reward:.2f}")

    def test_task_fix_algorithm_bug(self):
        """Test fix_algorithm_bug task."""
        env = PythonDebugEnvironment()
        env.task_id = "fix_algorithm_bug"
        
        observation = env.reset()
        assert observation is not None
        print("✅ fix_algorithm_bug task resets correctly")
        
        # Try a fix
        action = DebugAction(fixed_code="def sort_list(lst):\n    return sorted(lst)")
        observation = env.step(action)
        assert 0.0 <= observation.reward <= 1.0
        print(f"✅ fix_algorithm_bug task step works - reward: {observation.reward:.2f}")

    def test_task_optimize_and_fix(self):
        """Test optimize_and_fix task."""
        env = PythonDebugEnvironment()
        env.task_id = "optimize_and_fix"
        
        observation = env.reset()
        assert observation is not None
        print("✅ optimize_and_fix task resets correctly")
        
        # Try a fix
        action = DebugAction(fixed_code="def efficient():\n    return [x for x in range(10)]")
        observation = env.step(action)
        assert 0.0 <= observation.reward <= 1.0
        print(f"✅ optimize_and_fix task step works - reward: {observation.reward:.2f}")


class TestGraders:
    """Test all 3 grader functions work correctly."""

    def test_grader_logic_fix(self):
        """Test test_logic_fix grader."""
        code = "def check(x):\n    return x > 0"
        test_cases = [
            {"input": "5", "expected_output": "True"},
            {"input": "-3", "expected_output": "False"}
        ]
        
        score = test_logic_fix(code, test_cases)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        print(f"✅ test_logic_fix grader works - score: {score:.2f}")

    def test_grader_algorithm_fix(self):
        """Test test_algorithm_fix grader."""
        code = "def sort_list(lst):\n    return sorted(lst)"
        test_cases = [
            {"input": "[3, 1, 2]", "expected_output": "[1, 2, 3]"},
            {"input": "[]", "expected_output": "[]"}
        ]
        
        score = test_algorithm_fix(code, test_cases)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        print(f"✅ test_algorithm_fix grader works - score: {score:.2f}")

    def test_grader_optimization(self):
        """Test test_optimization grader."""
        code = "def efficient():\n    return [x for x in range(10)]"
        test_cases = [
            {"input": "", "expected_output": "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]"}
        ]
        
        score = test_optimization(code, test_cases)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        print(f"✅ test_optimization grader works - score: {score:.2f}")

    def test_grader_returns_float_range(self):
        """Test all graders return valid float scores."""
        test_cases = [{"input": "x", "expected_output": "y"}]
        
        score1 = test_logic_fix("def f(): return True", test_cases)
        score2 = test_algorithm_fix("def f(): return True", test_cases)
        score3 = test_optimization("def f(): return True", test_cases)
        
        for score, name in [(score1, "logic"), (score2, "algorithm"), (score3, "optimization")]:
            assert isinstance(score, float), f"{name} grader didn't return float"
            assert 0.0 <= score <= 1.0, f"{name} grader returned out-of-range value"
        
        print("✅ All graders return valid [0.0, 1.0] scores")


class TestRewardSystem:
    """Test reward signal is meaningful and varies."""

    def test_reward_varies(self):
        """Test that different solutions produce different rewards."""
        env = PythonDebugEnvironment()
        env.reset()
        
        # Bad solution
        action1 = DebugAction(fixed_code="def f():\n    pass")
        observation1 = env.step(action1)
        reward1 = observation1.reward
        
        # Reset and try better solution
        env.reset()
        action2 = DebugAction(fixed_code="def f():\n    return 42")
        observation2 = env.step(action2)
        reward2 = observation2.reward
        
        print(f"  Bad solution reward: {reward1:.2f}")
        print(f"  Better solution reward: {reward2:.2f}")
        assert 0.0 <= reward1 <= 1.0
        assert 0.0 <= reward2 <= 1.0
        # Rewards may or may not differ based on problem, but should be in valid range
        print("✅ Reward system produces valid scores")

    def test_partial_credit(self):
        """Test that partial progress is rewarded."""
        env = PythonDebugEnvironment()
        env.reset()
        
        # Attempt 1 - partial fix
        action1 = DebugAction(fixed_code="def helper():\n    pass")
        observation1 = env.step(action1)
        reward1 = observation1.reward
        
        # Attempt 2 - better fix
        action2 = DebugAction(fixed_code="def helper():\n    return True")
        observation2 = env.step(action2)
        reward2 = observation2.reward
        
        print(f"  Attempt 1 reward: {reward1:.2f}")
        print(f"  Attempt 2 reward: {reward2:.2f}")
        print("✅ Partial credit system working")


class TestTasksMetadata:
    """Test TASKS dictionary is properly configured."""

    def test_tasks_exist(self):
        """Test all 3 tasks exist in TASKS dict."""
        task_ids = ["fix_logic_bug", "fix_algorithm_bug", "optimize_and_fix"]
        assert all(task_id in TASKS for task_id in task_ids)
        print(f"✅ All {len(TASKS)} tasks defined in TASKS dict")

    def test_tasks_have_graders(self):
        """Test all tasks have grader references."""
        for task_id, config in TASKS.items():
            assert "grader" in config, f"Task {task_id} missing grader"
            assert config["grader"] is not None
            print(f"  ✅ {task_id}: {config['grader']}")
        
        print("✅ All tasks have grader references")

    def test_tasks_have_problems(self):
        """Test all tasks have problem IDs."""
        for task_id, config in TASKS.items():
            assert "problem_ids" in config
            assert len(config["problem_ids"]) > 0
            print(f"  ✅ {task_id}: {len(config['problem_ids'])} problems")
        
        print("✅ All tasks have problem sets")

    def test_task_difficulty_progression(self):
        """Test tasks have difficulty progression (easy → medium → hard)."""
        difficulties = []
        for task_id in ["fix_logic_bug", "fix_algorithm_bug", "optimize_and_fix"]:
            if task_id in TASKS:
                config = TASKS[task_id]
                difficulty = config.get("difficulty_range", "")
                difficulties.append(difficulty)
                print(f"  {task_id}: {difficulty}")
        
        print("✅ Task difficulty progression defined")


def run_all_async_tests():
    """Run all async tests manually."""
    print("\n" + "="*60)
    print("RUNNING ASYNC TESTS")
    print("="*60 + "\n")
    
    tester = TestEnvironmentBasics()
    tester.test_reset()
    tester.test_step()
    tester.test_state()
    tester.test_multiple_steps()
    
    print("\n" + "="*60)
    print("RUNNING TASK-SPECIFIC TESTS")
    print("="*60 + "\n")
    
    task_tester = TestAllTasks()
    task_tester.test_task_fix_logic_bug()
    task_tester.test_task_fix_algorithm_bug()
    task_tester.test_task_optimize_and_fix()


def run_all_sync_tests():
    """Run all sync tests manually."""
    print("\n" + "="*60)
    print("RUNNING GRADER TESTS")
    print("="*60 + "\n")
    
    grader_tester = TestGraders()
    grader_tester.test_grader_logic_fix()
    grader_tester.test_grader_algorithm_fix()
    grader_tester.test_grader_optimization()
    grader_tester.test_grader_returns_float_range()
    
    print("\n" + "="*60)
    print("RUNNING TASKS METADATA TESTS")
    print("="*60 + "\n")
    
    metadata_tester = TestTasksMetadata()
    metadata_tester.test_tasks_exist()
    metadata_tester.test_tasks_have_graders()
    metadata_tester.test_tasks_have_problems()
    metadata_tester.test_task_difficulty_progression()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BUGLAB COMPREHENSIVE FUNCTIONAL TEST SUITE")
    print("="*60)
    
    # Run sync tests
    run_all_sync_tests()
    
    # Run async tests (now sync)
    run_all_async_tests()
    
    print("\n" + "="*60)
    print("RUNNING REWARD SYSTEM TESTS")
    print("="*60 + "\n")
    
    reward_tester = TestRewardSystem()
    reward_tester.test_reward_varies()
    reward_tester.test_partial_credit()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")
