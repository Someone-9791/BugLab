"""
Baseline Inference Script for BugLab
====================================
Tests the environment against easy, medium, and hard debugging tasks.

MANDATORY REQUIREMENTS:
- Uses OpenAI Client for all LLM calls
- Reads from env vars: API_BASE_URL, MODEL_NAME, HF_TOKEN
- Emits structured logs: [START], [STEP], [END]
- Completes in < 20 minutes
- Works on 2 vCPU, 8GB RAM
"""

import asyncio
import os
import sys
import random
import numpy as np
from typing import Optional

from openai import OpenAI
from openenv import GenericEnvClient

# Set seeds for deterministic behavior (reproducible baselines)
random.seed(42)
np.random.seed(42)

# Environment variables (with defaults for local testing)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("API_KEY")
ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")
BENCHMARK = "BugLab"

# Test configuration - select specific problems by difficulty
# Note: Our environment gives random problems, so we test multiple episodes
EPISODES_PER_DIFFICULTY = {
    "easy": 2,    # Test 2 easy episodes
    "medium": 2,  # Test 2 medium episodes  
    "hard": 1,    # Test 1 hard episode
}
MAX_STEPS_PER_EPISODE = 3  # Allow up to 3 attempts per problem (multi-step environment)
TEMPERATURE = 0.0  # Deterministic (changed from 0.7 for reproducibility)
MAX_TOKENS = 500
SUCCESS_THRESHOLD = 0.7  # Reward >= 0.7 counts as success


def log_start(task: str, model: str, env: str):
    """Emit [START] log."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None):
    """Emit [STEP] log - formatted exactly as required."""
    done_str = "true" if done else "false"
    error_str = error if error else "null"
    # Truncate action if too long for readability
    action_display = action[:80].replace('\n', '\\n') + "..." if len(action) > 80 else action.replace('\n', '\\n')
    print(f"[STEP] step={step} action={action_display} reward={reward:.2f} done={done_str} error={error_str}", flush=True)


def log_end(success: bool, steps: int, rewards: list[float]):
    """Emit [END] log - formatted exactly as required."""
    success_str = "true" if success else "false"
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={success_str} steps={steps} rewards={rewards_str}", flush=True)


def create_prompt(buggy_code: str, description: str) -> str:
    """Create prompt for LLM to fix the code."""
    return f"""You are a Python debugging expert. Fix the following buggy code.

Task: {description}

Buggy code:
```python
{buggy_code}
```

Provide ONLY the fixed Python code with the same function signature, no explanation or markdown formatting.
Return just the corrected code."""


async def run_episode(client: OpenAI, env_url: str, task_id: str) -> tuple[bool, int, list[float]]:
    """
    Run one episode against the environment.
    
    Args:
        client: OpenAI client for LLM calls
        env_url: Environment URL
        task_id: Task identifier (fix_logic_bug, fix_algorithm_bug, optimize_and_fix)
    
    Returns:
        (success, steps, rewards)
    """
    rewards = []
    step_count = 0
    
    try:
        # Connect to environment
        env = GenericEnvClient(base_url=env_url)
        await env.connect()
        
        # Reset environment with explicit task_id to test specific task
        result = await env.reset(task_id=task_id)
        obs = result.observation
        
        # Our environment gives random problems, so we use the actual problem_id
        actual_task = obs.get("problem_id")
        
        # Multi-step loop: attempt up to MAX_STEPS_PER_EPISODE times
        done = False
        while step_count < MAX_STEPS_PER_EPISODE and not done:
            step_count += 1
            
            # Get LLM to generate fix
            prompt = create_prompt(obs.get("buggy_code"), obs.get("description"))
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
                
                fixed_code = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if "```python" in fixed_code:
                    fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
                elif "```" in fixed_code:
                    fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
                
                # Submit action
                result = await env.step({"fixed_code": fixed_code})
                obs = result.observation
                
                reward = obs.get("reward", 0.0)
                done = obs.get("done", False)
                rewards.append(reward)
                
                # Log the step
                log_step(step_count, f"fix_attempt_{step_count}", reward, done, None)
                
                # Check success (done=true means episode ended, could be due to excellent score)
                if done:
                    success = reward >= SUCCESS_THRESHOLD
                    await env.close()
                    return success, step_count, rewards
                
            except Exception as e:
                error_msg = str(e)[:100]  # Truncate long errors
                log_step(step_count, f"fix_attempt_{step_count}", 0.0, False, error_msg)
                rewards.append(0.0)
                await env.close()
                return False, step_count, rewards
        
        # If we exit loop without done=true, episode still ended (max steps reached)
        await env.close()
        success = max(rewards) >= SUCCESS_THRESHOLD if rewards else False
        return success, step_count, rewards
        
    except Exception as e:
        print(f"Episode error: {e}", file=sys.stderr)
        if not rewards:
            rewards = [0.0]
        return False, step_count if step_count > 0 else 1, rewards


async def main_async():
    """Run baseline inference across multiple episodes testing all 3 tasks."""
    if not API_KEY:
        print("ERROR: OPENAI_API_KEY, HF_TOKEN, or API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Initialize OpenAI client
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )
    
    # Define explicit tasks to test (maps to TASKS dict in environment.py)
    EXPLICIT_TASKS = [
        ("fix_logic_bug", 2),      # fix_logic_bug: 2 episodes (easy/medium)
        ("fix_algorithm_bug", 2),  # fix_algorithm_bug: 2 episodes (medium/hard)
        ("optimize_and_fix", 1),   # optimize_and_fix: 1 episode (hard)
    ]
    
    # Calculate total episodes (5 total)
    total_episodes = sum(count for _, count in EXPLICIT_TASKS)
    successful_episodes = 0
    all_rewards = []
    
    # Run episodes for each defined task
    episode_num = 0
    for task_name, count in EXPLICIT_TASKS:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"TASK: {task_name.upper()}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        
        for i in range(count):
            episode_num += 1
            episode_id = f"{task_name}_{i+1}"
            
            log_start(episode_id, MODEL_NAME, BENCHMARK)
            
            try:
                # Explicitly pass task_id to test specific task
                success, steps, rewards = await run_episode(client, ENV_URL, task_name)
                
                if success:
                    successful_episodes += 1
                
                all_rewards.extend(rewards)
                log_end(success, steps, rewards)
                    
            except Exception as e:
                print(f"Task {episode_id} failed: {e}", file=sys.stderr)
                log_end(False, 1, [0.0])
                all_rewards.append(0.0)
    
    # Summary statistics
    success_rate = successful_episodes / total_episodes if total_episodes > 0 else 0.0
    avg_reward = sum(all_rewards) / len(all_rewards) if all_rewards else 0.0
    
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Baseline Inference Results", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Model: {MODEL_NAME}", file=sys.stderr)
    print(f"Episodes tested: {total_episodes}", file=sys.stderr)
    print(f"Episodes successful: {successful_episodes}", file=sys.stderr)
    print(f"Success rate: {success_rate:.1%}", file=sys.stderr)
    print(f"Average reward: {avg_reward:.3f}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)


def main():
    """Entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
