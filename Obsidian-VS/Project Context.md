# Project Context - PythonDebugEnv

> Technical specification and complete project understanding
> Source: `/home/someone/ml/PROJECT_CONTEXT.md`

---

## 🎪 The Hackathon

**Name:** Meta PyTorch OpenEnv Hackathon x Scaler School of Technology  
**URL:** https://www.scaler.com/school-of-technology/meta-pytorch-hackathon  
**Sponsors:** Meta PyTorch, Hugging Face, Scaler School of Technology

### Timeline
- Round 1 Starts: March 25, 2026
- **Round 1 Deadline: April 8, 2026** ⚠️
- Results: April 10, 2026
- Advanced Bootcamp: April 18-19, 2026
- Grand Finale (Bangalore): April 25-26, 2026

### Judging Criteria
- Quality and originality of environment
- **Reward function design** (dual signals score higher)
- Code quality and documentation
- Deployment to HuggingFace Spaces

---

## 🧠 The Concept: PythonDebugEnv

An RL environment where LLM agents receive **broken Python code** and must return **corrected versions**.

### Why This is Strong
1. ✅ **Dual reward signals** - Exactly what judges want
2. ✅ **Coding domain** - Relevant to Meta/HF interests
3. ✅ **GPU utilization** - Local LLM judge (RX 9060 XT)
4. ✅ **Novel dataset** - Custom bug bank, not recycled benchmarks

---

## 🎮 Environment Flow

```
1. Agent calls env.reset()
   └─► Returns DebugObservation(
         problem_id="bug_042",
         buggy_code="def add(a,b): return a-b",
         description="This function should add two numbers",
         test_cases=[{"input": [2,3], "expected": 5}],
         difficulty="easy"
       )

2. Agent analyzes code, generates fix

3. Agent calls env.step(DebugAction(fixed_code="def add(a,b): return a+b"))
   └─► Returns StepResult(
         observation=DebugObservation(...next...),
         reward=0.92,
         done=True,
         info={
           "test_score": 1.0,
           "llm_score": 0.8,
           "passed_tests": 3,
           "total_tests": 3
         }
       )
```

---

## 🏆 Reward Formula

```python
final_reward = 0.6 * test_pass_rate + 0.4 * llm_quality_score
```

**Components:**
1. **test_pass_rate** (0.0-1.0) - Deterministic
   - Sandboxed subprocess execution
   - 5-second timeout
   - Hidden test cases
   - Fast and objective

2. **llm_quality_score** (0.0-1.0) - LLM-as-Judge
   - Qwen2.5-Coder-7B-Instruct via HF Inference API
   - Evaluates correctness, code quality, approach
   - Returns JSON: `{"score": 0.85, "reason": "..."}`
   - Fallback to 0.5 on any error

---

## 📊 Bug Categories (30 Problems)

| Category | Count | Examples |
|----------|-------|----------|
| Logic Errors | 4 | Wrong operators (`>` vs `>=`) |
| Off-by-One | 4 | `range(n)` vs `range(n+1)` |
| Wrong Return | 4 | Returns wrong variable |
| Missing Edge Cases | 4 | No null checks |
| Type Errors | 4 | String + int without conversion |
| Recursion Errors | 3 | Missing base case |
| Loop Errors | 4 | Infinite loop, wrong variable |
| Variable Shadowing | 3 | Variable name conflicts |

**Difficulty:** 9 easy, 15 medium, 6 hard

---

## 🖥️ System Configuration

### Hardware
- **CPU:** AMD Ryzen 5600X (6C/12T)
- **RAM:** 8GB DDR4 3200MHz ⚠️ BOTTLENECK
- **GPU:** AMD Radeon RX 9060 XT (16GB VRAM, RDNA4)
- **Storage:** 128GB SSD (Linux)

### Software Stack
```
Ubuntu 24.04.4 LTS
└─ Kernel 6.17.0-20-generic (HWE for RDNA4)
   └─ ROCm 7.2.1 (/opt/rocm-7.2.1)
      └─ Python 3.12.3 venv (~/ml)
         ├─ PyTorch 2.9.1+rocm7.2.1
         ├─ transformers 5.4.0
         ├─ openenv 0.2.3
         ├─ fastapi + uvicorn
         ├─ huggingface_hub
         └─ numpy 1.26.4 (PINNED - do not upgrade!)
```

### Critical Notes
- **8GB RAM = No local models in Python** - Use HF Inference API
- **Always activate venv:** `source ~/ml/bin/activate`
- **ROCm uses CUDA-compatible API** - `torch.cuda.is_available()` works
- **numpy 1.26.4 is locked** - v2.0 breaks ROCm PyTorch

---

## 🔧 LLM Judge Strategy

**Primary (RAM-constrained):**
- HuggingFace Inference API (free tier)
- Model: `Qwen/Qwen2.5-Coder-7B-Instruct`
- Zero RAM overhead (runs on HF servers)
- Rate limited but sufficient
- Requires `HF_TOKEN` in `.env`

**Secondary (if needed):**
- llama.cpp with ROCm backend
- Q4_K_M quantized (~4.5GB VRAM)
- Local at `http://localhost:8080`
- ~92 tokens/sec on RX 9060 XT

---

## 🚀 OpenEnv Framework

**GitHub:** https://github.com/meta-pytorch/OpenEnv  
**Docs:** https://meta-pytorch.org/OpenEnv/

### Core API (3 methods)
```python
env.reset()   # Initialize episode → Observation
env.step()    # Accept Action → StepResult (obs + reward + done)
env.state()   # Return episode metadata
```

### Architecture
```
Client (LLM Agent)
    │ WebSocket
    ▼
FastAPI Server (Docker container)
    ├─ Environment class (your logic)
    ├─ Grader (reward computation)
    └─ HF Spaces deployment
```

### Commands
```bash
pip install openenv-core
openenv init my_env        # Scaffold new environment
openenv push              # Deploy to HuggingFace Spaces
```

---

## 📋 Environment Variables

`.env` file contents:
```bash
HF_TOKEN=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
LLM_JUDGE_MODE=api        # "api" or "local"
LOCAL_LLM_URL=http://localhost:8080
```

---

## ⚠️ Critical Constraints

1. **Never use eval()/exec()** - Always subprocess with timeout
2. **Always timeout subprocesses** - Agents can submit infinite loops
3. **LLM judge must not crash** - Wrap in try/except, return 0.5
4. **numpy 1.26.4 locked** - Do not upgrade
5. **Always activate venv** - `source ~/ml/bin/activate`
6. **ROCm path:** `/opt/rocm-7.2.1` (symlinked to `/opt/rocm`)
7. **HF_TOKEN in .env** - Never hardcode
8. **8GB RAM limit** - No models >3B in fp16 directly
9. **Docker port 8000** - OpenEnv standard
10. **openenv.yaml accuracy** - Judges read this

---

*Back to [[PythonDebugEnv Project Hub]]*
