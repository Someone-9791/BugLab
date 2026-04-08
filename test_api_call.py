#!/usr/bin/env python3
"""Minimal test to verify API calls are being made."""

import os
import sys
from openai import OpenAI

# Set test environment variables
os.environ["API_BASE_URL"] = "https://test.example.com/v1"
os.environ["API_KEY"] = "test-key-12345"
os.environ["MODEL_NAME"] = "test-model"

# Simulate what the inference script does
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("API_KEY")

print(f"API_BASE_URL: {API_BASE_URL}")
print(f"MODEL_NAME: {MODEL_NAME}")
print(f"API_KEY: {API_KEY}")

if not API_BASE_URL or not API_KEY or not MODEL_NAME:
    print("ERROR: Missing required environment variables")
    sys.exit(1)

print("Creating OpenAI client...")
try:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )
    print("Client created successfully")
except Exception as e:
    print(f"ERROR creating client: {e}")
    sys.exit(1)

print("Attempting API call...")
try:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "test"}],
        temperature=0.0,
        max_tokens=100,
    )
    print(f"API call successful: {response}")
except Exception as e:
    print(f"API call failed (expected): {e}")
    # This is expected since we're using fake credentials
    # But the error should show the API was called
    print(f"Error type: {type(e).__name__}")
    if "https://test.example.com" in str(e):
        print("SUCCESS: API attempted to use provided base URL")
    else:
        print(f"WARNING: Error doesn't mention our URL: {e}")
