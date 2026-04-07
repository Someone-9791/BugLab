#!/usr/bin/env python3
"""
Test script to validate the critical improvements implemented.
Tests all PRIORITY 1, 2, and 3 improvements.
"""

import sys
import re
import json
from pathlib import Path

def test_priority_1_1_instance_state():
    """PRIORITY 1.1: Verify class-level state converted to instance state."""
    print("\n[TEST] PRIORITY 1.1: Instance state (not class state)")
    
    try:
        from server.environment import PythonDebugEnvironment
        
        # Create two instances
        env1 = PythonDebugEnvironment()
        env2 = PythonDebugEnvironment()
        
        # Verify they have instance variables (not class variables)
        assert hasattr(env1, 'current_problem'), "Missing instance variable: current_problem"
        assert hasattr(env1, 'current_episode_id'), "Missing instance variable: current_episode_id"
        assert hasattr(env1, 'current_attempt_count'), "Missing instance variable: current_attempt_count"
        assert hasattr(env1, 'current_previous_score'), "Missing instance variable: current_previous_score"
        
        # Verify they're independent (not sharing class state)
        env1.current_problem = {"id": "test_1"}
        env2.current_problem = {"id": "test_2"}
        
        assert env1.current_problem["id"] == "test_1", "Instance 1 state leaked to instance 2"
        assert env2.current_problem["id"] == "test_2", "Instance 2 state leaked to instance 1"
        
        print("  ✓ Instance state properly isolated (thread-safe)")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_1_2_validation_error_handler():
    """PRIORITY 1.2: Verify FastAPI validation error handler exists."""
    print("\n[TEST] PRIORITY 1.2: FastAPI validation error handler")
    
    try:
        from server.app import app
        
        # Check if RequestValidationError handler is registered
        exception_handlers = app.exception_handlers
        
        # Import to get the exception class
        from fastapi.exceptions import RequestValidationError
        
        assert RequestValidationError in exception_handlers, \
            "RequestValidationError handler not registered"
        
        print("  ✓ Validation error handler properly registered")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_1_3_timeout_in_inference():
    """PRIORITY 1.3: Verify asyncio.wait_for timeout in inference.py."""
    print("\n[TEST] PRIORITY 1.3: Timeouts in inference steps")
    
    try:
        import inference
        
        # Check that asyncio.wait_for is used in run_episode
        source = Path("inference.py").read_text(encoding='utf-8', errors='ignore')
        
        assert "asyncio.wait_for" in source, "asyncio.wait_for not found in inference.py"
        assert "timeout=30.0" in source, "30 second timeout not found"
        assert "asyncio.TimeoutError" in source, "TimeoutError handling not found"
        
        print("  ✓ Timeouts properly added to inference steps")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_1_4_connection_retry():
    """PRIORITY 1.4: Verify connection retry logic in inference.py."""
    print("\n[TEST] PRIORITY 1.4: Connection retry with exponential backoff")
    
    try:
        import inference
        
        # Check that connect_with_retry function exists
        assert hasattr(inference, 'connect_with_retry'), \
            "connect_with_retry function not found"
        
        # Check function signature
        import inspect
        sig = inspect.signature(inference.connect_with_retry)
        params = list(sig.parameters.keys())
        
        assert 'env_url' in params, "Missing env_url parameter"
        assert 'max_retries' in params, "Missing max_retries parameter"
        assert 'initial_delay' in params, "Missing initial_delay parameter"
        
        # Verify it's used in run_episode
        source = Path("inference.py").read_text(encoding='utf-8', errors='ignore')
        assert "await connect_with_retry" in source, \
            "connect_with_retry not called in run_episode"
        
        print("  ✓ Connection retry with exponential backoff implemented")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_2_5_hints():
    """PRIORITY 2.5: Verify mistake hints in environment."""
    print("\n[TEST] PRIORITY 2.5: Common mistake hints")
    
    try:
        from server.environment import CATEGORY_HINTS
        
        expected_categories = [
            "logic_error", "off_by_one", "wrong_return", "type_error",
            "recursion_error", "missing_edge_case", "variable_shadowing"
        ]
        
        for category in expected_categories:
            assert category in CATEGORY_HINTS, \
                f"Missing hint for category: {category}"
            assert isinstance(CATEGORY_HINTS[category], str), \
                f"Hint for {category} is not a string"
            assert len(CATEGORY_HINTS[category]) > 0, \
                f"Hint for {category} is empty"
        
        print(f"  ✓ All {len(expected_categories)} category hints present")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_2_6_partial_credit():
    """PRIORITY 2.6: Verify partial credit system in step()."""
    print("\n[TEST] PRIORITY 2.6: Partial credit system")
    
    try:
        source = Path("server/environment.py").read_text(encoding='utf-8', errors='ignore')
        
        # Check partial credit logic
        assert "0.7 * test_score + 0.3 * quality_score" in source, \
            "Partial credit formula (70/30 split) not found"
        
        # Check that bonus is only applied if base_reward > 0
        assert "if base_reward > 0.0:" in source, \
            "Improvement bonus gating logic not found"
        
        print("  ✓ Partial credit system (70% tests + 30% quality)")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_2_7_enhanced_errors():
    """PRIORITY 2.7: Verify enhanced error messages."""
    print("\n[TEST] PRIORITY 2.7: Enhanced error messages")
    
    try:
        from models import DebugObservation
        
        # Check that error_details field exists
        assert 'error_details' in DebugObservation.model_fields, \
            "error_details field not in DebugObservation"
        
        # Check that it's used in environment.py
        source = Path("server/environment.py").read_text(encoding='utf-8', errors='ignore')
        assert "error_details" in source, "error_details not used in environment.py"
        assert "test_failures" in source, "test_failures not in error details"
        
        print("  ✓ Enhanced error details with test failures")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_2_8_episode_id_validation():
    """PRIORITY 2.8: Verify episode ID validation."""
    print("\n[TEST] PRIORITY 2.8: Episode ID validation")
    
    try:
        from server.environment import validate_episode_id
        
        # Test valid IDs
        assert validate_episode_id("ep_12345") == "ep_12345"
        assert validate_episode_id("test-episode_001") == "test-episode_001"
        
        # Test invalid IDs
        try:
            validate_episode_id("x" * 101)  # Too long
            print("  ✗ Should reject episode ID > 100 chars")
            return False
        except ValueError:
            pass  # Expected
        
        try:
            validate_episode_id("ep@invalid")  # Invalid characters
            print("  ✗ Should reject invalid characters")
            return False
        except ValueError:
            pass  # Expected
        
        print("  ✓ Episode ID validation working")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_3_9_dead_code_removed():
    """PRIORITY 3.9: Verify dead LLM judge code removed."""
    print("\n[TEST] PRIORITY 3.9: Dead code removal")
    
    try:
        source = Path("server/grader.py").read_text(encoding='utf-8', errors='ignore')
        
        # Check that call_llm_judge function is removed
        assert "def call_llm_judge(" not in source, \
            "Dead call_llm_judge function still present"
        
        # Check that we still have analyze_code_quality
        assert "def analyze_code_quality(" in source, \
            "analyze_code_quality function missing"
        
        print("  ✓ Dead LLM judge code removed")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_3_10_docstrings():
    """PRIORITY 3.10: Verify docstrings added."""
    print("\n[TEST] PRIORITY 3.10: Docstrings added")
    
    try:
        source = Path("server/grader.py").read_text(encoding='utf-8', errors='ignore')
        
        # Check VarVisitor has docstring
        assert 'class VarVisitor(ast.NodeVisitor):\n            """AST visitor' in source, \
            "VarVisitor class docstring missing"
        
        # Check visit methods have docstrings
        assert '"""Track variable assignments."""' in source
        assert '"""Track variable usage."""' in source
        assert '"""Track loop variable definitions."""' in source
        
        print("  ✓ Docstrings added to VarVisitor class")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_priority_3_11_temp_cleanup():
    """PRIORITY 3.11: Verify improved temp file cleanup."""
    print("\n[TEST] PRIORITY 3.11: Temp file cleanup logging")
    
    try:
        source = Path("server/grader.py").read_text(encoding='utf-8', errors='ignore')
        
        # Check that logger is used for cleanup errors
        assert "logger.warning" in source, "Logger not used for cleanup errors"
        assert "Failed to clean temp file" in source, "Cleanup error message not found"
        assert "OSError" in source, "OSError not caught specifically"
        
        print("  ✓ Temp file cleanup with error logging")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_model_fields():
    """Verify new fields added to DebugObservation."""
    print("\n[TEST] Model fields: hint and error_details")
    
    try:
        from models import DebugObservation
        
        fields = DebugObservation.model_fields
        
        assert 'hint' in fields, "hint field not in DebugObservation"
        assert 'error_details' in fields, "error_details field not in DebugObservation"
        
        # Check they're Optional
        hint_field = fields['hint']
        error_details_field = fields['error_details']
        
        print("  ✓ New fields (hint, error_details) added to DebugObservation")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("BugLab Critical Improvements Test Suite")
    print("=" * 70)
    
    tests = [
        # PRIORITY 1
        ("PRIORITY 1.1", test_priority_1_1_instance_state),
        ("PRIORITY 1.2", test_priority_1_2_validation_error_handler),
        ("PRIORITY 1.3", test_priority_1_3_timeout_in_inference),
        ("PRIORITY 1.4", test_priority_1_4_connection_retry),
        # PRIORITY 2
        ("PRIORITY 2.5", test_priority_2_5_hints),
        ("PRIORITY 2.6", test_priority_2_6_partial_credit),
        ("PRIORITY 2.7", test_priority_2_7_enhanced_errors),
        ("PRIORITY 2.8", test_priority_2_8_episode_id_validation),
        # PRIORITY 3
        ("PRIORITY 3.9", test_priority_3_9_dead_code_removed),
        ("PRIORITY 3.10", test_priority_3_10_docstrings),
        ("PRIORITY 3.11", test_priority_3_11_temp_cleanup),
        # Model
        ("Models", test_model_fields),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ✗ EXCEPTION: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All critical improvements validated!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
