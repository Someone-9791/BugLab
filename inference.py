"""
Baseline Inference Script for BugLab
=====================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM (injected by validator).
    MODEL_NAME     The model identifier to use for inference.
    API_KEY        Your API key for the LLM proxy (injected by validator).

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
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is required (injected by validator)")

API_BASE_URL = os.environ.get("API_BASE_URL")
if not API_BASE_URL:
    raise ValueError("API_BASE_URL environment variable is required (injected by validator)")

MODEL_NAME = os.environ.get("MODEL_NAME") or "gpt-3.5-turbo"
TASK_NAME = os.environ.get("EVAL_TASK", "fix_logic_bug")
BENCHMARK = os.environ.get("EVAL_BENCHMARK", "BugLab")
ENV_URL = os.environ.get("ENV_URL", "http://localhost:8000")
MAX_STEPS = 3
TEMPERATURE = 0.0
MAX_TOKENS = 500

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
    action_safe = " ".join(action.split())
    print(
        f"[STEP] step={step} action={action_safe} reward={reward:.2f} done={done_val} error={error_val}",
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
    except Exception:
        return "pass"


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    env = GenericEnvClient(ENV_URL)

    rewards: List[float] = []
    steps_taken = 0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=TASK_NAME)
        obs = getattr(result, "observation", {})
        buggy_code = obs.get("buggy_code", "")
        description = obs.get("description", "")

        for step in range(1, MAX_STEPS + 1):
            if getattr(result, "done", False):
                break

            fixed_code = get_model_message(client, step, buggy_code, description)

            result = await env.step({"fixed_code": fixed_code})

            reward = float(getattr(result, "reward", 0.0) or 0.0)
            done = bool(getattr(result, "done", False))
            error = getattr(result, "last_action_error", None)

            rewards.append(reward)
            steps_taken = step

            obs = getattr(result, "observation", {})
            buggy_code = obs.get("buggy_code", "")
            description = obs.get("description", "")

            log_step(step=step, action=fixed_code, reward=reward, done=done, error=error)

            if getattr(result, "success", None) is True:
                success = True
            
            if done:
                break

    except Exception:
        success = False
        raise
    finally:
        try:
            await env.close()
        except Exception:
            pass
        log_end(success=success, steps=steps_taken, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
