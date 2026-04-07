# Code Quality Scoring System

## Overview

BugLab uses a **deterministic, objective code quality scoring system** based on static analysis. This ensures reproducible, consistent grading independent of subjective factors.

## The Six Quality Checks (6 × 16.7% = 100%)

Each check is worth up to 0.1 points (10% of total), allowing a maximum score of 1.0:

### 1. **Syntax Validity** (10%)
- **What it checks**: Code must be valid Python
- **Scoring**: 
  - ✅ Valid syntax: +0.1
  - ❌ Syntax error: 0.0 (entire submission fails)
- **How to improve**: Ensure no `SyntaxError` when running `python -m py_compile`

### 2. **Unused Variables** (10%)
- **What it checks**: No variables defined but never used
- **Scoring**:
  - ✅ No unused variables: +0.1
  - ⚠️ 1 unused variable: -0.05
  - ⚠️ 2+ unused variables: -0.10 (max penalty)
- **How to improve**: Remove unused variables or use `_` for intentionally ignored values

### 3. **PEP8 Style Compliance** (10%)
- **What it checks**: Code formatting and style
- **Scoring**:
  - ✅ No style issues: +0.1
  - ⚠️ 1-2 style issues: +0.05
  - ❌ 3+ style issues: 0.0
- **Common issues**:
  - Lines longer than 100 characters
  - Inconsistent indentation (must be multiples of 4 spaces)
- **How to improve**: 
  - Keep lines under 100 characters
  - Use 4-space indentation consistently
  - Run `black` or `flake8` to check compliance

### 4. **Cyclomatic Complexity** (10%)
- **What it checks**: Code branching/nesting complexity
- **Scoring**:
  - ✅ Low complexity (≤5 branches/function): +0.1
  - ⚠️ Moderate (5-10 branches): +0.05
  - ❌ High (>10 branches): 0.0
- **Branches counted**: `if`, `for`, `while`, `with` statements
- **How to improve**: 
  - Break complex logic into smaller functions
  - Use early returns to reduce nesting
  - Extract conditional logic into helper functions

### 5. **Function Size** (10%)
- **What it checks**: Functions should be reasonably short
- **Scoring**:
  - ✅ Well-sized (≤30 lines/function): +0.1
  - ⚠️ Somewhat large (30-50 lines): +0.05
  - ❌ Too large (>50 lines): 0.0
- **How to improve**:
  - Break large functions into smaller ones
  - Each function should do one thing well
  - Typical ideal: 10-30 lines per function

### 6. **No Anti-Patterns** (10%)
- **What it checks**: Dangerous or discouraged patterns
- **Scoring**:
  - ✅ No anti-patterns: +0.1
  - ⚠️ 1 anti-pattern: +0.05
  - ❌ 2+ anti-patterns: 0.0
- **Anti-patterns flagged**:
  - `import *` (use explicit imports)
  - `eval()` (security risk)
  - `exec()` (security risk)
  - `__del__()` (destructors with side effects)
- **How to improve**: 
  - Use explicit imports: `from module import name`
  - Use `ast.literal_eval()` instead of `eval()`
  - Avoid dynamic code execution

## How the Score is Calculated

```
Quality Score = (passed_checks × 0.1) - penalties
Final Score = min(1.0, max(0.0, Quality Score))
```

**Example**:
- Passed 5 checks: 5 × 0.1 = 0.5 (base)
- Has 1 unused variable: -0.05 (penalty)
- Final quality score: 0.45 (45%)

## How Quality Contributes to Overall Reward

The environment uses a **dual reward model**:

```
Overall Reward = (70% × Test Score) + (30% × Quality Score)
```

- **Test Score (70%)**: Automated tests passing
- **Quality Score (30%)**: Code quality metrics

**Example**:
- All tests pass: 1.0
- Code quality: 0.60
- Overall reward = 0.7(1.0) + 0.3(0.60) = 0.88

## Score Ranges and Meanings

| Score | Quality Level | Feedback |
|-------|---------------|----------|
| 0.90-1.00 | Excellent | ⭐ Code follows best practices |
| 0.70-0.89 | Good | 👍 Minor improvements needed |
| 0.50-0.69 | Fair | ⚠️ Several issues to address |
| 0.00-0.49 | Poor | 🔧 Significant improvements needed |

## Why Static Analysis?

We use objective AST-based analysis instead of LLM evaluation because:

1. **Reproducibility**: Same code always gets the same score
2. **Transparency**: Users understand exactly why their score is what it is
3. **Speed**: Instant feedback without API calls
4. **Fairness**: No bias from LLM mood or tokenization quirks
5. **Determinism**: Essential for ML training consistency

## Feedback Format

After each submission, you'll see:

```
## Code Quality Score: 60% (0.60/1.0)

### ✓ What's Good:
  - Code is syntactically valid
  - All variables are used
  - Functions are well-sized

### ✗ What Needs Improvement:
  - Code follows PEP8 but has 2 style issues
  - Code complexity is moderate

### How to Improve:
  1. Keep lines under 100 characters
  2. Break complex functions into smaller ones
```

## Why Code Quality Matters

- **Maintainability**: Clean code is easier to understand and modify
- **Reliability**: Code following conventions has fewer bugs
- **Efficiency**: Well-structured code often runs faster
- **Professional practice**: Industry standard in real-world development

## Next Steps

When you see a low quality score:

1. **Read the feedback**: Understand what checks failed
2. **Focus on improvements**: Follow the specific suggestions
3. **Test locally**: Use tools like `black` and `flake8`
4. **Resubmit**: Each submission gets a new quality analysis

Good luck!
