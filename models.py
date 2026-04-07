"""
Pydantic models for PythonDebugEnv.
Defines Action, Observation, and State types for the RL environment.
"""

from pydantic import BaseModel, Field, field_serializer
from typing import Literal, Optional


class DebugAction(BaseModel):
    """
    Action submitted by the agent.
    Contains the fixed/corrected Python code.
    """
    fixed_code: str = Field(
        ...,
        description="The corrected Python code submitted by the agent"
    )


class DebugObservation(BaseModel):
    """
    Observation returned to the agent.
    Contains the buggy code and metadata about the problem.
    """
    problem_id: str = Field(
        ...,
        description="Unique identifier for this problem"
    )
    buggy_code: str = Field(
        ...,
        description="The broken Python code that needs to be fixed"
    )
    description: str = Field(
        ...,
        description="Human-readable description of what the code should do"
    )
    test_cases: list[dict] = Field(
        ...,
        description="List of test cases (not shown to agent, used for grading)"
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        ...,
        description="Problem difficulty level"
    )
    category: str = Field(
        "unknown",
        description="Bug category (e.g., logic_error, off_by_one)"
    )
    task_id: Optional[str] = Field(
        None,
        description="Task ID if problem belongs to a task (e.g., fix_logic_bug, fix_algorithm_bug)"
    )
    task_name: Optional[str] = Field(
        None,
        description="Human-readable task name (e.g., 'Fix Logic Bugs')"
    )
    reward: float = Field(
        0.0,
        description="Reward for the last action (0.0 on reset). Range: [0.0, 1.0]"
    )
    test_score: float = Field(
        0.0,
        description="Test-based score (70% weight). Range: [0.0, 1.0]. Only set after step()."
    )
    llm_score: float = Field(
        0.0,
        description="DEPRECATED - kept for backward compatibility"
    )
    quality_score: float = Field(
        0.0,
        description="Code quality score from static analysis (30% weight). Range: [0.0, 1.0]. Session 8."
    )
    quality_feedback: Optional[dict] = Field(
        None,
        description="Detailed code quality feedback with breakdown of checks and improvements"
    )
    improvement: float = Field(
        0.0,
        description="Score improvement from previous attempt. Session 8 reward shaping."
    )
    improvement_bonus: float = Field(
        0.0,
        description="Bonus reward for improvement between steps. Session 8 reward shaping."
    )
    test_details: list[dict] = Field(
        [],
        description="Detailed test results from last step. Each dict has: input, expected, actual, status (pass/fail/error), error. Session 8."
    )
    error_summary: str = Field(
        "",
        description="Human-readable summary of test failures/errors. Session 8 rich observations."
    )
    attempt: int = Field(
        0,
        description="Current attempt number (0 on reset, 1-3 after steps)"
    )
    max_attempts: int = Field(
        3,
        description="Maximum number of attempts allowed per episode"
    )
    done: bool = Field(
        False,
        description="Whether the episode is complete. True after step(), False on reset()"
    )
    
    @field_serializer('reward', 'done', 'test_score', 'llm_score', 'quality_score', 'attempt', 'max_attempts', 'task_id', 'task_name', 'improvement', 'improvement_bonus', 'test_details', 'error_summary', 'quality_feedback', when_used='always')
    def serialize_always(self, value):
        """Force serialization of all result fields even when they're defaults."""
        return value



class DebugState(BaseModel):
    """
    Environment state metadata.
    Tracks episode information and current progress.
    """
    episode_id: str | None = Field(
        None,
        description="Unique identifier for the current episode"
    )
    step_count: int = Field(
        0,
        description="Number of steps taken in the current episode"
    )
    current_problem_id: str | None = Field(
        None,
        description="ID of the currently active problem"
    )
