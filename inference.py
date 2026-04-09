"""
Baseline Inference Script for BugLab
=====================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.

- Defaults are set only for API_BASE_URL and MODEL_NAME 
    (and should reflect your active inference setup):
    API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
    MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
    
- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables

STDOUT FORMAT
- The script must emit exactly three line types to stdout, in this order:

    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> rewards=<r1,r2,...,rn>

  Rules:
    - One [START] line at episode begin.
    - One [STEP] line per step, immediately after env.step() returns.
    - One [END] line after env.close(), always emitted (even on exception).
    - reward and rewards are formatted to 2 decimal places.
    - done and success are lowercase booleans: true or false.
    - error is the raw last_action_error string, or null if none.
    - All fields on a single line with no newlines within a line.
    - Each task should return score in [0, 1]

  Example:
    [START] task=fix_logic_bug env=BugLab model=gpt-4.1-mini
    [STEP] step=1 action=fix_attempt_1 reward=0.30 done=false error=null
    [STEP] step=2 action=fix_attempt_2 reward=0.85 done=true error=null
    [END] success=true steps=2 rewards=0.30,0.85
"""

import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI
from openenv import GenericEnvClient

# Environment variable configuration (MANDATORY)
HF_TOKEN = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-3.5-turbo"
TASK_NAME = os.getenv("EVAL_TASK", "fix_logic_bug")
BENCHMARK = os.getenv("EVAL_BENCHMARK", "BugLab")
ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")
MAX_STEPS = 3
TEMPERATURE = 0.0
MAX_TOKENS = 500
SUCCESS_SCORE_THRESHOLD = 0.7

# Max possible reward calculation
_MAX_REWARD_PER_STEP = 1.0
MAX_TOTAL_REWARD = MAX_STEPS * _MAX_REWARD_PER_STEP

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a Python code debugging expert. Your task is to fix buggy code.
    Analyze the provided buggy code and description carefully.
    Return ONLY the fixed Python code with the same function signature, no explanation.
    """
).strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)


def build_user_prompt(step: int, buggy_code: str, description: str) -> str:
    return textwrap.dedent(
        f"""
        Step: {step}
        Task: {description}
        
        Buggy code:
        {buggy_code}
        
        Provide ONLY the fixed code, no explanation.
        """
    ).strip()


def get_model_message(client: OpenAI, step: int, buggy_code: str, description: str) -> str:
    user_prompt = build_user_prompt(step, buggy_code, description)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "pass"
    except Exception as exc:
        return "pass"


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    env = GenericEnvClient(ENV_URL)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=TASK_NAME)
        obs = result.observation
        buggy_code = obs.get("buggy_code", "")
        description = obs.get("description", "")

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            fixed_code = get_model_message(client, step, buggy_code, description)

            result = await env.step({"fixed_code": fixed_code})
            obs = result.observation

            reward = result.reward or 0.0
            done = result.done
            error = None

            rewards.append(reward)
            steps_taken = step
            buggy_code = obs.get("buggy_code", "")
            description = obs.get("description", "")

            log_step(step=step, action=fixed_code[:50], reward=reward, done=done, error=error)

            history.append(f"Step {step}: reward {reward:+.2f}")

            if done:
                break

        success = sum(rewards) > 0 if rewards else False

    finally:
        try:
            await env.close()
        except Exception as e:
            pass
        log_end(success=success, steps=steps_taken, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
