"""
PythonDebugEnv server package.
Contains environment, grader, and FastAPI app.
"""

__version__ = "0.1.0"

from server.environment import PythonDebugEnvironment, TASKS
from server.grader import (
    test_logic_fix,
    test_algorithm_fix,
    test_optimization,
    run_tests_sandboxed,
    analyze_code_quality,
    compute_reward,
)

__all__ = [
    "PythonDebugEnvironment",
    "TASKS",
    "test_logic_fix",
    "test_algorithm_fix",
    "test_optimization",
    "run_tests_sandboxed",
    "analyze_code_quality",
    "compute_reward",
]
