# Phase 2.5: Inference Script & Validation

> **Status:** 🔥 NEW REQUIREMENT - High Priority  
> **Target:** Complete immediately after Phase 2  
> **Estimated Time:** 3-4 hours

---

## 🎯 Purpose

Create the baseline inference script that:
1. Connects to our environment using OpenAI client
2. Runs an LLM agent against tasks at different difficulties
3. Emits structured logs for automated evaluation
4. Produces reproducible baseline scores

---

## 📋 Requirements

### File: `inference.py` (root directory)

**Must:**
- Use OpenAI Client for all LLM calls
- Read env vars: API_BASE_URL, MODEL_NAME, HF_TOKEN
- Test against easy, medium, and hard tasks
- Complete in < 20 minutes
- Work on 2 vCPU, 8GB RAM
- Emit structured stdout logs

---

## 📝 Structured Logging Format

**CRITICAL:** Must follow this format exactly:

```
[START] task=<task_name> env=<benchmark> model=<model_name>
[STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
[END]   success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
```

**Rules:**
- One [START] line at episode begin
- One [STEP] line per step (immediately after env.step())
- One [END] line after env.close() (always, even on exception)
- reward and rewards formatted to 2 decimal places
- done/success are lowercase booleans: `true` or `false`
- error is raw error string or `null`
- All fields on single line, no newlines within a line

**Example:**
```
[START] task=logic_001 env=python-debug-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=fix_code reward=0.92 done=true error=null
[END] success=true steps=1 rewards=0.92
```

---

## 🔧 Implementation Pattern

```python
"""
Baseline Inference Script for PythonDebugEnv
=============================================
Tests the environment against easy, medium, and hard debugging tasks.
"""

import asyncio
import os
import sys
from typing import Optional

from openai import OpenAI
from client import PythonDebugEnv
from models import DebugAction

# Environment variables (with defaults for local testing)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")
BENCHMARK = "python-debug-env"

# Test configuration
TASKS_TO_TEST = [
    "logic_001",    # Easy
    "off_by_one_003",  # Medium
    "recursion_002",   # Hard
]
MAX_STEPS = 5  # Allow multiple attempts per problem
TEMPERATURE = 0.7
MAX_TOKENS = 500

def log_start(task: str, model: str, env: str):
    """Emit [START] log."""
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None):
    """Emit [STEP] log."""
    done_str = "true" if done else "false"
    error_str = error if error else "null"
    # Truncate action if too long
    action_display = action[:100] + "..." if len(action) > 100 else action
    print(f"[STEP] step={step} action={action_display} reward={reward:.2f} done={done_str} error={error_str}", flush=True)

def log_end(success: bool, steps: int, rewards: list[float]):
    """Emit [END] log."""
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

Provide ONLY the fixed Python code, no explanation. Keep the function signature the same.
"""

def run_episode(client: OpenAI, env: PythonDebugEnv, task_id: str) -> tuple[bool, int, list[float]]:
    """
    Run one episode against a specific task.
    
    Returns:
        (success, steps, rewards)
    """
    rewards = []
    step_count = 0
    
    try:
        # Reset environment (we'll need to modify environment to support task selection)
        obs = env.reset()
        
        # For now, we get random problems - in production we'd select by task_id
        # This is a limitation we'll note in the implementation
        
        for attempt in range(MAX_STEPS):
            step_count += 1
            
            # Get LLM to generate fix
            prompt = create_prompt(obs.buggy_code, obs.description)
            
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
                action = DebugAction(fixed_code=fixed_code)
                result = env.step(action)
                
                rewards.append(result.reward)
                log_step(step_count, f"fix_attempt_{attempt+1}", result.reward, result.done)
                
                if result.done:
                    # Episode complete
                    success = result.reward >= 0.7  # Threshold for success
                    return success, step_count, rewards
                
                # Get next observation for retry
                obs = result.observation
                
            except Exception as e:
                log_step(step_count, f"fix_attempt_{attempt+1}", 0.0, False, str(e))
                rewards.append(0.0)
        
        # Max steps reached
        return False, step_count, rewards
        
    except Exception as e:
        print(f"Episode error: {e}", file=sys.stderr)
        if not rewards:
            rewards = [0.0]
        return False, step_count if step_count > 0 else 1, rewards

def main():
    """Run baseline inference across multiple tasks."""
    if not API_KEY:
        print("ERROR: HF_TOKEN or API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    # Initialize OpenAI client
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )
    
    # Test each task
    total_tasks = len(TASKS_TO_TEST)
    successful_tasks = 0
    
    for task_id in TASKS_TO_TEST:
        log_start(task_id, MODEL_NAME, BENCHMARK)
        
        try:
            # Connect to environment
            with PythonDebugEnv(base_url=ENV_URL).sync() as env:
                success, steps, rewards = run_episode(client, env, task_id)
                
                if success:
                    successful_tasks += 1
                
                log_end(success, steps, rewards)
                
        except Exception as e:
            print(f"Task {task_id} failed: {e}", file=sys.stderr)
            log_end(False, 1, [0.0])
    
    # Summary
    success_rate = successful_tasks / total_tasks
    print(f"\n=== Baseline Results ===", file=sys.stderr)
    print(f"Tasks tested: {total_tasks}", file=sys.stderr)
    print(f"Tasks successful: {successful_tasks}", file=sys.stderr)
    print(f"Success rate: {success_rate:.2%}", file=sys.stderr)

if __name__ == "__main__":
    main()
```

---

## ⚙️ Environment Variables Update

**Update `/home/someone/python_debug_env/.env`:**

```bash
# Existing
HF_TOKEN=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
LLM_JUDGE_MODE=api
LOCAL_LLM_URL=http://localhost:8080

# NEW - Required for inference.py
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
ENV_URL=http://localhost:8000
```

---

## 🧪 Testing

**Local test:**
```bash
# Terminal 1: Start environment
source ~/ml/bin/activate
cd /home/someone/python_debug_env
uvicorn server.app:app --host 0.0.0.0 --port 8000

# Terminal 2: Run inference
source ~/ml/bin/activate
cd /home/someone/python_debug_env
python3 inference.py
```

**Expected output:**
```
[START] task=logic_001 env=python-debug-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=fix_attempt_1 reward=0.92 done=true error=null
[END] success=true steps=1 rewards=0.92
[START] task=off_by_one_003 env=python-debug-env model=Qwen/Qwen2.5-72B-Instruct
...
```

---

## ✅ Success Criteria

- [ ] inference.py created in root directory
- [ ] Uses OpenAI client (not direct API calls)
- [ ] Reads all required env vars
- [ ] Tests easy, medium, hard tasks
- [ ] Emits correct [START], [STEP], [END] format
- [ ] Handles errors gracefully (always emits [END])
- [ ] Completes in < 20 minutes
- [ ] Produces reproducible scores

---

## ⚠️ Known Limitation

**Task Selection:** Our current environment design gives random problems. We may need to:
1. Add a `task_id` parameter to `reset(task_id=None)`
2. Or accept that baseline tests random problems (document this)

**Recommendation:** Keep simple for now, document limitation. Judges likely understand this.

---

*Back to [[PythonDebugEnv Project Hub]]*
