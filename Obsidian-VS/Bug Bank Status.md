# Bug Bank Status

> Dataset statistics and validation
> Source: `/home/someone/python_debug_env/bug_bank.py`

---

## 📊 Overview

**Total Problems:** 30  
**File Size:** 611 lines  
**Status:** ✅ Complete and validated (April 2, 2026)

---

## 📈 Category Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| Logic Errors | 4 | 13.3% |
| Off-by-One | 4 | 13.3% |
| Wrong Return | 4 | 13.3% |
| Missing Edge Cases | 4 | 13.3% |
| Type Errors | 4 | 13.3% |
| Recursion Errors | 3 | 10.0% |
| Loop Errors | 4 | 13.3% |
| Variable Shadowing | 3 | 10.0% |

**Total:** 8 categories, well-balanced distribution

---

## 📊 Difficulty Distribution

| Difficulty | Count | Percentage |
|------------|-------|------------|
| Easy | 9 | 30.0% |
| Medium | 15 | 50.0% |
| Hard | 6 | 20.0% |

**Pyramid structure:** Good progression from easy to hard

---

## 🧪 Test Coverage

- **Total Test Cases:** ~90 (3+ per problem)
- **Test Types:** Input/output pairs with expected values
- **Edge Cases:** Included in most problems

**Sample Test Case Structure:**
```python
"test_cases": [
    {"input": [5, 3], "expected": 5},
    {"input": [2, 8], "expected": 8},
    {"input": [7, 7], "expected": 7},
]
```

---

## 📋 Problem Structure

Each problem contains:
- ✅ `id` - Unique identifier (e.g., "logic_001")
- ✅ `difficulty` - "easy", "medium", or "hard"
- ✅ `category` - Bug type classification
- ✅ `description` - Human-readable explanation
- ✅ `buggy_code` - The broken code
- ✅ `fixed_code` - The correct solution
- ✅ `test_cases` - List of input/output pairs

---

## 🎯 Category Examples

### Logic Errors (4 problems)
**Example:** `logic_001`
```python
# Buggy: Returns min instead of max
def find_max(a, b):
    if a < b:  # Wrong comparison
        return a
    return b

# Fixed:
def find_max(a, b):
    if a > b:
        return a
    return b
```

### Off-by-One (4 problems)
**Example:** `off_by_one_001`
```python
# Buggy: Missing last number
def first_n_numbers(n):
    return list(range(1, n))  # Should be n+1

# Fixed:
def first_n_numbers(n):
    return list(range(1, n + 1))
```

### Wrong Return (4 problems)
**Example:** Returning wrong variable after computation

### Missing Edge Cases (4 problems)
**Example:** No null/empty list checks

### Type Errors (4 problems)
**Example:** String concatenation without conversion

### Recursion Errors (3 problems)
**Example:** Missing base case causing infinite recursion

### Loop Errors (4 problems)
**Example:** Early break, wrong loop variable

### Variable Shadowing (3 problems)
**Example:** Loop variable overwrites accumulator

---

## ✅ Validation Checklist

- [x] All 30 problems have required fields
- [x] All `buggy_code` contains actual bugs
- [x] All `fixed_code` resolves the bug
- [x] All test cases have `input` and `expected`
- [x] Categories are balanced (3-4 per category)
- [x] Difficulties span easy/medium/hard
- [x] No duplicate problem IDs
- [x] Import tested successfully
- [x] Python syntax valid in all code snippets

---

## 🔍 Quality Metrics

**Diversity:** ✅ 8 distinct bug types  
**Complexity:** ✅ Progressive difficulty curve  
**Coverage:** ✅ 3+ tests per problem  
**Realism:** ✅ Common real-world bugs  
**Clarity:** ✅ Clear descriptions for each

---

## 🚀 Usage in Environment

Problems are loaded via:
```python
from bug_bank import PROBLEMS

# In environment.reset():
self.current_problem = random.choice(PROBLEMS)
```

Agent receives:
- `problem_id`
- `buggy_code`
- `description`
- `test_cases`
- `difficulty`

Grader uses:
- `test_cases` for automated testing
- `fixed_code` as reference (not shown to agent)

---

*Back to [[PythonDebugEnv Project Hub]]*
