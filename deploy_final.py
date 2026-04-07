#!/usr/bin/env python3
"""Create HF Space from clean GitHub code"""
import subprocess
import os
import shutil
from huggingface_hub import HfApi, create_repo

HF_TOKEN = os.environ.get('HF_TOKEN')
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not set")

api = HfApi(token=HF_TOKEN)

print("=" * 70)
print("Creating BugLab Space from clean GitHub")
print("=" * 70)

# Create new Space
print("\n✨ Creating Space...")
try:
    repo = create_repo(
        repo_id="BugLab",
        repo_type="space",
        space_sdk="docker",
        token=HF_TOKEN,
        private=False,
        exist_ok=True
    )
    print(f"✓ Space created/exists: {repo.repo_id}")
except Exception as e:
    print(f"Note: {e}")

# Clone from GitHub (clean code)
print("\n📥 Cloning from GitHub...")
temp = "./buglab_clean"
if os.path.exists(temp):
    shutil.rmtree(temp, ignore_errors=True)

subprocess.run(['git', 'clone', 'https://github.com/Someone-9791/BugLab.git', temp],
              capture_output=True)

os.chdir(temp)

# Configure git
subprocess.run(['git', 'config', 'user.email', 'auto@example.com'], capture_output=True)
subprocess.run(['git', 'config', 'user.name', 'Automation'], capture_output=True)

# Add HF Space remote
hf_url = f'https://Someone5249:{HF_TOKEN}@huggingface.co/spaces/Someone5249/BugLab'
subprocess.run(['git', 'remote', 'add', 'hf', hf_url], capture_output=True)

# Push to Space
print("📤 Pushing clean code to HF Space...")
result = subprocess.run(['git', 'push', '-f', 'hf', 'main:main'],
                       capture_output=True, text=True)

os.chdir('..')
shutil.rmtree(temp, ignore_errors=True)

print()
print("=" * 70)

if result.returncode == 0:
    print("\n✅ SUCCESS - BugLab Space updated!")
    print("\n🔧 What's deployed:")
    print("   ✓ Quality score normalization (÷ 0.6)")
    print("   ✓ Reward clamping (max 1.0)")
    print("   ✓ All source code")
    print("\n🔨 Docker rebuild starting (2-5 minutes)...")
    print("\n🧪 Test at: https://huggingface.co/spaces/Someone5249/BugLab")
else:
    print(f"\n❌ Failed: {result.stderr[:200]}")
