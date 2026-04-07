"""
BugLab Environment Client.

This client enables agents to interact with the BugLab debugging environment
through a persistent WebSocket connection.
"""

from typing import Dict
from openenv.core import EnvClient
from openenv.core.client_types import StepResult

from models import DebugAction, DebugObservation, DebugState


class PythonDebugEnv(EnvClient[DebugAction, DebugObservation, DebugState]):
    """
    Client for the BugLab environment.
    
    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions for debugging Python code.
    Each client instance has its own dedicated environment session on the server.
    
    Example:
        >>> # Connect to a running server
        >>> with PythonDebugEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     print(f"Problem: {result.observation.description}")
        ...     print(f"Buggy code:\\n{result.observation.buggy_code}")
        ...
        ...     # Submit fix
        ...     action = DebugAction(fixed_code="def add(a, b): return a + b")
        ...     result = client.step(action)
        ...     print(f"Reward: {result.reward}")
        ...     print(f"Test score: {result.observation.test_score}")
    
    Example with Docker:
        >>> # Automatically start container and connect
        >>> client = PythonDebugEnv.from_docker_image("python-debug-env:latest")
        >>> try:
        ...     result = client.reset()
        ...     action = DebugAction(fixed_code=result.observation.buggy_code)
        ...     result = client.step(action)
        ... finally:
        ...     client.close()
    """

    def _step_payload(self, action: DebugAction) -> Dict:
        """
        Convert DebugAction to JSON payload for step message.
        
        Args:
            action: DebugAction instance with fixed_code
        
        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "fixed_code": action.fixed_code,
        }

    def _parse_result(self, payload: Dict) -> StepResult[DebugObservation]:
        """
        Parse server response into StepResult[DebugObservation].
        
        Args:
            payload: JSON response data from server
        
        Returns:
            StepResult with DebugObservation
        """
        obs_data = payload.get("observation", {})
        
        # Parse observation with all fields
        observation = DebugObservation(
            problem_id=obs_data.get("problem_id", ""),
            buggy_code=obs_data.get("buggy_code", ""),
            description=obs_data.get("description", ""),
            test_cases=obs_data.get("test_cases", []),
            difficulty=obs_data.get("difficulty", "easy"),
            category=obs_data.get("category", "unknown"),
            task_id=obs_data.get("task_id"),
            task_name=obs_data.get("task_name"),
            reward=obs_data.get("reward", 0.0),
            test_score=obs_data.get("test_score", 0.0),
            llm_score=obs_data.get("llm_score", 0.0),
            quality_score=obs_data.get("quality_score", 0.0),
            improvement=obs_data.get("improvement", 0.0),
            improvement_bonus=obs_data.get("improvement_bonus", 0.0),
            test_details=obs_data.get("test_details", []),
            error_summary=obs_data.get("error_summary", ""),
            attempt=obs_data.get("attempt", 0),
            max_attempts=obs_data.get("max_attempts", 3),
            done=obs_data.get("done", False),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> DebugState:
        """
        Parse server response into DebugState object.
        
        Args:
            payload: JSON response from state request
        
        Returns:
            DebugState object with episode metadata
        """
        return DebugState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            problem_id=payload.get("problem_id"),
            attempt=payload.get("attempt", 0),
            task_id=payload.get("task_id"),
        )


# For convenience - agents can use either class name
DebugEnvClient = PythonDebugEnv
