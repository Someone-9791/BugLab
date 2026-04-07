
# BugLab: Python Code Debugging Environment 🐛→✨

An **OpenEnv reinforcement learning environment** where AI agents learn to debug broken Python code using **deterministic, reproducible evaluation**.

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-blue)](https://github.com/meta-pytorch/openenv)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-orange)](https://huggingface.co/spaces/Someone5249/BugLab)

---

## Overview

**BugLab** is a real-world RL environment where agents fix broken Python code. Features:

- ✅ **30+ debugging problems** across 8 error categories
- ✅ **3 explicit tasks** (easy → hard difficulty progression)
- ✅ **Deterministic dual reward**: 70% test pass rate + 30% code quality
- ✅ **Multi-step learning**: 3 attempts per problem with progress signals
- ✅ **Fully OpenEnv compliant** with type validation
- ✅ **Reproducible grading** - no API calls, no randomness
- ✅ **Production ready** - deployed on HuggingFace Spaces

---

## Quick Start

### Installation

```bash
git clone https://github.com/Someone-9791/BugLab.git
cd BugLab
pip install -r requirements.txt
```

### Local Development

```bash
# Start server
python -m server.app

# In another terminal, run baseline
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_TOKEN=your_hf_token

python inference.py
```

### Docker Deployment

```bash
docker build -t buglab .
docker run -p 8000:8000 \
  -e API_BASE_URL=https://router.huggingface.co/v1 \
  -e MODEL_NAME=Qwen/Qwen2.5-72B-Instruct \
  -e HF_TOKEN=your_token \
  buglab
```

---

## Key Features

### Three Tasks with Progressive Difficulty

| Task | Difficulty | Objective | Examples |
|------|-----------|-----------|----------|
| `fix_logic_bug` | Easy→Medium | Fix logic errors and operators | Wrong comparison, off-by-one, missing edge cases |
| `fix_algorithm_bug` | Medium→Hard | Fix algorithmic errors | Type errors, wrong returns, recursion bugs |
| `optimize_and_fix` | Hard | Fix complex bugs + optimize | Performance issues, nested logic, multiple bugs |

### Evaluation Metrics

**Dual Reward System** (Deterministic & Reproducible):
- **Test Score (70%)**: Automated test execution - no randomness
- **Quality Score (30%)**: Static code analysis (AST) - 6 quality checks
- **Progress Bonus**: Multi-step rewards for improvement

```
final_reward = (0.7 × test_score) + (0.3 × quality_score) + bonus
clamped to [0.0, 1.0]
```

---

## Baseline Performance

Evaluated with **Qwen/Qwen2.5-72B-Instruct** (temperature=0.0, deterministic):

| Metric | Result |
|--------|--------|
| Overall Reward | 0.678 |
| Success Rate | 40% |
| Easy Tasks | 83.0% |
| Medium Tasks | 64.2% |
| Hard Tasks | 44.5% |
| Runtime | < 5 minutes (2 vCPU, 8GB RAM) |

---

## API & Integration

BugLab exposes a simple REST API:

```bash
# Reset: get a new debugging problem
curl -X POST http://localhost:8000/reset \
  -d '{"task_id": "fix_logic_bug"}'

# Step: submit fixed code and get reward
curl -X POST http://localhost:8000/step \
  -d '{"fixed_code": "fixed code here"}'

# State: get current episode state
curl -X GET http://localhost:8000/state
```

**Full API documentation**: See [`server/app.py`](server/app.py)

---

## Project Structure

```
BugLab/
├── server/              # FastAPI backend
│   ├── app.py          # API endpoints
│   ├── environment.py   # OpenEnv implementation
│   └── grader.py        # Deterministic grading engine
├── models.py            # Type definitions (Pydantic)
├── bug_bank.py          # 30+ debugging problems
├── inference.py         # Baseline agent script
├── openenv.yaml         # OpenEnv spec (validated)
├── Dockerfile           # Container config
├── requirements.txt     # Dependencies
└── Obsidian-VS/         # Technical documentation
```

---

## Compliance & Standards

✅ **OpenEnv Specification**
- Typed models (Pydantic)
- Full API: `reset()`, `step()`, `state()`
- Validated with `openenv validate`

✅ **Hackathon Requirements**
- Real-world debugging task
- 3 tasks with difficulty progression
- Deterministic reward (0.0-1.0)
- Reproducible baseline script
- Docker deployment ready

✅ **Code Quality**
- Type hints throughout
- Clean API design
- Well-documented (Obsidian vault)
- Security sandboxing

---

## License & Acknowledgments

- **License**: MIT
- **Framework**: OpenEnv (Meta/PyTorch)
- **Challenge**: OpenEnv Hackathon 2026

See [LICENSE](LICENSE) for details. For security issues, see [SECURITY.md](SECURITY.md).

---

**Questions?** Check the [technical documentation](Obsidian-VS/) or open an issue.
