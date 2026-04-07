# Critical Compliance Fixes - Action Plan

**Status**: URGENT (4 critical issues identified)  
**Deadline**: April 8, 2026 (3 days)  
**Risk Level**: 🔴 HIGH (Disqualification possible)  
**Time Required**: 3-5 hours for critical fixes  
**Effort**: Doable (must start today)

---

## 🚨 CRITICAL ISSUES (Must Fix Before HF Deployment)

### CRITICAL #1: Non-Deterministic Grading ❌

**Problem**:
- `inference.py` uses `temperature = 0.7`
- Same code → different reward each run
- Violates: "Graders must be deterministic and reproducible"

**Risk**: DISQUALIFICATION
- Judges run baseline twice
- If scores differ → automatic fail
- This is explicit requirement

**Current Code** (inference.py, ~line 35):
```python
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[...],
    temperature=0.7,  # ← PROBLEM: Non-deterministic
    max_tokens=150
)
```

**Fix (Choose One)**:

Option A (RECOMMENDED - 5 min):
```python
temperature=0.0  # Deterministic outputs
random.seed(42)
```

Option B (More complex - 20 min):
```python
# Cache LLM outputs by code hash
def get_llm_score(buggy_code, fixed_code):
    key = hash(buggy_code + fixed_code)
    if key in CACHE:
        return CACHE[key]
    score = call_llm(...)
    CACHE[key] = score
    return score
```

Option C (Simplest - 10 min):
```python
# Remove LLM, use only test scores
reward = test_score  # Just tests, no LLM evaluation
```

**Recommendation**: Option A
- Keeps LLM evaluation (for code quality)
- Deterministic (judges require this)
- Takes 5 minutes

**Implementation**:
1. Edit inference.py line 35
2. Change temperature=0.7 → temperature=0.0
3. Add random.seed(42) at start
4. Test: Run inference.py twice, compare scores
5. ✓ Should be identical both times

---

### CRITICAL #2: Task Selection API ❌

**Problem**:
- API doesn't expose task/difficulty selection
- Requirement: "minimum 3 tasks (easy/medium/hard)"
- Judges can't test each difficulty separately
- Violates: "Enumerate tasks independently"

**Current Code** (server/app.py):
```python
@app.post("/reset")
async def reset():
    problem = random.choice(PROBLEMS)  # ← Random, no control
    return observation
```

**Fix** (30 minutes):

Change to:
```python
@app.post("/reset")
async def reset(difficulty: str = None):
    if difficulty:
        # Filter problems by difficulty
        filtered = [p for p in PROBLEMS if p['difficulty'] == difficulty]
        if not filtered:
            raise HTTPException(400, f"No problems with difficulty {difficulty}")
        problem = random.choice(filtered)
    else:
        problem = random.choice(PROBLEMS)
    
    # Store in class-level state
    DebugEnv._global_problem = problem
    return observation
```

**New API Usage**:
```bash
# Reset with specific difficulty
curl -X POST http://localhost:8000/reset?difficulty=easy
curl -X POST http://localhost:8000/reset?difficulty=medium
curl -X POST http://localhost:8000/reset?difficulty=hard

# Reset with random problem
curl -X POST http://localhost:8000/reset
```

**Also Update** models.py to document:
```python
class ResetRequest(BaseModel):
    difficulty: str = None  # Optional: "easy", "medium", "hard"
```

**Test**:
```bash
# Run each difficulty multiple times
for i in {1..3}; do
    curl -X POST http://localhost:8000/reset?difficulty=easy
done
# All should succeed
```

---

### CRITICAL #3: Baseline Not Reproducible ❌

**Problem**:
- inference.py generates LLM actions
- Non-deterministic LLM outputs
- Same baseline script → different scores
- Violates: "Baseline reproduces scores"

**Current Code** (inference.py, ~line 120):
```python
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[...],
    temperature=0.7  # ← Non-deterministic
)
fixed_code = response.choices[0].message.content
# Different code each time → different score
```

**Fix** (10 minutes):
1. Fix temperature to 0.0 (see Critical #1)
2. Add seed at start:
   ```python
   import random
   import numpy as np
   
   random.seed(42)
   np.random.seed(42)
   ```
3. Test reproducibility:
   ```bash
   python inference.py > run1.txt
   python inference.py > run2.txt
   diff run1.txt run2.txt  # Should be identical
   ```

**Verification**:
- Run inference.py 3 times
- Compare scores in [END] lines
- Should be 100% identical

---

### CRITICAL #4: Single-Turn Environment ❌

**Problem**:
- step() immediately returns done=true
- Agent gets one shot, no iteration
- Violates: "Reward must provide signal over trajectory"
- Loses 20% of scoring on environment design

**Current Code** (server/environment.py):
```python
def step(action):
    # Evaluate fix
    test_score, llm_score = grader.grade(action.fixed_code)
    reward = 0.6 * test_score + 0.4 * llm_score
    
    # Always done after one step
    return observation, reward, done=true  # ← PROBLEM
```

**Why It's Bad**:
- RL requires trajectory (multiple steps)
- Real debugging is iterative
- Agent should be able to improve

**Fix** (1-2 hours):

Update environment.py:
```python
class DebugEnv:
    def __init__(self):
        self.max_attempts = 3
        self.attempts = 0
        self.best_score = 0.0
        self.best_code = ""
    
    def reset(self):
        self.attempts = 0
        self.best_score = 0.0
        return observation
    
    def step(self, action):
        self.attempts += 1
        
        # Grade the submission
        test_score, llm_score = grader.grade(action.fixed_code)
        reward = 0.6 * test_score + 0.4 * llm_score
        
        # Track best attempt
        if reward > self.best_score:
            self.best_score = reward
            self.best_code = action.fixed_code
        
        # Determine if done
        done = (
            self.attempts >= self.max_attempts or  # Out of attempts
            reward >= 0.95  # Or nearly perfect
        )
        
        # Add intermediate reward signal
        intermediate = 0.0
        if test_score > 0:
            intermediate += 0.1 * test_score
        if self.attempts > 1 and reward > self.best_score - 0.01:
            intermediate += 0.05  # Bonus for improvement
        
        final_reward = intermediate if not done else reward
        
        observation = DebugObservation(
            problem_statement=...,
            buggy_code=...,
            test_score=test_score,
            llm_score=llm_score,
            feedback=self._generate_feedback(reward, self.attempts),
            attempt=self.attempts,
            max_attempts=self.max_attempts
        )
        
        return observation, final_reward, done
    
    def _generate_feedback(self, reward, attempt):
        if reward >= 0.95:
            return "Excellent! Problem solved!"
        elif reward >= 0.7:
            return f"Good progress! ({reward:.0%}). Try again to improve."
        elif reward >= 0.4:
            return f"Some progress ({reward:.0%}). Keep trying!"
        else:
            return f"Not quite right ({reward:.0%}). Please try again."
```

Also update models.py:
```python
class DebugObservation(BaseModel):
    problem_statement: str
    buggy_code: str
    test_score: float
    llm_score: float
    feedback: str
    attempt: int = 1  # NEW
    max_attempts: int = 3  # NEW
```

**Test**:
```bash
# Should allow multiple /step calls
curl -X POST http://localhost:8000/reset
curl -X POST http://localhost:8000/step -d '{"action":{"fixed_code":"..."}}'
# done=false on first attempt
curl -X POST http://localhost:8000/step -d '{"action":{"fixed_code":"..."}}'
# done=false on second attempt
curl -X POST http://localhost:8000/step -d '{"action":{"fixed_code":"..."}}'
# done=true on third attempt (or if perfect)
```

---

## ⚠️ MAJOR ISSUES (High Impact, Should Fix)

### MAJOR #5: Intermediate Reward Signals

**Problem**:
- Only final reward
- No signal for progress during trajectory

**Fix** (1 hour):
- Add +0.1 for syntax correctness
- Add proportional bonus for test improvement
- Bonus for attempting improvement

**Code**: See Critical #4 implementation above

---

### MAJOR #6: Weak State Design

**Problem**:
- Class-level globals (`_global_problem`)
- Not clean RL design
- Not scalable

**Fix** (1-2 hours):
- Migrate to per-episode state objects
- Use proper state management
- Clean up global variables

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Critical Fixes (Today - April 5)
- [ ] Fix #1: Set temperature=0.0 in inference.py (5 min)
- [ ] Fix #1: Add seed to inference.py (5 min)
- [ ] Fix #2: Add difficulty parameter to /reset (30 min)
- [ ] Fix #3: Verify baseline reproducibility (10 min)
- [ ] Test all three fixes work together (30 min)

**Time**: ~1.5 hours

### Phase 2: Single-Turn Fix (April 5-6)
- [ ] Update environment.py for multi-step (1.5 hours)
- [ ] Update models.py with attempt tracking (30 min)
- [ ] Add intermediate reward logic (30 min)
- [ ] Test with multiple /step calls (30 min)
- [ ] Verify done=true after 3 attempts (15 min)

**Time**: ~3.5 hours

### Phase 3: Verify & Deploy (April 6-7)
- [ ] Run local tests on all endpoints (30 min)
- [ ] Run inference.py 3+ times, verify identical scores (15 min)
- [ ] Test difficulty selection (15 min)
- [ ] Test multi-step workflow (15 min)
- [ ] Test reproducibility again (15 min)
- [ ] Update documentation (30 min)

**Time**: ~2 hours

### Phase 4: Deploy & Submit (April 7-8)
- [ ] Deploy to HuggingFace Spaces
- [ ] Run validator script
- [ ] Verify all checks pass
- [ ] Submit to hackathon portal

**Time**: ~1 hour

---

## 🎯 CURRENT vs FIXED STATE

### Current Issues:
```
Temperature:        0.7 (non-deterministic) → 0.0 (deterministic)
Task Selection:     Random only → Can select by difficulty
Baseline:           Non-reproducible → Reproducible
Episodes:           Single-turn → Multi-turn (3 attempts)
Rewards:            Final only → Intermediate + final
State:              Globals → Structured
```

### After Critical Fixes:
```
Compliance:         85% → 95%+
Determinism:        No → Yes
Reproducibility:    No → Yes
RL Design:          Weak → Strong
Scoring Risk:       High → Low
Disqualification:   Possible → Unlikely
```

---

## 📊 TIME ESTIMATE

| Task | Time | Priority |
|------|------|----------|
| Fix temperature=0.0 | 5 min | CRITICAL |
| Add seeds | 5 min | CRITICAL |
| Add difficulty API | 30 min | CRITICAL |
| Multi-step environment | 90 min | CRITICAL |
| Intermediate rewards | 30 min | MAJOR |
| Testing & verification | 90 min | CRITICAL |
| Deployment | 60 min | CRITICAL |
| **TOTAL** | **~310 min** | **~5.2 hours** |

**Feasible before April 8**: YES ✅

---

## ⚡ QUICK START (Next 30 Minutes)

1. **Fix #1: Determinism** (5 min)
   ```bash
   # Edit inference.py
   # Change: temperature=0.7 → temperature=0.0
   # Add: random.seed(42)
   ```

2. **Fix #3: Test Reproducibility** (10 min)
   ```bash
   python inference.py > /tmp/run1.txt
   python inference.py > /tmp/run2.txt
   diff /tmp/run1.txt /tmp/run2.txt
   # Should show no differences
   ```

3. **Fix #2: API Parameter** (15 min)
   ```bash
   # Edit server/app.py
   # Add difficulty parameter to reset()
   # Test: curl -X POST http://localhost:8000/reset?difficulty=easy
   ```

---

## ⚠️ WARNING

**DO NOT deploy to HF Spaces without these fixes.**

If you deploy current version:
- Judges will test reproducibility
- Scores will differ
- Automatic rejection
- Disqualification risk

**Must fix before deployment.**

---

## 📝 NEXT ACTION

1. **Read this document** (10 min) ✓
2. **Understand the issues** (15 min)
3. **Start with Fix #1** (5 min)
4. **Test reproducibility** (10 min)
5. **Then move to Fix #2** (30 min)
6. **Continue to Fix #4** (2 hours)

**Start NOW. Don't wait.**

---

**Document**: Critical Compliance Fixes Plan  
**Created**: April 5, 2026  
**Status**: URGENT - Action required immediately  
**Deadline**: April 8, 2026 (3 days)
