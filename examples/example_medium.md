# Example Medium Problem - Off-by-One Error

## Problem: off_by_one_001

**Difficulty**: Medium  
**Category**: off_by_one  

### Buggy Code
```python
def first_n_numbers(n):
    return list(range(1, n))
```

### Description
Function should return first N natural numbers (1 to N inclusive).

### What's Wrong
Classic off-by-one error. Python's `range(1, n)` returns numbers from 1 to n-1 (exclusive end).

### Fixed Code
```python
def first_n_numbers(n):
    return list(range(1, n + 1))  # Added +1 to include n
```

### Multi-Step Reward Shaping
Shows how agents learn iteratively with improvement bonuses.
