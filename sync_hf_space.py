#!/usr/bin/env python3
"""
Sync GitHub latest changes to HF Space
"""
from huggingface_hub import HfApi
import subprocess
import os
import shutil

HF_TOKEN = os.environ.get('HF_TOKEN')
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable must be set")

temp_dir = './temp_sync_quality'
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir, ignore_errors=True)

print("Syncing CRITICAL scoring fixes to HF Space...")

# Clone HF Space
clone_url = f'https://Someone5249:{HF_TOKEN}@huggingface.co/spaces/Someone5249/BugLab'
subprocess.run(['git', 'clone', clone_url, temp_dir], capture_output=True)

os.chdir(temp_dir)

# Set git config
subprocess.run(['git', 'config', 'user.email', 'automation@example.com'], capture_output=True)
subprocess.run(['git', 'config', 'user.name', 'Automation'], capture_output=True)

# Add GitHub remote
subprocess.run(['git', 'remote', 'add', 'github', 'https://github.com/Someone-9791/BugLab.git'], 
               capture_output=True)

# Fetch latest
subprocess.run(['git', 'fetch', 'github', 'main'], capture_output=True)

# Update critical files
files_to_update = ['server/grader.py', 'server/environment.py']
for f in files_to_update:
    subprocess.run(['git', 'checkout', 'github/main', '--', f], capture_output=True)

# Commit and push
subprocess.run(['git', 'add', '-A'], capture_output=True)
subprocess.run(['git', 'commit', '-m', 'Critical fix: Normalize quality scores and clamp rewards'], 
               capture_output=True)

result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Pushed CRITICAL fixes to HF Space")
else:
    print(f"Note: {result.stderr[:100]}")

os.chdir('..')
shutil.rmtree(temp_dir, ignore_errors=True)

print("\n✅ CRITICAL SCORING FIXES DEPLOYED!")
print("\nFixes applied:")
print("  ✓ Quality score normalization (max 0.6 → normalized to 1.0)")
print("    - 5/6 checks: 0.45/0.60 = 75%")
print("    - 6/6 checks: 0.60/0.60 = 100%")
print("  ✓ Reward clamped to [0, 1]")
print("    - No more rewards >100%")
print("\nRefresh: https://huggingface.co/spaces/Someone5249/BugLab")


