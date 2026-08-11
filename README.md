
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
- ✅ **Intelligent hints**: Category-specific guidance to accelerate agent learning
- ✅ **Partial credit system**: Reward for progressively passing tests (not all-or-nothing)
- ✅ **Rich error feedback**: Detailed test failures and suggestions for common mistakes
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
# Start FastAPI server (for API access)
uvicorn server.app:app --host 0.0.0.0 --port 8000

# In another terminal, run baseline
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_TOKEN=your_hf_token

python inference.py
```

### Interactive UI (Optional)

For local testing with a visual web interface:

```bash
# Start Gradio UI
python -m server.gradio_ui

# Visit http://localhost:7860 in your browser
```

**Note:** The HuggingFace Space runs the API server (not the UI) to enable automated agent evaluation. The Gradio UI is for local manual testing only.

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
- **Test Score (70%)**: Automated test execution - partial credit for passing subset of tests
- **Quality Score (30%)**: Static code analysis (AST) - 6 quality checks
- **Progress Bonus**: Multi-step rewards for improvement
- **Category Hints**: Agents receive targeted guidance based on error category
- **Error Details**: Comprehensive feedback on test failures with input/output/error information

```
final_reward = (0.7 × test_score) + (0.3 × quality_score) + improvement_bonus
clamped to [0.0, 1.0]

where test_score = passed_tests / total_tests  (rewards partial progress)
```

---

## Baseline Performance

Evaluated with **Qwen/Qwen2.5-72B-Instruct** (temperature=0.0, deterministic):

--------------------------------------------------
| Metric         | Result                        |
|----------------|-------------------------------|
| Overall Reward | 0.678                         |
| Success Rate   | 40%                           |
| Easy Tasks     | 83.0%                         |
| Medium Tasks   | 64.2%                         |
| Hard Tasks     | 44.5%                         |
| Runtime        | < 5 minutes (2 vCPU, 8GB RAM) |

---

## Advanced Features (Competitive Advantages)

### Partial Credit Scoring
Agents earn rewards for progressive improvement, not just all-or-nothing success. Passing 3/5 tests yields reward proportional to progress.

### Intelligent Feedback
- Category-specific hints guide debugging strategy
- Detailed error messages show failed tests, expected vs. actual output
- Rich observation includes pass/fail counts and suggestions

### Production-Ready Reliability
- Timeout protection (30s) prevents hanging
- Concurrent-safe request handling
- Graceful error handling with 400-level responses

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
│   ├── app.py           # REST API endpoints (/reset, /step, /state)
│   ├── environment.py    # OpenEnv implementation
│   └── grader.py         # Deterministic grading engine
├── models.py             # Type definitions (Pydantic)
├── bug_bank.py           # 30+ debugging problems
├── inference.py          # Baseline agent evaluation script
├── openenv.yaml          # OpenEnv specification
├── Dockerfile            # Docker container config
├── requirements.txt      # Python dependencies
└── ARCHITECTURE.md       # Detailed technical documentation
```

---

## Compliance & Standards

✅ **OpenEnv Compliant** — Full specification implemented (reset, step, state, type validation)

✅ **Deterministic & Reproducible** — No randomness in grading; baseline achieves 67.8% average reward

✅ **Production Ready** — Handles concurrent requests, 30s timeout protection, graceful error responses

✅ **Live Deployment** — Running on HuggingFace Spaces with Docker containerization

---

## Team

**Team Name:** Team "Not Found"

| Role | Name |
|------|------|
| 👨‍💻 **Main Developer**  | Pranatpal Sharma |
| 👩‍💼 **Team Leader**     | Shloka Chourasia |
| 🎨 **UI/UX Developer** | Vedant Sharma    |

---

## License & Acknowledgments

- **License**: MIT
- **Framework**: OpenEnv (Meta/PyTorch)
- **Challenge**: OpenEnv Hackathon 2026

See [LICENSE](LICENSE) for details. For security issues, see [SECURITY.md](SECURITY.md).

---

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Complete technical reference (systems, APIs, task definitions)
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines
- **[LICENSE](LICENSE)** — MIT license

