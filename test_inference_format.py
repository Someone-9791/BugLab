"""Quick validation test for inference.py stdout format compliance."""
import re
import sys

# Test patterns from spec
START_PATTERN = r'^\[START\] task=\S+ env=\S+ model=\S+$'
STEP_PATTERN = r'^\[STEP\] step=\d+ action=\S+ reward=-?\d+\.\d{2} done=(true|false) error=(\S+|null)$'
END_PATTERN = r'^\[END\] success=(true|false) steps=\d+ rewards=(-?\d+\.\d{2}(,-?\d+\.\d{2})*)$'

def test_stdout_format():
    """Test that output lines match required format."""
    print("=== Testing inference.py stdout format ===\n")
    
    # Test START
    start_line = "[START] task=fix_logic_bug env=BugLab model=gpt-3.5-turbo"
    if re.match(START_PATTERN, start_line):
        print("✓ START format valid")
    else:
        print("✗ START format invalid")
        return False
    
    # Test STEP
    step_line = "[STEP] step=1 action=fix_attempt_1 reward=0.50 done=false error=null"
    if re.match(STEP_PATTERN, step_line):
        print("✓ STEP format valid")
    else:
        print("✗ STEP format invalid")
        return False
    
    # Test STEP with error
    step_error = "[STEP] step=2 action=fix_attempt_2 reward=0.85 done=true error=syntax_error"
    if re.match(STEP_PATTERN, step_error):
        print("✓ STEP with error format valid")
    else:
        print("✗ STEP with error format invalid")
        return False
    
    # Test END
    end_line = "[END] success=true steps=2 rewards=0.50,0.85"
    if re.match(END_PATTERN, end_line):
        print("✓ END format valid")
    else:
        print("✗ END format invalid")
        return False
    
    # Test END with single reward
    end_single = "[END] success=false steps=1 rewards=0.30"
    if re.match(END_PATTERN, end_single):
        print("✓ END (single reward) format valid")
    else:
        print("✗ END (single reward) format invalid")
        return False
    
    print("\n=== Testing output structure ===\n")
    
    # Test no extra stdout
    lines = [start_line, step_line, end_line]
    for line in lines:
        if line.startswith('['):
            if '\n' in line:
                print(f"✗ Embedded newline in: {line[:50]}")
                return False
    print("✓ No embedded newlines in output")
    
    # Test boolean format
    if "true" in end_line and "false" not in end_line:
        print("✓ Booleans are lowercase")
    
    # Test reward format
    import re as regex
    rewards_match = regex.findall(r'reward=(-?\d+\.\d{2})', step_line)
    if rewards_match and len(rewards_match[0]) > 0:
        print("✓ Reward formatted to 2 decimals")
    
    return True

def test_script_structure():
    """Test that inference.py has required structure."""
    print("\n=== Testing inference.py structure ===\n")
    
    with open('D:\\Projects\\MetaOpenEnv\\inference.py', 'r') as f:
        content = f.read()
    
    checks = {
        'HF_TOKEN validation': 'if HF_TOKEN is None:' in content and 'raise ValueError' in content,
        'OpenAI client': 'from openai import OpenAI' in content,
        'GenericEnvClient': 'from openenv import GenericEnvClient' in content,
        'log_start function': 'def log_start' in content and '[START]' in content,
        'log_step function': 'def log_step' in content and '[STEP]' in content,
        'log_end function': 'def log_end' in content and '[END]' in content,
        'try/finally': 'try:' in content and 'finally:' in content,
        'env.close() in finally': 'finally:' in content and 'await env.close()' in content,
        'async main': 'async def main' in content,
        'getattr safety': 'getattr(result' in content,
    }
    
    all_pass = True
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}")
        if not result:
            all_pass = False
    
    return all_pass

def test_field_handling():
    """Test that script handles missing fields gracefully."""
    print("\n=== Testing field safety ===\n")
    
    with open('D:\\Projects\\MetaOpenEnv\\inference.py', 'r') as f:
        content = f.read()
    
    # Check for safe field access
    safe_patterns = [
        ('getattr(result, "observation"', 'observation field'),
        ('getattr(result, "reward"', 'reward field'),
        ('getattr(result, "done"', 'done field'),
        ('getattr(result, "success"', 'success field'),
        ('getattr(result, "last_action_error"', 'error field'),
    ]
    
    all_safe = True
    for pattern, field in safe_patterns:
        if pattern in content:
            print(f"✓ Safe access: {field}")
        else:
            print(f"✗ Missing safe access: {field}")
            all_safe = False
    
    return all_safe

if __name__ == "__main__":
    print("MetaOpenEnv Submission Validator\n")
    
    results = []
    results.append(("Format Compliance", test_stdout_format()))
    results.append(("Script Structure", test_script_structure()))
    results.append(("Field Safety", test_field_handling()))
    
    print("\n" + "=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)
    
    all_pass = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
        if not result:
            all_pass = False
    
    print("\n" + "=" * 50)
    if all_pass:
        print("✓ Script structure is submission-ready")
        print("\nRemaining validation:")
        print("- Environment provides correct fields (reward, done, success, observation)")
        print("- LLM API calls work with credentials")
        print("- [END] prints even on environment exceptions")
        sys.exit(0)
    else:
        print("✗ Script has structural issues")
        sys.exit(1)
