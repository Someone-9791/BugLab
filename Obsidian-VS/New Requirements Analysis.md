# 🚨 NEW REQUIREMENTS ANALYSIS - April 4, 2026

> **URGENT:** Updated hackathon requirements received  
> **Impact:** MODERATE - Some design changes needed  
> **Status:** Reviewing and updating project plan

---

## 📋 NEW MANDATORY REQUIREMENTS

### 1. Minimum 3 Tasks ✅ WE HAVE THIS
**Requirement:** "Minimum 3 tasks with agent graders (easy → medium → hard)"

**Our Status:**
- ✅ **30 problems** across 3 difficulty levels
- ✅ 9 easy, 15 medium, 6 hard
- ✅ Each has deterministic grader (test cases)
- ✅ Each has LLM grader component

**Interpretation:** 
- They want at least 3 distinct tasks at different difficulties
- We have 30, so we EXCEED this requirement significantly
- Our approach: Agent gets random problem from difficulty-appropriate pool

---

### 2. Baseline inference.py Script ❌ MISSING - HIGH PRIORITY

**Requirement:** 
```
- Must be named `inference.py` in root directory
- Uses OpenAI Client for all LLM calls
- Reads from env vars: API_BASE_URL, MODEL_NAME, HF_TOKEN
- Produces reproducible baseline scores on all 3 tasks
- Runtime < 20 minutes
- Works on 2 vCPU, 8GB RAM
```

**What We Need:**
```python
# inference.py structure
import os
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN")

# Connect to our environment
# Run agent against easy, medium, hard tasks
# Emit structured logs
```

**Estimated Work:** 2-3 hours

---

### 3. Structured Logging Format ❌ MISSING - HIGH PRIORITY

**Requirement:** Must emit exactly this format to stdout:

```
[START] task=<task_name> env=<benchmark> model=<model_name>
[STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
[END]   success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
```

**Rules:**
- One [START] per episode
- One [STEP] per step (immediately after env.step())
- One [END] after env.close() (always, even on exception)
- reward formatted to 2 decimals
- done/success are lowercase booleans
- error is string or null

**Example:**
```
[START] task=logic_001 env=python-debug-env model=Qwen2.5-72B-Instruct
[STEP] step=1 action=fix_code reward=0.92 done=true error=null
[END] success=true steps=1 rewards=0.92
```

**Implementation:** Add to `inference.py`

---

### 4. Additional Environment Variables ❌ NOT CONFIGURED

**Current `.env`:**
```bash
HF_TOKEN=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
LLM_JUDGE_MODE=api
LOCAL_LLM_URL=http://localhost:8080
```

**Required additions:**
```bash
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
# Optional:
LOCAL_IMAGE_NAME=python-debug-env
```

**Action:** Update `.env` file

---

### 5. openenv validate ❌ NOT TESTED

**Requirement:** `openenv validate` must pass before submission

**What it checks:**
- openenv.yaml correctness
- Typed models (Action, Observation, State)
- step()/reset()/state() endpoints
- Spec compliance

**Action:** Run after Phase 2 complete

---

### 6. Pre-validation Script ❌ NOT RUN

**Checks:**
1. Docker build succeeds
2. openenv validate passes
3. (Additional checks TBD)

**Action:** Run before final submission

---

## 📊 EVALUATION CRITERIA (WEIGHTS REVEALED)

| Criterion | Weight | Our Assessment |
|-----------|--------|----------------|
| **Real-world utility** | 30% | ✅ STRONG - Code debugging is highly practical |
| **Task & grader quality** | 25% | ✅ STRONG - Dual reward, 30 problems, clear grading |
| **Environment design** | 20% | ⚠️ REVIEW - Need to ensure clean state, good action/obs spaces |
| **Code quality & spec** | 15% | ⚠️ PENDING - Must pass openenv validate |
| **Creativity & novelty** | 10% | ✅ GOOD - Dual reward design, code domain |

**Total Confidence:** ~70% (need to nail environment design + spec compliance)

---

## 🔧 ENVIRONMENT DESIGN CHECKLIST

Based on 20% weight for "Environment design":

- [ ] **reset() produces clean state?** - Need to verify
- [ ] **Action/observation types well-designed?** - ✅ Already done in models.py
- [ ] **Reward function provides varying signal (not sparse)?** - ✅ Dual reward 0.0-1.0
- [ ] **Episode boundaries sensible?** - ⚠️ Currently single-turn, is this okay?

**Question:** Should we change from single-turn to multi-turn?
- Single-turn: Agent gets 1 problem, submits 1 fix, episode ends
- Multi-turn: Agent could request hints, ask questions, iterate?

**Decision:** Keep single-turn for now (simpler, matches real code review flow)

---

## 📝 UPDATED PROJECT GAPS

### Phase 2 (Original - Still needed)
- [ ] server/grader.py
- [ ] server/environment.py
- [ ] server/app.py
- [ ] client.py

### NEW Phase 2.5 (Inference & Validation)
- [ ] **inference.py** (root directory) 🔥 NEW
- [ ] Update .env with API_BASE_URL, MODEL_NAME 🔥 NEW
- [ ] Implement structured logging in inference.py 🔥 NEW
- [ ] Run `openenv validate` 🔥 NEW
- [ ] Test inference script end-to-end 🔥 NEW

### Phase 4 (Updated)
- [ ] Dockerfile (unchanged)
- [ ] Run pre-validation script 🔥 NEW

---

## ⏱️ REVISED TIME ESTIMATES

| Task | Original | Revised | Notes |
|------|----------|---------|-------|
| Phase 2: Server | 6-8h | 6-8h | Unchanged |
| **Phase 2.5: Inference** | - | **3-4h** | 🆕 NEW |
| Phase 3: LLM Judge | 3h | 2h | (Integrated in grader) |
| Phase 4: Docker | 5h | 6h | (+validation script) |
| Phase 5: Deploy | 6h | 6h | Unchanged |
| Buffer | 8h | 5h | Reduced buffer |
| **Total** | **36h** | **38h** | +2 hours |

**Still comfortable:** 38h needed, 86h available

---

## 🎯 UPDATED PRIORITY ORDER

### TODAY (April 4th) - Critical Path
1. **Complete Phase 2** (server components) - 6-8h
2. **Create inference.py** - 3h 🔥 NEW
3. **Update .env** - 5min 🔥 NEW
4. **Test openenv validate** - 30min 🔥 NEW

### April 5th
1. Phase 4: Docker + pre-validation
2. Test inference script in container
3. Fix any validation issues

### April 6th
1. Phase 5: Deploy to HF Spaces
2. End-to-end testing
3. Documentation polish

---

## 🚨 RISKS & MITIGATIONS

### Risk 1: openenv validate fails
**Likelihood:** Medium  
**Impact:** High (disqualification)  
**Mitigation:** Test early and often after Phase 2

### Risk 2: Inference script format incorrect
**Likelihood:** Medium  
**Impact:** High (incorrect scoring)  
**Mitigation:** Follow example exactly, test stdout parsing

### Risk 3: Single-turn design penalized
**Likelihood:** Low  
**Impact:** Medium (lose points on "environment design")  
**Mitigation:** Justify in README as matching real code review workflow

### Risk 4: Docker build fails validation
**Likelihood:** Low  
**Impact:** High (disqualification)  
**Mitigation:** Test with pre-validation script before submission

---

## ✅ CONFIDENCE ASSESSMENT

**Current Strengths:**
- ✅ 30 problems (way exceeds "minimum 3")
- ✅ Dual reward design (creative, judges like this)
- ✅ Real-world domain (code debugging)
- ✅ Clear grading criteria

**Areas to Nail:**
- ⚠️ Spec compliance (openenv validate)
- ⚠️ Inference script format (exact stdout format)
- ⚠️ Docker validation (pre-validation script)
- ⚠️ Environment design polish

**Overall Confidence:** 75% → Can win if we execute well

---

*Back to [[PythonDebugEnv Project Hub]]*
