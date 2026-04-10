#!/usr/bin/env python3
"""Verify inference.py meets all requirements."""

import re

with open('inference.py', 'r') as f:
    content = f.read()

requirements = {
    'Environment Variables': [
        ('HF_TOKEN present (no default)', 'HF_TOKEN = os.environ.get("HF_TOKEN")'),
        ('API_BASE_URL with default', 'API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")'),
        ('MODEL_NAME with default', 'MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")'),
        ('LOCAL_IMAGE_NAME optional', 'LOCAL_IMAGE_NAME = os.environ.get("LOCAL_IMAGE_NAME")'),
    ],
    'OpenAI Client': [
        ('OpenAI imported', 'from openai import OpenAI'),
        ('Client initialized with variables', 'client = OpenAI(base_url=API_BASE_URL, api_key=LLM_TOKEN)'),
    ],
    'Stdout Logging': [
        ('START format', '[START]' in content and 'task=' in content),
        ('STEP format', '[STEP]' in content and 'step=' in content),
        ('END format with score', '[END]' in content and 'score=' in content),
    ],
}

print("\nREQUIREMENT COMPLIANCE CHECK")
print("=" * 60)

all_pass = True
for section, checks in requirements.items():
    print(f"\n{section}:")
    for check_name, check_result in checks:
        if isinstance(check_result, str):
            passed = check_result in content
        else:
            passed = check_result
        status = "PASS" if passed else "FAIL"
        symbol = "[O]" if passed else "[X]"
        print(f"  {symbol} {check_name}: {status}")
        if not passed:
            all_pass = False

print("\n" + "=" * 60)
if all_pass:
    print("STATUS: ALL REQUIREMENTS MET")
else:
    print("STATUS: SOME REQUIREMENTS NOT MET - REVIEW ABOVE")
print("=" * 60)
