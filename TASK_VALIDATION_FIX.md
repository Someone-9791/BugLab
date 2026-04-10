# Task Validation Error - Fixed

## Problem
Validator was failing with: **"Not enough tasks with graders"**

Despite having 3 tasks defined in the codebase.

## Root Cause Analysis
The validator checks if task graders are **callable Python functions**.

Previously:
- Tasks were defined in `TASKS` dict with grader names (e.g., "test_logic_fix")
- But these grader functions did NOT exist in `server/grader.py`
- Validator couldn't verify the graders were callable

## Solution Implemented

### 1. Added Grader Functions (server/grader.py)
```python
def test_logic_fix(code: str, test_cases: list[dict]) -> float:
    """Grader for fix_logic_bug task"""
    score, _ = run_tests_sandboxed(code, test_cases, timeout_s=5.0, detailed=True)
    quality = analyze_code_quality(code)
    return 0.7 * score + 0.3 * quality

def test_algorithm_fix(code: str, test_cases: list[dict]) -> float:
    """Grader for fix_algorithm_bug task"""
    score, _ = run_tests_sandboxed(code, test_cases, timeout_s=5.0, detailed=True)
    quality = analyze_code_quality(code)
    return 0.7 * score + 0.3 * quality

def test_optimization(code: str, test_cases: list[dict]) -> float:
    """Grader for optimize_and_fix task"""
    score, _ = run_tests_sandboxed(code, test_cases, timeout_s=5.0, detailed=True)
    quality = analyze_code_quality(code)
    return 0.7 * score + 0.3 * quality
```

### 2. Added Graders Discovery Endpoint (server/app.py)
```python
@app.get("/graders")
async def list_graders():
    """List all available grader functions."""
    from server.grader import test_logic_fix, test_algorithm_fix, test_optimization
    graders = {
        "test_logic_fix": {"callable": True, ...},
        "test_algorithm_fix": {"callable": True, ...},
        "test_optimization": {"callable": True, ...}
    }
    return {"graders": graders, "total": 3}
```

### 3. Task-Grader Mapping
Each task in TASKS dict now maps to a callable grader:
- `fix_logic_bug` → `test_logic_fix` (callable, exists)
- `fix_algorithm_bug` → `test_algorithm_fix` (callable, exists)
- `optimize_and_fix` → `test_optimization` (callable, exists)

## Grader Implementation Details

All graders use the **70/30 split** scoring system:
- **70%**: Test pass rate (automated sandboxed execution)
- **30%**: Code quality (static analysis)

Final score = `0.7 * test_score + 0.3 * quality_score`

## Verification

```
[OK] test_logic_fix: callable
[OK] test_algorithm_fix: callable
[OK] test_optimization: callable
[OK] Each task maps to correct grader
[OK] Docker builds successfully
[OK] OpenEnv validation passes
```

## What Changed

**server/grader.py:**
- Added 3 grader functions
- Each function wraps test execution + quality analysis
- Returns normalized score [0.0, 1.0]

**server/app.py:**
- Added `/graders` endpoint for validator discovery
- Enables validator to confirm all graders are available and callable

## Expected Result
Validator should now:
1. Call `/tasks` endpoint and find 3 tasks
2. Call `/graders` endpoint and find 3 callable graders
3. Verify each task has a corresponding grader function
4. Pass Task Validation check

## Status
Ready for resubmission to validator.
