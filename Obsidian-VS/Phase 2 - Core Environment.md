# Phase 2: Core Environment Implementation

> **Status:** 🔥 ACTIVE - Top Priority  
> **Target:** Complete by April 4th EOD  
> **Estimated Time:** 6-8 hours

---

## 📋 Task Breakdown

### 1. `server/__init__.py` ⏳
**Purpose:** Package initialization  
**Time:** 5 minutes  
**Content:**
```python
"""
PythonDebugEnv server package.
Contains environment, grader, and FastAPI app.
"""
```

---

### 2. `server/grader.py` ⏳ 🔥 CRITICAL
**Purpose:** Sandboxed test execution + LLM judge + reward computation  
**Time:** 3-4 hours  
**Estimated Lines:** ~200

**Required Functions:**

#### `run_tests_sandboxed(code: str, test_cases: list[dict]) -> float`
- Create temporary Python script with user code + test runner
- Execute in isolated subprocess with 5-second timeout
- Catch: SyntaxError, RuntimeError, TimeoutError
- Return: pass_rate (0.0 to 1.0)
- Clean up temp files

**Key Pattern:**
```python
import subprocess
import json
import tempfile
import os

def run_tests_sandboxed(code: str, test_cases: list) -> float:
    # Build test script
    test_script = f"""
{code}

import json
results = []
test_cases = {json.dumps(test_cases)}

for tc in test_cases:
    try:
        result = solution(*tc['input'])
        results.append(result == tc['expected'])
    except Exception:
        results.append(False)

print(json.dumps(results))
"""
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            tmp_path = f.name
        
        proc = subprocess.run(
            ['python3', tmp_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if proc.returncode != 0:
            return 0.0
        
        results = json.loads(proc.stdout.strip())
        return sum(results) / len(results) if results else 0.0
    
    except subprocess.TimeoutExpired:
        return 0.0
    except Exception:
        return 0.0
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

#### `call_llm_judge(buggy_code: str, fixed_code: str) -> float`
- Call HF Inference API
- Model: `Qwen/Qwen2.5-Coder-7B-Instruct`
- Use structured prompt template
- Parse JSON response: `{"score": 0.85, "reason": "..."}`
- Return: quality_score (0.0 to 1.0)
- Fallback: Return 0.5 on ANY error

**Key Pattern:**
```python
import requests
import json
import os

HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-7B-Instruct"

JUDGE_PROMPT = """You are a code quality judge. A student fixed broken Python code.

Original broken code:
```python
{buggy_code}
```

Student's fix:
```python
{fixed_code}
```

Rate the fix from 0.0 to 1.0 based on:
- Correctness (does it fix the bug?)
- Code quality (clean and readable?)
- Approach (minimal and appropriate?)

Respond ONLY with JSON: {{"score": 0.85, "reason": "brief explanation"}}
"""

def call_llm_judge(buggy_code: str, fixed_code: str) -> float:
    try:
        prompt = JUDGE_PROMPT.format(buggy_code=buggy_code, fixed_code=fixed_code)
        
        response = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return 0.5
        
        output = response.json()[0]["generated_text"]
        
        # Parse JSON
        start = output.find('{')
        end = output.rfind('}') + 1
        if start == -1 or end == 0:
            return 0.5
        
        data = json.loads(output[start:end])
        score = float(data.get("score", 0.5))
        return max(0.0, min(1.0, score))  # clamp [0, 1]
    
    except Exception:
        return 0.5  # never crash
```

#### `compute_reward(test_score: float, llm_score: float) -> float`
- Simple weighted sum
- Formula: `0.6 * test_score + 0.4 * llm_score`

**Key Pattern:**
```python
def compute_reward(test_score: float, llm_score: float) -> float:
    """Compute final reward from dual signals."""
    return 0.6 * test_score + 0.4 * llm_score
```

---

### 3. `server/environment.py` ⏳ 🔥 CRITICAL
**Purpose:** OpenEnv Environment subclass  
**Time:** 2-3 hours  
**Estimated Lines:** ~120

**Required Methods:**

#### `__init__(self)`
- Load PROBLEMS from bug_bank
- Initialize state: current_problem, episode_id, step_count

#### `reset(self) -> DebugObservation`
- Select random problem from PROBLEMS
- Generate new episode_id
- Reset step_count to 0
- Return DebugObservation with problem details

#### `step(self, action: DebugAction) -> StepResult`
- Increment step_count
- Call grader functions:
  - test_score = run_tests_sandboxed(action.fixed_code, test_cases)
  - llm_score = call_llm_judge(buggy_code, action.fixed_code)
  - reward = compute_reward(test_score, llm_score)
- Set done = True (single-turn environment)
- Return StepResult with reward and info dict

#### `state(self) -> DebugState`
- Return current episode metadata

**Key Pattern:**
```python
from openenv.core.environment import Environment
from openenv.core.models import StepResult
from models import DebugAction, DebugObservation, DebugState
from server.grader import run_tests_sandboxed, call_llm_judge, compute_reward
from bug_bank import PROBLEMS
import random

class PythonDebugEnvironment(Environment):
    
    def __init__(self):
        self.problems = PROBLEMS
        self.current_problem = None
        self.episode_id = None
        self.step_count = 0
    
    def reset(self) -> DebugObservation:
        self.current_problem = random.choice(self.problems)
        self.step_count = 0
        self.episode_id = f"ep_{random.randint(10000, 99999)}"
        
        return DebugObservation(
            problem_id=self.current_problem["id"],
            buggy_code=self.current_problem["buggy_code"],
            description=self.current_problem["description"],
            test_cases=self.current_problem["test_cases"],
            difficulty=self.current_problem["difficulty"]
        )
    
    def step(self, action: DebugAction) -> StepResult:
        self.step_count += 1
        problem = self.current_problem
        
        # Dual reward
        test_score = run_tests_sandboxed(action.fixed_code, problem["test_cases"])
        llm_score = call_llm_judge(problem["buggy_code"], action.fixed_code)
        reward = compute_reward(test_score, llm_score)
        
        done = True
        next_obs = DebugObservation(
            problem_id="done",
            buggy_code="",
            description="Episode complete",
            test_cases=[],
            difficulty="easy"
        )
        
        return StepResult(
            observation=next_obs,
            reward=reward,
            done=done,
            info={
                "test_score": test_score,
                "llm_score": llm_score,
                "passed_tests": int(test_score * len(problem["test_cases"])),
                "total_tests": len(problem["test_cases"]),
                "problem_id": problem["id"],
                "difficulty": problem["difficulty"]
            }
        )
    
    def state(self) -> DebugState:
        return DebugState(
            episode_id=self.episode_id,
            step_count=self.step_count,
            current_problem_id=self.current_problem["id"] if self.current_problem else None
        )
```

---

### 4. `server/app.py` ⏳
**Purpose:** FastAPI application factory  
**Time:** 30 minutes  
**Estimated Lines:** ~30

**Key Pattern:**
```python
from fastapi import FastAPI
from openenv.core.server import create_app
from server.environment import PythonDebugEnvironment

app = create_app(PythonDebugEnvironment)
```

---

### 5. `client.py` ⏳
**Purpose:** Client for connecting to environment  
**Time:** 30 minutes  
**Estimated Lines:** ~40

**Key Pattern:**
```python
from openenv.core.client import EnvClient
from models import DebugAction, DebugObservation, DebugState

class PythonDebugEnv(EnvClient):
    """Client for PythonDebugEnv."""
    
    action_type = DebugAction
    observation_type = DebugObservation
    state_type = DebugState

# Usage example
if __name__ == "__main__":
    with PythonDebugEnv(base_url="http://localhost:8000").sync() as env:
        obs = env.reset()
        print(f"Problem: {obs.description}")
        print(f"Buggy code:\n{obs.buggy_code}")
        
        # Submit fix
        result = env.step(DebugAction(fixed_code=obs.buggy_code))
        print(f"Reward: {result.reward}")
        print(f"Info: {result.info}")
```

---

### 6. Local Testing ⏳
**Purpose:** Validate everything works before Docker  
**Time:** 1 hour

**Test Commands:**
```bash
# Activate venv
source ~/ml/bin/activate

# Navigate to project
cd /home/someone/python_debug_env

# Run server
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload

# In another terminal: test client
python3 client.py
```

**Test Scenarios:**
1. Reset returns valid observation
2. Step with correct fix → high reward
3. Step with buggy code → low reward
4. LLM judge fallback works (disconnect internet)
5. Timeout handling (infinite loop code)

---

## ✅ Success Criteria

- [ ] All 5 files created and error-free
- [ ] Server starts without errors
- [ ] Client can connect and reset
- [ ] Sandboxed execution works (test with infinite loop)
- [ ] LLM judge returns scores (0.0-1.0)
- [ ] Reward formula produces expected values
- [ ] No crashes on malformed code
- [ ] State tracking accurate

---

## 🚨 Common Pitfalls

1. **Import paths** - Use `from server.grader import ...`, not relative imports
2. **Temp file cleanup** - Always use `finally:` block
3. **Timeout handling** - Must catch `subprocess.TimeoutExpired`
4. **LLM errors** - Never let API failures crash environment
5. **JSON parsing** - LLM output may not be perfect JSON

---

*Back to [[PythonDebugEnv Project Hub]]*
