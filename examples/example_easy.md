# Example Easy Problem - Logic Error

## Problem: logic_001

**Difficulty**: Easy  
**Category**: logic_error  

### Buggy Code
```python
def find_max(a, b):
    if a < b:
        return a
    return b
```

### Description
Function should return the maximum of two numbers.

### Test Cases
```python
test_cases = [
    {"input": [5, 3], "expected": 5},
    {"input": [2, 8], "expected": 8},
    {"input": [7, 7], "expected": 7},
]
```

### What's Wrong
The comparison operator is incorrect. The function returns `a` when `a < b`, which gives us the minimum, not the maximum.

### Fixed Code
```python
def find_max(a, b):
    if a > b:  # Changed < to >
        return a
    return b
```

### Reward Breakdown
- **Test Score**: 3/3 tests pass = 1.0
- **Quality Score**: 
  - Syntax valid: +0.1
  - No unused vars: +0.1
  - Good style: +0.1
  - Low complexity: +0.1
  - Reasonable size: +0.1
  - No anti-patterns: +0.1
  - Total: 0.6
- **Final Reward**: 0.7 * 1.0 + 0.3 * 0.6 = 0.88
