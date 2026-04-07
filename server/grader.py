"""
Grader module for BugLab.
Provides sandboxed code execution, LLM-based quality judging, and reward computation.
"""

import subprocess
import json
import tempfile
import os
import requests
from typing import Optional


# Environment configuration
HF_TOKEN = os.getenv("HF_TOKEN")
LLM_JUDGE_MODE = os.getenv("LLM_JUDGE_MODE", "api")
HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-7B-Instruct"

# LLM Judge prompt template
JUDGE_PROMPT = """You are a code quality judge. A student was given broken Python code and asked to fix it.

Original broken code:
```python
{buggy_code}
```

Student's fix:
```python
{fixed_code}
```

Rate the fix on a scale from 0.0 to 1.0 based on:
- Correctness (does it actually fix the bug?)
- Code quality (is it clean and readable?)
- Approach (is the fix minimal and appropriate?)

Respond ONLY with a JSON object like this: {{"score": 0.85, "reason": "brief explanation"}}
"""


def run_tests_sandboxed(code: str, test_cases: list[dict], timeout_s: float = 5.0, detailed: bool = False) -> float | tuple[float, list[dict]]:
    """
    Run code against test cases in isolated subprocess with timeout.
    
    Args:
        code: The Python code to test (should define a function named 'solution')
        test_cases: List of dicts with 'input' (list of args) and 'expected' (result)
        timeout_s: Timeout in seconds for test execution (default: 5.0)
        detailed: If True, return (score, test_details). If False, return just score.
    
    Returns:
        float: Pass rate from 0.0 to 1.0 (if detailed=False)
        tuple: (score, test_details) if detailed=True, where test_details is list of dicts
    
    Security:
        - Runs in subprocess with configurable timeout
        - Uses temporary file (not eval/exec)
        - Catches all exceptions
    """
    if not test_cases:
        if detailed:
            return 0.0, []
        return 0.0
    
    # Build the test script (Session 8: now returns detailed results)
    # The user's code should define a function - we'll try to call it
    # IMPORTANT: Use repr() for test_cases to preserve Python literals (True/False, not JSON true/false)
    test_script = f"""
import json
import sys

# User's code
{code}

# Test execution
results = []
detailed_results = []
test_cases = {repr(test_cases)}

# Try to find the function name from the code
# Common patterns: def func_name(...):
import re
func_match = re.search(r'def\\s+(\\w+)\\s*\\(', '''{code}''')
if func_match:
    func_name = func_match.group(1)
    solution = locals().get(func_name) or globals().get(func_name)
else:
    # Fallback: try 'solution' as default name
    solution = locals().get('solution') or globals().get('solution')

if not solution or not callable(solution):
    # If no callable found, all tests fail
    results = [False] * len(test_cases)
    for i, tc in enumerate(test_cases):
        detailed_results.append({{
            "input": tc['input'],
            "expected": tc['expected'],
            "actual": None,
            "status": "error",
            "error": "Function not found or not callable"
        }})
else:
    for i, tc in enumerate(test_cases):
        try:
            result = solution(*tc['input'])
            passed = result == tc['expected']
            results.append(passed)
            detailed_results.append({{
                "input": tc['input'],
                "expected": tc['expected'],
                "actual": result,
                "status": "pass" if passed else "fail",
                "error": None if passed else f"Expected {{tc['expected']}}, got {{result}}"
            }})
        except Exception as e:
            results.append(False)
            detailed_results.append({{
                "input": tc['input'],
                "expected": tc['expected'],
                "actual": None,
                "status": "error",
                "error": str(e)
            }})

# Output: JSON with both simple results and detailed results
output = {{
    "results": results,
    "detailed": detailed_results
}}
print(json.dumps(output))
"""
    
    tmp_path = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            tmp_path = f.name
        
        # Run in subprocess with timeout
        proc = subprocess.run(
            ['python3', tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout_s  # Use provided timeout
        )
        
        # Check if process succeeded
        if proc.returncode != 0:
            if detailed:
                return 0.0, []
            return 0.0
        
        # Parse results
        try:
            data = json.loads(proc.stdout.strip())
            
            # Session 8: Handle new detailed output format
            if isinstance(data, dict) and "results" in data:
                results = data["results"]
                detailed_results = data.get("detailed", [])
            else:
                # Fallback for old format (simple list)
                results = data if isinstance(data, list) else []
                detailed_results = []
            
            if not results:
                if detailed:
                    return 0.0, []
                return 0.0
            
            score = sum(results) / len(results)
            
            if detailed:
                return score, detailed_results
            return score
            
        except (json.JSONDecodeError, ValueError):
            if detailed:
                return 0.0, []
            return 0.0
    
    except subprocess.TimeoutExpired:
        # Code took too long (infinite loop?)
        if detailed:
            return 0.0, [{"status": "timeout", "error": "Code execution timeout"}]
        return 0.0
    
    except Exception as e:
        # Any other error
        if detailed:
            return 0.0, [{"status": "error", "error": str(e)}]
        return 0.0
    
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass


def call_llm_judge(buggy_code: str, fixed_code: str) -> float:
    """
    Call LLM judge to score code quality.
    
    Args:
        buggy_code: The original broken code
        fixed_code: The student's fix attempt
    
    Returns:
        float: Quality score from 0.0 to 1.0 (0.5 on any error)
    
    Notes:
        - Uses HuggingFace Inference API with Qwen2.5-Coder-7B
        - Returns 0.5 (neutral) on any error to avoid crashing environment
        - Parses JSON response for score
    """
    # If no token, return neutral score
    if not HF_TOKEN:
        return 0.5
    
    try:
        # Format prompt
        prompt = JUDGE_PROMPT.format(
            buggy_code=buggy_code.strip(),
            fixed_code=fixed_code.strip()
        )
        
        # Call HuggingFace Inference API
        response = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            },
            timeout=30
        )
        
        # Check response status
        if response.status_code != 200:
            return 0.5  # neutral fallback
        
        # Parse response
        response_data = response.json()
        
        # Handle different response formats
        if isinstance(response_data, list) and len(response_data) > 0:
            output = response_data[0].get("generated_text", "")
        elif isinstance(response_data, dict):
            output = response_data.get("generated_text", "")
        else:
            return 0.5
        
        # Extract JSON from response
        # Look for JSON object in the output
        start = output.find('{')
        end = output.rfind('}') + 1
        
        if start == -1 or end == 0:
            return 0.5
        
        json_str = output[start:end]
        data = json.loads(json_str)
        
        # Extract score
        score = float(data.get("score", 0.5))
        
        # Clamp to valid range [0, 1]
        return max(0.0, min(1.0, score))
    
    except requests.exceptions.Timeout:
        # API timeout
        return 0.5
    
    except requests.exceptions.RequestException:
        # Network error
        return 0.5
    
    except (json.JSONDecodeError, ValueError, KeyError):
        # JSON parsing error
        return 0.5
    
    except Exception:
        # Any other error - never crash the environment
        return 0.5


def analyze_code_quality(fixed_code: str) -> tuple[float, dict]:
    """
    Analyze code quality using static analysis and return detailed breakdown.
    
    Replaces subjective LLM scoring with objective AST-based checks.
    
    Checks (each worth up to 0.1):
    - Syntax valid (+0.1)
    - No unused variables (+0.1)
    - PEP8 style compliance (+0.1)
    - Low cyclomatic complexity (+0.1)
    - Function length reasonable (+0.1)
    - No anti-patterns (+0.1)
    
    Args:
        fixed_code: The Python code to analyze
    
    Returns:
        tuple: (quality_score, detailed_breakdown)
        - quality_score: float from 0.0 to 1.0
        - detailed_breakdown: dict with detailed feedback
    """
    import ast
    
    score = 0.0
    penalties = 0.0
    feedback = {
        "checks": {},
        "passed": [],
        "failed": [],
        "improvements": []
    }
    
    try:
        # 1. Syntax validation (+0.1)
        tree = ast.parse(fixed_code)
        score += 0.1
        feedback["checks"]["syntax"] = {"score": 0.1, "status": "Valid Python syntax"}
        feedback["passed"].append("Code is syntactically valid")
    except SyntaxError as e:
        feedback["checks"]["syntax"] = {"score": 0.0, "status": "Syntax error"}
        feedback["failed"].append(f"Syntax Error: {str(e)}")
        return 0.0, feedback
    
    try:
        # 2. Unused variables (-0.05 each if found)
        defined_vars = set()
        used_vars = set()
        
        class VarVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_vars.add(target.id)
                self.generic_visit(node)
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
                self.generic_visit(node)
            
            def visit_For(self, node):
                if isinstance(node.target, ast.Name):
                    defined_vars.add(node.target.id)
                self.generic_visit(node)
        
        VarVisitor().visit(tree)
        unused = defined_vars - used_vars - {'_'}
        if not unused:
            score += 0.1
            feedback["checks"]["unused_vars"] = {"score": 0.1, "status": "No unused variables"}
            feedback["passed"].append("All variables are used")
        else:
            penalty = 0.05 * min(len(unused), 2)
            penalties += penalty
            feedback["checks"]["unused_vars"] = {"score": -penalty, "status": f"Found {len(unused)} unused variable(s): {', '.join(unused)}"}
            feedback["failed"].append(f"Unused variables: {', '.join(unused)}")
            feedback["improvements"].append(f"Remove unused variables: {', '.join(unused)}")
    
    except Exception as e:
        feedback["checks"]["unused_vars"] = {"score": 0.0, "status": "Could not analyze"}
        pass
    
    try:
        # 3. PEP8 style check (simplified)
        lines = fixed_code.split('\n')
        style_issues = []
        
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                style_issues.append(f"Line {i}: too long ({len(line)} chars, max 100)")
            if line and line[0] == ' ' and not (len(line) - len(line.lstrip())) % 4 == 0:
                style_issues.append(f"Line {i}: inconsistent indentation")
        
        if not style_issues:
            score += 0.1
            feedback["checks"]["style"] = {"score": 0.1, "status": "Good PEP8 compliance"}
            feedback["passed"].append("Code follows PEP8 style guidelines")
        elif len(style_issues) <= 2:
            score += 0.05
            feedback["checks"]["style"] = {"score": 0.05, "status": f"Minor style issues ({len(style_issues)})"}
            feedback["failed"].append(f"Style issues: {style_issues[0]}" + (f" and {len(style_issues)-1} more" if len(style_issues) > 1 else ""))
            feedback["improvements"].append("Fix line length (keep under 100 chars) and indentation (use 4 spaces)")
        else:
            feedback["checks"]["style"] = {"score": 0.0, "status": f"Multiple style issues ({len(style_issues)})"}
            feedback["failed"].append(f"{len(style_issues)} style issues found")
            feedback["improvements"].append(f"Fix {len(style_issues)} style issues: ensure proper indentation and line length")
    
    except Exception:
        pass
    
    try:
        # 4. Cyclomatic complexity
        branch_count = sum(
            1 for node in ast.walk(tree)
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With))
        )
        
        func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        if func_count == 0:
            func_count = 1
        
        avg_complexity = branch_count / func_count
        if avg_complexity <= 5:
            score += 0.1
            feedback["checks"]["complexity"] = {"score": 0.1, "status": f"Good complexity ({avg_complexity:.1f})"}
            feedback["passed"].append(f"Code complexity is reasonable (avg {avg_complexity:.1f} branches per function)")
        elif avg_complexity <= 10:
            score += 0.05
            feedback["checks"]["complexity"] = {"score": 0.05, "status": f"Moderate complexity ({avg_complexity:.1f})"}
            feedback["failed"].append(f"Code complexity is moderate (avg {avg_complexity:.1f} branches per function)")
            feedback["improvements"].append(f"Consider breaking down complex logic into smaller functions (current avg: {avg_complexity:.1f} branches)")
        else:
            feedback["checks"]["complexity"] = {"score": 0.0, "status": f"High complexity ({avg_complexity:.1f})"}
            feedback["failed"].append(f"Code is too complex (avg {avg_complexity:.1f} branches per function)")
            feedback["improvements"].append(f"Reduce code complexity by breaking into smaller functions (target: <5 branches per function)")
    
    except Exception:
        pass
    
    try:
        # 5. Function size
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        if not functions:
            total_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            if total_lines <= 20:
                score += 0.1
                feedback["checks"]["function_size"] = {"score": 0.1, "status": f"Good function size ({total_lines} lines)"}
                feedback["passed"].append(f"Function is concise ({total_lines} lines)")
            else:
                feedback["checks"]["function_size"] = {"score": 0.0, "status": f"Function is long ({total_lines} lines)"}
                feedback["failed"].append(f"Function is long ({total_lines} lines, recommended <20)")
                feedback["improvements"].append(f"Break down into smaller functions (current: {total_lines} lines, target: <20)")
        else:
            total_lines = len(lines)
            avg_size = total_lines / len(functions)
            if avg_size <= 30:
                score += 0.1
                feedback["checks"]["function_size"] = {"score": 0.1, "status": f"Good average function size ({avg_size:.0f} lines)"}
                feedback["passed"].append(f"Functions are well-sized (avg {avg_size:.0f} lines per function)")
            elif avg_size <= 50:
                score += 0.05
                feedback["checks"]["function_size"] = {"score": 0.05, "status": f"Functions could be smaller ({avg_size:.0f} lines avg)"}
                feedback["failed"].append(f"Functions are somewhat long (avg {avg_size:.0f} lines per function)")
                feedback["improvements"].append(f"Consider splitting large functions (current avg: {avg_size:.0f} lines, target: <30)")
            else:
                feedback["checks"]["function_size"] = {"score": 0.0, "status": f"Functions too large ({avg_size:.0f} lines avg)"}
                feedback["failed"].append(f"Functions are too large (avg {avg_size:.0f} lines per function)")
                feedback["improvements"].append(f"Break into smaller functions (current avg: {avg_size:.0f} lines, target: <30)")
    
    except Exception:
        pass
    
    try:
        # 6. No anti-patterns
        code_lower = fixed_code.lower()
        anti_patterns = []
        
        if 'import *' in code_lower:
            anti_patterns.append("'import *' (use explicit imports)")
        if 'eval(' in fixed_code:
            anti_patterns.append("eval() (security risk)")
        if 'exec(' in fixed_code:
            anti_patterns.append("exec() (security risk)")
        if '__del__' in code_lower:
            anti_patterns.append("__del__() (destructors)")
        
        if not anti_patterns:
            score += 0.1
            feedback["checks"]["anti_patterns"] = {"score": 0.1, "status": "No dangerous patterns"}
            feedback["passed"].append("No dangerous or discouraged patterns detected")
        elif len(anti_patterns) == 1:
            score += 0.05
            feedback["checks"]["anti_patterns"] = {"score": 0.05, "status": f"Found pattern: {anti_patterns[0]}"}
            feedback["failed"].append(f"Discouraged pattern: {anti_patterns[0]}")
            feedback["improvements"].append(f"Avoid {anti_patterns[0]} for better code safety")
        else:
            feedback["checks"]["anti_patterns"] = {"score": 0.0, "status": f"Found {len(anti_patterns)} patterns"}
            feedback["failed"].append(f"Found {len(anti_patterns)} discouraged patterns")
            feedback["improvements"].append(f"Remove dangerous patterns: {', '.join(anti_patterns)}")
    
    except Exception:
        pass
    
    # Normalize score: max possible is 6 checks × 0.1 = 0.6
    # Normalize to 0-1 range
    MAX_POSSIBLE = 0.6
    raw_score = max(0.0, score - penalties)
    final_score = raw_score / MAX_POSSIBLE if MAX_POSSIBLE > 0 else 0.0
    final_score = min(1.0, final_score)  # Clamp to [0, 1]
    
    # Add transparency: show score calculation
    check_scores = [c.get("score", 0) for c in feedback["checks"].values()]
    total_checks = len(feedback["checks"])
    passed_checks = sum(1 for c in feedback["checks"].values() if c.get("score") == 0.1)
    partial_checks = sum(1 for c in feedback["checks"].values() if 0 < c.get("score", 0) < 0.1)
    failed_checks = sum(1 for c in feedback["checks"].values() if c.get("score", 0) <= 0)
    
    feedback["summary"] = {
        "score": final_score,
        "max_score": 1.0,
        "percentage": int(final_score * 100),
        "breakdown": {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "partial_checks": partial_checks,
            "failed_checks": failed_checks,
            "raw_score": raw_score,
            "max_possible": MAX_POSSIBLE,
            "base_score": score,
            "penalties": penalties,
            "normalized_score": final_score
        }
    }
    
    return final_score, feedback


def humanize_quality_feedback(quality_feedback: dict) -> str:
    """
    Convert quality feedback dict into a human-readable markdown explanation.
    
    Args:
        quality_feedback: Dict from analyze_code_quality() with checks and improvements
    
    Returns:
        str: Markdown-formatted explanation suitable for UI display
    """
    if not quality_feedback:
        return "No quality feedback available"
    
    summary = quality_feedback.get("summary", {})
    score = summary.get("score", 0.0)
    percentage = summary.get("percentage", 0)
    
    lines = [
        f"## Code Quality Score: {percentage}% ({score:.2f}/1.0)",
        ""
    ]
    
    # Add score calculation transparency
    breakdown = summary.get("breakdown", {})
    if breakdown:
        lines.append("### How This Score Was Calculated:")
        base = breakdown.get("base_score", 0)
        penalties = breakdown.get("penalties", 0)
        lines.append(f"  - Base score from checks: {base:.2f}")
        if penalties > 0:
            lines.append(f"  - Penalties applied: -{penalties:.2f}")
        lines.append(f"  - **Final score: {score:.2f}** ← {percentage}%")
        lines.append("")
        
        # Show check summary
        passed_count = breakdown.get("passed_checks", 0)
        partial_count = breakdown.get("partial_checks", 0)
        failed_count = breakdown.get("failed_checks", 0)
        total_count = breakdown.get("total_checks", 0)
        
        lines.append(f"  - {passed_count}/{total_count} checks fully passed (10% each)")
        if partial_count > 0:
            lines.append(f"  - {partial_count}/{total_count} checks partially passed (5% each)")
        if failed_count > 0:
            lines.append(f"  - {failed_count}/{total_count} checks failed (0%)")
        lines.append("")
    
    passed = quality_feedback.get("passed", [])
    if passed:
        lines.append("### ✓ What's Good:")
        for item in passed:
            lines.append(f"  - {item}")
        lines.append("")
    
    failed = quality_feedback.get("failed", [])
    if failed:
        lines.append("### ✗ What Needs Improvement:")
        for item in failed:
            lines.append(f"  - {item}")
        lines.append("")
    
    improvements = quality_feedback.get("improvements", [])
    if improvements:
        lines.append("### How to Improve:")
        for idx, item in enumerate(improvements, 1):
            lines.append(f"  {idx}. {item}")
        lines.append("")
    
    checks = quality_feedback.get("checks", {})
    if checks:
        lines.append("### Detailed Breakdown (Each Check Worth 10% Max):")
        for check_name, check_info in checks.items():
            status = check_info.get("status", "Unknown")
            score_val = check_info.get("score", 0)
            score_pct = int(score_val * 100)
            check_title = check_name.replace('_', ' ').title()
            lines.append(f"  - **{check_title}** ({score_pct}%): {status}")
        lines.append("")
    
    lines.append("### Scoring Breakdown (6 checks):")
    lines.append("  - **Syntax** (10%): Valid Python syntax")
    lines.append("  - **Variables** (10%): No unused variables")
    lines.append("  - **Style** (10%): PEP8 compliance (lines <100 chars, proper indentation)")
    lines.append("  - **Complexity** (10%): Reasonable branching (<5 branches per function)")
    lines.append("  - **Function Size** (10%): Functions <=30 lines")
    lines.append("  - **Patterns** (10%): No dangerous patterns (eval, exec, import *, __del__)")
    lines.append("")
    
    if score >= 0.9:
        lines.append("**Result:** Excellent! Your code follows best practices.")
    elif score >= 0.7:
        lines.append("**Result:** Good! Consider the improvements above for a higher score.")
    elif score >= 0.5:
        lines.append("**Result:** Your code needs improvements. Address the issues above.")
    else:
        lines.append("**Result:** Your code needs significant work. Focus on the suggestions.")
    
    return "\n".join(lines)


def compute_reward(test_score: float, llm_score: float = None) -> float:
    """
    Compute final reward from dual signals (Session 8: updated to 70/30 split).
    
    Args:
        test_score: Automated test pass rate (0.0-1.0)
        llm_score: Deprecated. Kept for backward compatibility but ignored.
    
    Returns:
        float: Weighted reward (0.7 * test + 0.3 * quality)
    
    Formula (Session 8):
        70% weight on test correctness (objective - automated tests)
        30% weight on code quality (objective - static analysis)
    
    Note:
        llm_score parameter is deprecated and ignored.
        Quality is now computed via analyze_code_quality() instead.
    """
    # Note: This function signature is now called with just test_score
    # in the environment. The formula now uses static analysis instead of LLM.
    # Return test_score only - quality is handled in environment.step()
    return test_score
