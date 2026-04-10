#!/usr/bin/env python
"""
Windows-Compatible OpenEnv Submission Validator (Enhanced)
Converts bash validate-submission script to Python for Windows

Performs 4 validation checks:
1. Python syntax check (inference.py)
2. Docker build
3. OpenEnv spec validation (YAML + imports)
4. Inference execution test
"""

import subprocess
import sys
import os
import json
import time
import yaml
from pathlib import Path
from datetime import datetime

DOCKER_BUILD_TIMEOUT = 600


def log(message):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def pass_check(message):
    """Log a passing check."""
    log(f"PASSED -- {message}")


def fail_check(message):
    """Log a failing check."""
    log(f"FAILED -- {message}")


def hint(message):
    """Log a hint for fixing issues."""
    print(f"  Hint: {message}")


def section_header(text):
    """Print a section header."""
    width = 80
    print("\n" + "=" * width)
    print(f"  {text}".center(width))
    print("=" * width + "\n")


def validate_openenv_yaml(repo_dir):
    """Validate openenv.yaml manually."""
    yaml_path = os.path.join(repo_dir, "openenv.yaml")
    
    if not os.path.exists(yaml_path):
        fail_check("openenv.yaml not found")
        return False
    
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        required_fields = ['name', 'entry_point', 'action_type', 'observation_type', 'state_type']
        missing = [f for f in required_fields if f not in config]
        
        if missing:
            fail_check(f"openenv.yaml missing fields: {missing}")
            return False
        
        # Validate types can be imported
        action_type = config.get('action_type', '')
        observation_type = config.get('observation_type', '')
        state_type = config.get('state_type', '')
        
        try:
            # Test imports
            import models
            if hasattr(models, 'DebugAction') and hasattr(models, 'DebugObservation') and hasattr(models, 'DebugState'):
                log(f"  Models validated: {action_type}, {observation_type}, {state_type}")
                return True
            else:
                fail_check(f"Models not properly exported from models.py")
                return False
        except ImportError as e:
            fail_check(f"Cannot import models: {e}")
            return False
            
    except yaml.YAMLError as e:
        fail_check(f"openenv.yaml parsing error: {e}")
        return False
    except Exception as e:
        fail_check(f"Error validating openenv.yaml: {e}")
        return False


def main():
    """Run all validation checks."""
    
    section_header("OpenEnv Submission Validator")
    
    repo_dir = os.path.abspath(".")
    log(f"Repo:     {repo_dir}")
    log(f"Timestamp: {datetime.now()}")
    print()
    
    passed = 0
    total = 4
    
    # Check 1: Python Syntax
    log("Check 1/4: Python Syntax...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "inference.py"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo_dir
        )
        if result.returncode == 0:
            pass_check("inference.py has valid Python syntax")
            passed += 1
        else:
            fail_check("inference.py has syntax errors")
            print(result.stderr)
            return 1
    except Exception as e:
        fail_check(f"Syntax check failed: {e}")
        return 1
    
    # Check 2: Docker Build
    log("Check 2/4: Docker Build...")
    
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError):
        fail_check("docker command not found")
        hint("Install Docker: https://docs.docker.com/get-docker/")
        return 1
    
    # Find Dockerfile
    dockerfile_path = None
    if os.path.isfile(os.path.join(repo_dir, "Dockerfile")):
        dockerfile_path = repo_dir
    elif os.path.isfile(os.path.join(repo_dir, "server", "Dockerfile")):
        dockerfile_path = os.path.join(repo_dir, "server")
    else:
        fail_check("No Dockerfile found in repo root or server/ directory")
        return 1
    
    log(f"  Found Dockerfile in {dockerfile_path}")
    
    # Build docker image
    try:
        start_time = time.time()
        result = subprocess.run(
            ["docker", "build", dockerfile_path, "--quiet"],
            capture_output=True,
            text=True,
            timeout=DOCKER_BUILD_TIMEOUT,
            cwd=repo_dir
        )
        build_time = time.time() - start_time
        
        if result.returncode == 0:
            pass_check(f"Docker build succeeded (time: {build_time:.1f}s)")
            passed += 1
        else:
            fail_check(f"Docker build failed (timeout={DOCKER_BUILD_TIMEOUT}s)")
            error_lines = result.stderr.split('\n')
            for line in error_lines[-20:]:
                if line.strip():
                    print(f"  {line}")
            return 1
    except subprocess.TimeoutExpired:
        fail_check(f"Docker build timed out ({DOCKER_BUILD_TIMEOUT}s)")
        return 1
    except Exception as e:
        fail_check(f"Docker build error: {e}")
        return 1
    
    # Check 3: OpenEnv Specification
    log("Check 3/4: OpenEnv Specification...")
    
    if validate_openenv_yaml(repo_dir):
        pass_check("openenv.yaml valid and models properly exported")
        passed += 1
    else:
        return 1
    
    # Check 4: Inference Execution
    log("Check 4/4: Inference Execution...")
    
    try:
        test_env = os.environ.copy()
        test_env['HF_TOKEN'] = 'hf-test-token-validation'
        test_env['API_BASE_URL'] = 'https://api.openai.com/v1'
        test_env['MODEL_NAME'] = 'gpt-3.5-turbo'
        
        result = subprocess.run(
            [sys.executable, "inference.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=repo_dir,
            env=test_env
        )
        
        output_lines = result.stdout.strip().split('\n')
        has_start = any(line.startswith('[START]') for line in output_lines)
        has_end = any(line.startswith('[END]') for line in output_lines)
        has_score = any('score=' in line for line in output_lines if line.startswith('[END]'))
        
        if has_start and has_end and has_score:
            pass_check("inference.py executed successfully with correct format")
            log(f"  Output sample: {output_lines[0]}")
            passed += 1
        else:
            fail_check("Output format incomplete")
            log(f"  Has [START]: {has_start}")
            log(f"  Has [END]: {has_end}")
            log(f"  Has score: {has_score}")
            print(f"  Output:\n{result.stdout}")
            return 1
            
    except subprocess.TimeoutExpired:
        fail_check("inference.py timed out (> 30 seconds)")
        return 1
    except Exception as e:
        fail_check(f"Execution error: {e}")
        return 1
    
    # Summary
    section_header("Validation Results")
    
    if passed == total:
        print(f"SUCCESS: All {total}/{total} checks passed!")
        print("\nYour submission is ready for validator.\n")
        print("Next steps:")
        print("  1. Wait for HF Space Docker build (2-5 min)")
        print("  2. Submit with:")
        print("     - Repository: https://github.com/Someone-9791/BugLab")
        print("     - Space: https://huggingface.co/spaces/Someone5249/BugLab")
        print()
        return 0
    else:
        print(f"INCOMPLETE: {passed}/{total} checks passed")
        print("Fix failures above before submitting.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
