# API & Authentication Guide

> **Last Updated**: Current Session  
> **Status**: ✅ Complete & Accurate

---

## Overview

BugLab uses **HuggingFace Router API** (via OpenAI-compatible client) for inference. **Grading is 100% deterministic** - no LLM calls in the scoring system.

---

## Architecture

### Two Distinct Flows

```
┌─────────────────────────────────────────────────┐
│ 1. INFERENCE SCRIPT (inference.py)              │
│    Purpose: Baseline testing with LLM agent     │
│    API: HuggingFace Router (OpenAI-compatible)  │
│    Model: Qwen/Qwen2.5-72B-Instruct             │
│    Auth: OPENAI_API_KEY or HF_TOKEN             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 2. ENVIRONMENT (server/environment.py)          │
│    Purpose: Evaluation and reward calculation   │
│    Grading: STATIC ANALYSIS ONLY (no LLM)       │
│    Components:                                   │
│      - Test execution (subprocess sandbox)      │
│      - Code quality checks (AST + static)       │
│      - No API calls required                    │
└─────────────────────────────────────────────────┘
```

---

## API Configuration

### HuggingFace Router (Used in inference.py)

**Endpoint**: `https://router.huggingface.co/v1`

**Model**: `Qwen/Qwen2.5-72B-Instruct`

**Client**: OpenAI Python library with custom base_url

```python
# From inference.py (Lines 21-31)
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("API_KEY")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)
```

**Why OpenAI Client?**
- HuggingFace Router implements OpenAI API specification
- Same interface works with any OpenAI-compatible endpoint
- Future-proof for switching APIs

**Why HuggingFace Router?**
- Free inference API
- No local model loading (RAM constraint)
- Managed by HuggingFace
- Faster than local inference

---

## Authentication

### Environment Variables (Priority Order)

**For inference.py (lines 31-32)**:
```
1. OPENAI_API_KEY  (primary)
2. HF_TOKEN         (fallback)
3. API_KEY          (fallback)
```

If none provided: Script fails with error message.

### Setting Credentials

**Local Development**:
```bash
export OPENAI_API_KEY=hf_xxxxxxxxxxxxx
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export API_BASE_URL=https://router.huggingface.co/v1

python inference.py
```

**Docker**:
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=hf_xxxxxxxxxxxxx \
  -e MODEL_NAME=Qwen/Qwen2.5-72B-Instruct \
  -e API_BASE_URL=https://router.huggingface.co/v1 \
  buglab
```

**HuggingFace Spaces**:
- Set secrets in Space settings: `OPENAI_API_KEY`
- Container reads from environment

---

## Grading System (NO API CALLS)

### Dual Reward Formula

```python
# From server/environment.py (Lines 220-247)

test_score, test_details = run_tests_sandboxed(action.fixed_code)
quality_score, quality_feedback = analyze_code_quality(action.fixed_code)

base_reward = 0.7 * test_score + 0.3 * quality_score
improvement_bonus = 0.5 * (quality_score - prev_score) + 0.1
final_reward = min(1.0, base_reward + improvement_bonus)
```

### Component 1: Test Score (70%)
**Function**: `run_tests_sandboxed()` → `server/grader.py`

- Executes fixed code in subprocess
- Runs against test cases (from bug_bank.py)
- Returns: pass_count / total_tests
- **NO API CALLS**

### Component 2: Quality Score (30%)
**Function**: `analyze_code_quality()` → `server/grader.py`

Static analysis checks (all local):

| Check | Method | Contribution |
|-------|--------|--------------|
| Syntax Valid | AST parsing | +0.10 |
| No Unused Vars | AST visitor | -0.05 each |
| PEP8 Compliant | pycodestyle | +0.10 |
| Cyclomatic Complexity | radon library | +0.10 |
| Function Length | Line counting | +0.10 |
| No Anti-patterns | Regex checks | +0.10 |

**NO API CALLS** - All checks run locally

### Why No LLM in Grading?

1. **Reproducibility**: Same code → same score always
2. **Speed**: Deterministic, no API latency
3. **Judge-proof**: Objective, verifiable criteria
4. **Cost**: No API charges for evaluation
5. **Fairness**: No LLM bias or inconsistency

---

## File References

### Inference Script
**File**: `inference.py` (Root)

Key lines:
- **7-8**: OpenAI client import
- **21-31**: API configuration
- **120-125**: LLM call to generate fixes
- **173-174**: API error handling

### Environment (Grading)
**File**: `server/environment.py`

Key lines:
- **220-247**: Dual reward calculation
- **229**: Call to `analyze_code_quality()` (NO API)
- **228**: Call to `run_tests_sandboxed()` (NO API)

**File**: `server/grader.py`

Key sections:
- **204-293**: `call_llm_judge()` (DEPRECATED, unused)
- **295-370+**: `analyze_code_quality()` (STATIC ONLY)
- **80-170**: `run_tests_sandboxed()` (SUBPROCESS SANDBOX)

---

## Summary

| Component | API Used | Endpoint | Auth | Purpose |
|-----------|----------|----------|------|---------|
| **inference.py** | HF Router | https://router.huggingface.co/v1 | HF_TOKEN | Baseline agent testing |
| **server/environment.py** | None | N/A | N/A | OpenEnv API |
| **server/grader.py** | None | N/A | N/A | Deterministic grading |
| **server/app.py** | None | N/A | N/A | FastAPI server |

---

## Migration Guide

**If switching to different API**:

1. Only change `API_BASE_URL` and `MODEL_NAME` in environment
2. Code remains unchanged (OpenAI-compatible interface)
3. Grading system unaffected (always deterministic)

**Examples**:
```bash
# OpenAI API
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o
export OPENAI_API_KEY=sk-...

# Local Ollama
export API_BASE_URL=http://localhost:11434/v1
export MODEL_NAME=llama2
# No auth needed for local

# Azure OpenAI
export API_BASE_URL=https://{resource}.openai.azure.com/
export MODEL_NAME=gpt-4
export OPENAI_API_KEY={azure-key}
```

---

## Troubleshooting

**Error**: "OPENAI_API_KEY not set"
- **Fix**: Export HF_TOKEN or OPENAI_API_KEY before running

**Error**: "API connection failed"
- **Check**: Is API_BASE_URL reachable?
- **Check**: Is HF_TOKEN valid?
- **Check**: Is model available?

**Error**: "Invalid model name"
- **Fix**: Ensure model exists on HuggingFace

**Grading failures** (should not happen)
- **Note**: Grading is local, no API involved
- **Debug**: Check test cases in bug_bank.py

---

*This document is the authoritative reference for API usage in BugLab.*
