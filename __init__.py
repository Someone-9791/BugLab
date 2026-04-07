"""
PythonDebugEnv - An OpenEnv environment for AI-driven code debugging.

This package provides a reinforcement learning environment where agents
debug broken Python code using a dual reward system:
- 70% weight: Test pass rate (deterministic)
- 30% weight: Static analysis quality score (deterministic)

For Meta PyTorch OpenEnv Hackathon 2026.
"""

__version__ = "0.1.0"
__author__ = "PythonDebugEnv Team"
