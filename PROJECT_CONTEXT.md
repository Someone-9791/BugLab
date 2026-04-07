# PROJECT CONTEXT — PythonDebugEnv (Meta x Scaler PyTorch Hackathon 2026)

> **This file is the single source of truth for this project.**
> Read this entirely before writing a single line of code.
> When in doubt, refer back here.

---

## 1. THE HACKATHON

**Name:** Meta PyTorch OpenEnv Hackathon x Scaler School of Technology
**URL:** https://www.scaler.com/school-of-technology/meta-pytorch-hackathon
**Sponsors:** Meta PyTorch, Hugging Face, Scaler School of Technology

### Timeline
| Event | Date |
|---|---|
| Round 1 Starts | 25th March 2026 |
| **Round 1 Deadline** | **8th April 2026 — THIS IS THE HARD DEADLINE** |
| Results Announced | 10th April 2026 |
| Advanced Bootcamp | 18–19 April 2026 |
| Grand Finale (Bangalore) | 25–26 April 2026 |

### What Round 1 Requires
Build a **Mini-RL Environment** using the OpenEnv framework with:
- Defined tasks with clear inputs and outputs
- A grader/reward function with programmatic checks
- An LLM scoring component (LLM-as-judge)
- Deployed to HuggingFace Spaces via `openenv push`

### Judging Criteria
- Quality and originality of the environment
- Reward function design (dual signals score higher)
- Code quality and documentation
- Deployment to HF Spaces

### Prize
- $30,000 prize pool
- Winners get direct interview opportunity at Meta and Hugging Face AI teams
- Code ships as open source contribution to a Meta-backed project

---

## 2. THE FRAMEWORK — OpenEnv

**GitHub:** https://github.com/meta-pytorch/OpenEnv
**Course:** https://github.com/huggingface/openenv-course
**Docs:** https://meta-pytorch.org/OpenEnv/

OpenEnv is an open-source framework by Meta and Hugging Face for creating standardized, isolated, reusable environments for training and evaluating AI agents. Think of it as Gymnasium but for LLM agents.

### Core API (3 methods, that's it)
```python
env.reset()   # Initialize episode, return initial Observation
env.step()    # Accept Action, return StepResult (Observation + reward + done)
env.state()   # Return episode metadata (step count, episode_id, etc.)
```

### Architecture
```
Client (LLM Agent)
    │ WebSocket
    ▼
FastAPI Server (Docker container)
    ├── Environment class (your logic)
    ├── Grader (reward computation)
    └── HF Spaces deployment
```

### Install
```bash
pip install openenv-core
openenv init my_env_name   # scaffold a new environment
openenv push               # deploy to HuggingFace Spaces
```

### Scaffold Structure (from `openenv init`)
```
my_env/
├── models.py              # Pydantic Action + Observation types
├── client.py              # EnvClient subclass
├── openenv.yaml           # Environment manifest
├── pyproject.toml         # Dependencies
├── README.md
└── server/
    ├── environment.py     # Environment subclass (core logic)
    ├── grader.py          # Reward computation
    ├── app.py             # FastAPI app factory
    └── Dockerfile
```

---

## 3. THE PROJECT — PythonDebugEnv

### Concept
An RL environment where an LLM agent receives **broken Python code** and must return a **corrected version**. The environment evaluates the fix using two independent reward signals.

### Why This Is a Strong Submission
1. **Dual reward signals** — exactly what judges want to see
2. **Coding domain** — directly relevant to Meta/HF's interests in code LLMs
3. **GPU utilization** — local LLM judge runs on our RX 9060 XT
4. **Novel dataset** — we generate our own bug bank, not a recycled benchmark

### Environment Flow
```
1. Agent calls env.reset()
   └── Returns: DebugObservation(
           problem_id="bug_042",
           buggy_code="def add(a, b):\n    return a - b",
           description="This function should add two numbers",
           test_cases=[{"input": [2,3], "expected": 5}],
           difficulty="easy"
       )

2. Agent analyzes code, generates fix

3. Agent calls env.step(DebugAction(fixed_code="def add(a,b):\n    return a+b"))
   └── Returns: StepResult(
           observation=DebugObservation(...next problem...),
           reward=0.92,
           done=False,
           info={"test_score": 1.0, "llm_score": 0.8, "passed_tests": 3, "total_tests": 3}
       )
```

### Reward Formula
```python
final_reward = 0.6 * test_pass_rate + 0.4 * llm_quality_score
```

- **test_pass_rate** (0.0–1.0): Deterministic. Run fixed code against hidden test cases in a sandboxed subprocess with timeout. Fast and objective.
- **llm_quality_score** (0.0–1.0): LLM-as-judge. Local Qwen2.5-Coder model scores code quality, style, and correctness beyond just passing tests.

### Bug Categories (build at least 30 problems across these)
| Category | Example |
|---|---|
| Logic errors | `>` instead of `>=`, wrong operator |
| Off-by-one | `range(n)` instead of `range(n+1)` |
| Wrong return | Returns wrong variable |
| Missing edge case | No null check |
| Type errors | String + int without conversion |
| Recursion base case | Missing base case in recursive function |
| Loop errors | Infinite loop, wrong loop variable |
| Variable shadowing | Variable name conflict |

---

## 4. THE HARDWARE & SYSTEM

### Machine
- **CPU:** AMD Ryzen 5600X (6 cores, 12 threads)
- **RAM:** 8GB DDR4 3200MHz dual channel (BOTTLENECK — keep this in mind)
- **GPU:** AMD Radeon RX 9060 XT — 16GB VRAM (gfx1200/RDNA4)
- **Motherboard:** MSI X570 Unify
- **Storage:** 128GB SSD (Linux), 500GB HDD (storage), 124GB exFAT

### Software Stack
```
Ubuntu 24.04.4 LTS
└── Kernel 6.17.0-20-generic (HWE — critical for RDNA4)
    └── ROCm 7.2.1 (installed at /opt/rocm-7.2.1)
        └── Python 3.12.3 venv at ~/ml
            ├── PyTorch 2.9.1+rocm7.2.1
            ├── transformers 5.4.0
            ├── openenv 0.2.3
            ├── fastapi + uvicorn
            ├── huggingface_hub
            └── numpy 1.26.4 (pinned — v2.0 breaks ROCm torch wheels)
```

### Critical Notes for This Machine
- **8GB RAM means no full-precision 7B models** — must use quantized (Q4_K_M) via llama.cpp
- **PyTorch venv must always be activated:** `source ~/ml/bin/activate`
- **ROCm uses CUDA-compatible API** — `torch.cuda.is_available()` returns True on ROCm
- **GPU verified working:** `torch.cuda.get_device_name(0)` → "AMD Radeon RX 9060 XT"
- **VRAM reported:** 17.1GB (ROCm reports slightly more than rated)
- **numpy must stay at 1.26.4** — do not upgrade

### LLM Judge Strategy (RAM-constrained)
**Primary:** HuggingFace Inference API (free tier) — `Qwen/Qwen2.5-Coder-7B-Instruct`
- Zero RAM overhead, runs on HF servers
- Requires HF_TOKEN in .env file
- Rate limited but sufficient for hackathon

**Secondary (local):** llama.cpp with ROCm backend + Q4_K_M quantized model
- Build llama.cpp with `-DCMAKE_HIP_ARCHITECTURES=gfx1201`
- Run `qwen2.5-coder-7b-instruct-q4_k_m.gguf` (~4.5GB, fits in VRAM)
- Exposes OpenAI-compatible API at `http://localhost:8080`
- ~92 tokens/sec on this GPU

---

## 5. FILE STRUCTURE TO BUILD

```
~/python_debug_env/
├── .env                        # HF_TOKEN=hf_... (never commit this)
├── .gitignore
├── README.md                   # Judges read this — make it good
├── openenv.yaml                # Environment manifest
├── pyproject.toml
│
├── models.py                   # START HERE
│   ├── DebugAction(BaseModel)
│   │   └── fixed_code: str
│   ├── DebugObservation(BaseModel)
│   │   ├── problem_id: str
│   │   ├── buggy_code: str
│   │   ├── description: str
│   │   ├── test_cases: list[dict]
│   │   └── difficulty: Literal["easy", "medium", "hard"]
│   └── DebugState(BaseModel)
│
├── client.py                   # PythonDebugEnv(EnvClient)
│
└── server/
    ├── environment.py          # PythonDebugEnvironment(Environment)
    │   ├── reset() → DebugObservation
    │   ├── step(action) → StepResult
    │   └── state() → DebugState
    │
    ├── grader.py               # CORE LOGIC
    │   ├── run_tests_sandboxed(code, tests) → float
    │   │   ├── subprocess with 5s timeout
    │   │   ├── catches SyntaxError, RuntimeError, TimeoutError
    │   │   └── returns pass_rate 0.0–1.0
    │   ├── call_llm_judge(buggy, fixed) → float
    │   │   ├── calls HF Inference API or local llama.cpp
    │   │   └── returns quality_score 0.0–1.0
    │   └── compute_reward(test_score, llm_score) → float
    │       └── 0.6 * test_score + 0.4 * llm_score
    │
    ├── bug_bank.py             # Dataset of problems
    │   └── PROBLEMS: list[dict] — at least 30 problems
    │
    ├── app.py                  # FastAPI app factory
    └── Dockerfile
```

---

## 6. DEVELOPMENT PLAN

### Phase 1 — Models & Data (Do First)
- [ ] Write `models.py` — all Pydantic models
- [ ] Write `bug_bank.py` — 30+ bug problems across all categories
- [ ] Each problem needs: id, description, buggy_code, fixed_code, test_cases, difficulty

### Phase 2 — Core Environment
- [ ] Write `server/grader.py` — sandboxed test runner first
- [ ] Write `server/environment.py` — reset/step/state
- [ ] Write `server/app.py` — FastAPI wiring
- [ ] Write `client.py` — EnvClient subclass

### Phase 3 — LLM Judge
- [ ] Implement HF Inference API judge (primary path)
- [ ] Write judge prompt template
- [ ] Parse JSON score from LLM response
- [ ] Add fallback: if API fails → return 0.5 (neutral score)

### Phase 4 — Docker & Testing
- [ ] Write `Dockerfile`
- [ ] Build and test locally: `docker build -t python-debug-env .`
- [ ] Run: `docker run -p 8000:8000 python-debug-env`
- [ ] Test with client against local container

### Phase 5 — Deploy & Polish
- [ ] `huggingface-cli login`
- [ ] `openenv push --repo-id USERNAME/python-debug-env`
- [ ] Write README.md (judges read this — explain reward design clearly)
- [ ] Add example agent interaction in README

---

## 7. KEY CODE PATTERNS

### Sandboxed Code Execution (critical — never use eval/exec directly)
```python
import subprocess
import json
import tempfile
import os

def run_tests_sandboxed(code: str, test_cases: list) -> float:
    """Run code against test cases in isolated subprocess with timeout."""
    
    test_script = f"""
{code}

import json
results = []
test_cases = {json.dumps(test_cases)}

for tc in test_cases:
    try:
        result = solution(*tc['input'])
        results.append(result == tc['expected'])
    except Exception as e:
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
            timeout=5  # 5 second hard timeout
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

### HF Inference API Judge
```python
import requests
import json
import os

HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-7B-Instruct"

JUDGE_PROMPT = """You are a code quality judge. A student was given broken Python code and asked to fix it.

Original broken code:
```python
{buggy_code}
```

Student's fix:
```python
{fixed_code}
```

Rate the fix on a scale from 0.0 to 1.0 based on:
- Correctness (does it actually fix the bug?)
- Code quality (is it clean and readable?)
- Approach (is the fix minimal and appropriate?)

Respond ONLY with a JSON object like this: {{"score": 0.85, "reason": "brief explanation"}}
"""

def call_llm_judge(buggy_code: str, fixed_code: str) -> float:
    """Call HF Inference API to score code quality. Returns 0.5 on any failure."""
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
            return 0.5  # neutral fallback
            
        output = response.json()[0]["generated_text"]
        
        # Parse JSON from response
        start = output.find('{')
        end = output.rfind('}') + 1
        if start == -1 or end == 0:
            return 0.5
            
        data = json.loads(output[start:end])
        score = float(data.get("score", 0.5))
        return max(0.0, min(1.0, score))  # clamp to [0, 1]
        
    except Exception:
        return 0.5  # always return something, never crash the environment
```

### Environment Class Pattern
```python
from openenv.core.environment import Environment
from openenv.core.models import StepResult
from .models import DebugAction, DebugObservation, DebugState
from .grader import run_tests_sandboxed, call_llm_judge
from .bug_bank import PROBLEMS
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
        
        # Compute dual reward
        test_score = run_tests_sandboxed(action.fixed_code, problem["test_cases"])
        llm_score = call_llm_judge(problem["buggy_code"], action.fixed_code)
        reward = 0.6 * test_score + 0.4 * llm_score
        
        # Episode ends after 1 step (single-turn environment)
        done = True
        next_obs = self.reset() if not done else DebugObservation(
            problem_id="done", buggy_code="", description="Episode complete",
            test_cases=[], difficulty="easy"
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

## 8. ENVIRONMENT VARIABLES

Create `~/python_debug_env/.env`:
```
HF_TOKEN=hf_your_token_here
LLM_JUDGE_MODE=api          # "api" for HF API, "local" for llama.cpp
LOCAL_LLM_URL=http://localhost:8080  # only used if LLM_JUDGE_MODE=local
```

---

## 9. COMMANDS REFERENCE

```bash
# Activate environment (always do this first)
source ~/ml/bin/activate

# Navigate to project
cd ~/python_debug_env

# Run server locally (without Docker)
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload

# Build Docker image
docker build -t python-debug-env .

# Run Docker container
docker run -p 8000:8000 --env-file .env python-debug-env

# Test client against local server
python3 -c "
from client import PythonDebugEnv, DebugAction
with PythonDebugEnv(base_url='http://localhost:8000').sync() as env:
    obs = env.reset()
    print('Problem:', obs.description)
    print('Buggy code:', obs.buggy_code)
    result = env.step(DebugAction(fixed_code=obs.buggy_code))
    print('Reward:', result.reward)
"

# Deploy to HuggingFace Spaces
huggingface-cli login
openenv push --repo-id YOUR_USERNAME/python-debug-env

# Verify GPU in PyTorch
python3 -c "import torch; print(torch.cuda.get_device_name(0))"

# Check ROCm GPU status
rocm-smi
```

---

## 10. IMPORTANT CONSTRAINTS & GOTCHAS

1. **Never use `eval()` or `exec()` directly** on agent-submitted code — always use subprocess
2. **Always timeout subprocesses** — agents can submit infinite loops
3. **LLM judge must never crash the environment** — wrap in try/except, return 0.5 on failure
4. **numpy must stay at 1.26.4** — numpy 2.0 breaks ROCm PyTorch wheels
5. **Always activate venv** before running anything: `source ~/ml/bin/activate`
6. **ROCm path:** `/opt/rocm-7.2.1` — symlinked to `/opt/rocm`
7. **HF_TOKEN must be in .env** — never hardcode tokens in source code
8. **8GB RAM limit** — do not attempt to load any model > 3B parameters in fp16 directly in Python; use llama.cpp server instead
9. **Docker must expose port 8000** — OpenEnv standard port
10. **openenv.yaml must be correct** — judges use this to understand your environment

---

## 11. DEADLINE CHECKLIST

Before April 8th, the following must be complete and working:

- [ ] `models.py` — DebugAction, DebugObservation, DebugState
- [ ] `bug_bank.py` — minimum 30 problems, all categories covered
- [ ] `server/grader.py` — sandboxed runner + LLM judge + reward formula
- [ ] `server/environment.py` — reset/step/state all working
- [ ] `server/app.py` — FastAPI app running
- [ ] `client.py` — client working against local server
- [ ] `Dockerfile` — builds and runs cleanly
- [ ] `openenv.yaml` — correctly describes the environment
- [ ] `README.md` — explains the environment, reward design, and usage
- [ ] Deployed to HuggingFace Spaces via `openenv push`
- [ ] HF Space is public and accessible

---

## 12. DEVELOPMENT LOG

### 2026-04-02 17:04 — Phase 1 Complete: Models & Data ✅

**Created Project Structure:**
```
/home/someone/python_debug_env/
├── .env                    ✅ HF token configured
├── .gitignore              ✅ Python/Docker/IDE patterns
├── models.py               ✅ DebugAction, DebugObservation, DebugState
├── bug_bank.py             ✅ 30 problems across 8 categories
├── openenv.yaml            ✅ Environment manifest
├── pyproject.toml          ✅ Dependencies defined
├── README.md               ✅ Comprehensive documentation
└── server/                 ⏳ (empty, ready for Phase 2)
```

**Bug Bank Statistics:**
- **Total Problems:** 30
- **Categories:** 8 (logic_error, off_by_one, wrong_return, missing_edge_case, type_error, recursion_error, loop_error, variable_shadowing)
- **Difficulty Distribution:** 9 easy, 15 medium, 6 hard
- **Test Coverage:** 3+ test cases per problem (90 total test cases)
- **All assertions passed:** ✅

**Files Status:**
- `models.py` — Fully validated Pydantic models with type hints
- `bug_bank.py` — Validated import, all problems have required fields
- `.env` — HF_TOKEN configured, LLM_JUDGE_MODE=api
- `README.md` — 6.4KB, includes architecture, usage examples, deployment guide
- `openenv.yaml` — Environment manifest with proper entry points

**Next Steps:**
- Phase 2: Core Environment (environment.py, grader.py, app.py, client.py)
- Phase 3: LLM Judge implementation
- Phase 4: Docker & Testing
- Phase 5: Deploy & Polish

**Time Remaining:** 5 days, 19 hours until April 8, 2026 deadline

---

*Last updated: April 2, 2026*
*System: Ubuntu 24.04.4 LTS | ROCm 7.2.1 | Python 3.12.3 | PyTorch 2.9.1*
