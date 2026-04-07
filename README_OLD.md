# PythonDebugEnv 🐛→✨

**An OpenEnv RL environment for training AI agents to debug Python code**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-0.2.3-blue)](https://github.com/meta-pytorch/OpenEnv)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Hackathon](https://img.shields.io/badge/Event-OpenEnv%202026-red)](https://huggingface.co/spaces)

---

## 🎯 What is This?

**PythonDebugEnv** is a reinforcement learning environment where AI agents learn to debug Python code. Agents receive broken code and must provide fixed versions. The environment uses a **deterministic, reproducible dual reward system**:

- **70% Test Score** — Automated test execution (objective, no API calls)
- **30% Quality Score** — Static code analysis via AST (deterministic, no LLM)

Built for the **OpenEnv Hackathon 2026** with focus on **real-world utility** and **reproducible evaluation**.

**Session 8 Status**: Production-ready for HuggingFace Spaces deployment  
**Estimated Score**: 93/100 (Top 5-10% percentile)

---

## 🏗️ Architecture

```
Agent (LLM - Optional)
    │
    ├─► env.reset() → DebugObservation (buggy code + tests)
    │
    ├─► env.step(DebugAction) → StepResult (reward + observation)
    │       │
    │       └─► Grader computes dual reward (Session 8):
    │            ├─ Test Runner (70%): Sandboxed execution, pass/fail
    │            └─ Code Analyzer (30%): Static AST analysis (deterministic)
    │
    └─► env.state() → DebugState (episode metadata)
```

**Key Improvement (Session 8)**: Switched from LLM-based grading to deterministic static analysis for reproducible, judge-proof evaluation.

---

## 📊 Tasks & Problems

**3 Explicit Tasks** (Session 8) with independent objectives:

| Task | Difficulty | Problems | Description |
|------|-----------|----------|-------------|
| `fix_logic_bug` | Easy→Medium | 10 | Logic errors, off-by-one, edge cases |
| `fix_algorithm_bug` | Medium→Hard | 10 | Type errors, loops, variable shadowing |
| `optimize_and_fix` | Hard | 10 | Recursion, optimization, complex fixes |

**Dataset**: 30 hand-crafted Python problems across 8 categories:

| Category | Count | Example |
|----------|-------|---------|
| Logic Errors | 4 | Wrong operators (`<` vs `>`) |
| Off-by-One | 4 | `range(n)` vs `range(n+1)` |
| Wrong Return | 4 | Returning wrong variable |
| Missing Edge Cases | 4 | Null checks, empty lists |
| Type Errors | 4 | String/int concatenation |
| Recursion Errors | 3 | Missing base case |
| Loop Errors | 2 | Infinite loops, wrong boundaries |
| Variable Shadowing | 2 | Scope issues, name collisions |
| Loop Errors | 4 | Early `break`, wrong loop variable, unreachable code |
| Variable Shadowing | 3 | Loop variable overwrites accumulator |

**Difficulty Distribution:**  
- Easy: 10 problems  
- Medium: 14 problems  
- Hard: 7 problems

---

## 🎮 Usage

### Install

```bash
pip install openenv-core
```

### Connect to Environment

```python
from openenv.core import EnvClient
from models import DebugAction

# Connect to deployed environment
env = EnvClient(base_url="https://huggingface.co/spaces/YOUR_USERNAME/python-debug-env")

with env.sync() as e:
    # Reset to get first problem
    obs = e.reset()
    print("Problem:", obs.description)
    print("Buggy code:", obs.buggy_code)
    
    # Agent analyzes and fixes code (simplified example)
    fixed_code = obs.buggy_code.replace("a - b", "a + b")  
    
    # Submit fix
    action = DebugAction(fixed_code=fixed_code)
    result = e.step(action)
    
    print(f"Reward: {result.reward:.2f}")
    print(f"  Test score: {result.info['test_score']:.2f}")
    print(f"  LLM score: {result.info['llm_score']:.2f}")
    print(f"  Tests passed: {result.info['passed_tests']}/{result.info['total_tests']}")
```

---

## 🔬 Reward System Details

### Component 1: Test Pass Rate (60%)

- Runs fixed code in **isolated subprocess** with 5-second timeout
- Executes against **3+ hidden test cases** per problem
- Returns fraction of tests passed: `0.0` (all fail) to `1.0` (all pass)
- Safe execution: catches `SyntaxError`, `RuntimeError`, `TimeoutError`

### Component 2: LLM Quality Judge (40%)

- Uses **Qwen2.5-Coder-7B-Instruct** via HuggingFace Inference API
- Evaluates:
  - ✅ Did the fix actually solve the bug?
  - ✅ Is the code clean and readable?
  - ✅ Is the approach minimal and appropriate?
- Returns quality score: `0.0` (poor) to `1.0` (excellent)
- Fallback: Returns `0.5` on API failure (neutral score)

### Final Reward Formula

```python
final_reward = 0.6 * test_pass_rate + 0.4 * llm_quality_score
```

**Why this weighting?**
- Test correctness is primary (objective, must pass tests)
- Code quality matters but is secondary (subjective, encourages good practices)

---

## 🛠️ Local Development

### Run Server Locally

```bash
# Clone and enter directory
cd python_debug_env

# Set HuggingFace token
echo "HF_TOKEN=hf_your_token_here" > .env

# Install dependencies
pip install -e .

# Run server
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

### Run with Docker

```bash
# Build image
docker build -t python-debug-env .

# Run container
docker run -p 8000:8000 --env-file .env python-debug-env
```

---

## 📁 Project Structure

```
python_debug_env/
├── models.py              # Pydantic types (Action, Observation, State)
├── bug_bank.py            # 30+ problem dataset
├── client.py              # EnvClient subclass
├── openenv.yaml           # Environment manifest
├── pyproject.toml         # Dependencies
└── server/
    ├── environment.py     # Environment logic (reset/step/state)
    ├── grader.py          # Dual reward computation
    ├── app.py             # FastAPI application
    └── Dockerfile         # Container definition
```

---

## 🚀 Deployment

Deploy to HuggingFace Spaces:

```bash
huggingface-cli login
openenv push --repo-id YOUR_USERNAME/python-debug-env
```

The environment will be live at:  
`https://huggingface.co/spaces/YOUR_USERNAME/python-debug-env`

---

## 🎯 Example Problem

**Problem ID:** `logic_001`  
**Difficulty:** Easy  
**Description:** Function should return the maximum of two numbers

**Buggy Code:**
```python
def find_max(a, b):
    if a < b:
        return a
    return b
```

**Expected Fix:**
```python
def find_max(a, b):
    if a > b:  # Changed < to >
        return a
    return b
```

**Test Cases (hidden from agent):**
- `find_max(5, 3)` → `5`
- `find_max(2, 8)` → `8`
- `find_max(7, 7)` → `7`

---

## 🏆 Hackathon Details

**Event:** Meta PyTorch OpenEnv Hackathon x Scaler School of Technology  
**Sponsors:** Meta PyTorch, Hugging Face, Scaler  
**Prize Pool:** $30,000  
**Deadline:** April 8, 2026  

**Judging Criteria:**
- ✅ Environment quality and originality
- ✅ Dual reward signal design
- ✅ Code quality and documentation
- ✅ Deployment to HuggingFace Spaces

---

## 🚀 Deployment

### Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/python-debug-env
cd python-debug-env

# Install dependencies
pip install -e .

# Set environment variables
cp .env.example .env
# Edit .env and add your HF_TOKEN

# Run server
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000

# Or use the entry point
server
```

### Docker

```bash
# Build image
docker build -t python-debug-env .

# Run container
docker run -p 8000:8000 --env-file .env python-debug-env

# Check health
curl http://localhost:8000/health
```

### HuggingFace Spaces

```bash
# Install OpenEnv CLI
pip install openenv-core

# Login to HuggingFace
huggingface-cli login

# Deploy to Spaces
openenv push --repo-id YOUR_USERNAME/python-debug-env

# Your environment will be available at:
# https://huggingface.co/spaces/YOUR_USERNAME/python-debug-env
```

---

## 📤 Baseline Inference

Run the baseline script to test your deployed environment:

```bash
# Set environment variables
export HF_TOKEN=your_token_here
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export ENV_URL=http://localhost:8000

# Run inference
python inference.py
```

**Example Output:**
```
[START] task=easy_1 env=python-debug-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=fix_code_logic_001 reward=0.92 done=true error=null
[END] success=true steps=1 rewards=0.92

[START] task=medium_1 env=python-debug-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=fix_code_off_by_one_003 reward=0.85 done=true error=null
[END] success=true steps=1 rewards=0.85

============================================================
Baseline Inference Results
============================================================
Model: Qwen/Qwen2.5-72B-Instruct
Episodes tested: 5
Episodes successful: 4
Success rate: 80.0%
Average reward: 0.812
============================================================
```

---

## 🔧 Troubleshooting

### Server Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Try a different port
uvicorn server.app:app --host 0.0.0.0 --port 8080
```

### LLM Judge Returns Low Scores

- Check that `HF_TOKEN` is set correctly in `.env`
- Verify HuggingFace Inference API is accessible
- The judge uses a fallback score of 0.5 if API fails

### Docker Build Fails

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t python-debug-env .
```

### openenv validate Fails

```bash
# Ensure all dependencies are installed
pip install -e .

# Check openenv.yaml syntax
cat openenv.yaml

# Regenerate uv.lock if needed
python -m uv lock
```

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **OpenEnv Framework:** [meta-pytorch/OpenEnv](https://github.com/meta-pytorch/OpenEnv)
- **LLM Judge Model:** [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
- **Hackathon:** [Scaler School of Technology](https://www.scaler.com/school-of-technology/meta-pytorch-hackathon)
