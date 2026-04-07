# Scoring Formulas (Corrected)

## Quality Score Calculation

### Step 1: Raw Score Calculation
Each of 6 checks is scored:
- **Syntax Check**: 0 (fail) or 0.1 (pass)
- **Unused Variables**: 0 or 0.1
- **Code Style**: 0 or 0.1  
- **Complexity**: 0 or 0.1
- **Function Size**: 0 or 0.1
- **Anti-patterns**: 0 or 0.1

```
raw_score = sum of individual check scores
range: [0.0, 0.6]
```

### Step 2: Apply Penalties
For each issue found:
- Syntax error: -0.1 (critical)
- Unused variable: -0.05 each
- Bad naming: -0.02 each
- Other issues: -0.01 to -0.05

```
penalized_score = max(0.0, raw_score - penalties)
```

### Step 3: Normalize to [0, 1]
⚠️ **CRITICAL FIX**: This was the bug!

```
MAX_POSSIBLE = 0.6  (6 checks × 0.1)
final_score = penalized_score / MAX_POSSIBLE
final_score = min(1.0, final_score)  # Clamp just in case
```

### Examples

| Checks Passed | Raw Score | After Normalize | Percentage |
|--------------|-----------|-----------------|-----------|
| 0/6 (all fail) | 0.0 | 0.0 | 0% |
| 2/6 | 0.2 | 0.333 | 33% |
| 3/6 | 0.3 | 0.5 | 50% |
| 4/6 | 0.4 | 0.667 | 67% |
| 5/6 | 0.5 | 0.833 | 83% |
| 6/6 | 0.6 | 1.0 | 100% ✓ |

---

## Overall Reward Calculation

### Step 1: Test Score + Quality Score
```
test_score ∈ [0, 1]     (from pytest)
quality_score ∈ [0, 1]  (normalized above)
```

### Step 2: Weighted Combination
```
base_reward = (0.7 × test_score) + (0.3 × quality_score)
range: [0, 1.0]
```

### Step 3: Improvement Bonus
⚠️ **CRITICAL FIX**: This was also the bug!

```
improvement = base_reward - previous_score
improvement_bonus = 0.0

if improvement > 0.0:
    improvement_bonus = improvement × 0.5    # 50% of improvement
    if improvement > 0.1:
        improvement_bonus += 0.1              # +10% bonus if major improvement
```

Max improvement_bonus ≈ 0.15 (when perfect improvement from 0 to 1.0)

### Step 4: Final Reward (Clamped)
```
reward = min(1.0, base_reward + improvement_bonus)
final_reward ∈ [0, 1]  (always!)
```

### Examples

| Test | Quality | Base | Improvement | Bonus | Total | Clamped |
|------|---------|------|-------------|-------|-------|---------|
| 1.0 | 1.0 | 1.0 | +1.0 | 0.6 | 1.6 | **1.0** ✓ |
| 0.8 | 0.9 | 0.84 | +0.54 | 0.37 | 1.21 | **1.0** ✓ |
| 0.5 | 0.5 | 0.5 | +0.5 | 0.35 | 0.85 | **0.85** ✓ |
| 0.2 | 0.3 | 0.24 | +0.24 | 0.12 | 0.36 | **0.36** ✓ |
| 0 | 0 | 0 | 0 | 0 | 0 | **0** ✓ |

---

## Fixed Defects

### Defect 1: Quality Score Not Normalized ✅ FIXED
- **Before**: Returned 0-0.6 directly (60% max)
- **After**: Normalized by dividing by 0.6 → 0-1.0
- **Impact**: 6/6 checks now correctly shows 100%

### Defect 2: Reward Not Clamped ✅ FIXED
- **Before**: Could reach 1.5+ (150%+!)
- **After**: Clamped to max 1.0
- **Impact**: No more impossible rewards >100%

---

## Code Location

**Quality Score Normalization**:
- File: `server/grader.py`
- Lines: 499-530
- Function: `analyze_code_quality()`

**Reward Calculation**:
- File: `server/environment.py`
- Lines: 233-250
- Method: `OpenEnvDebugCompilationTask.step_env()`

---

## Verification

All calculations now satisfy:
✅ Quality score ∈ [0, 1]  
✅ Test score ∈ [0, 1]  
✅ Final reward ∈ [0, 1]  
✅ No impossible values (e.g., no 142%)  
✅ All checks properly weighted  
✅ Penalties properly applied  
