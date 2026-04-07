#!/usr/bin/env python3
"""
Create and configure BugLab HuggingFace Space
"""
import subprocess
import os
import shutil
import sys

HF_TOKEN = os.environ.get('HF_TOKEN')
if not HF_TOKEN:
    raise ValueError('HF_TOKEN environment variable not set')
HF_USERNAME = 'Someone5249'
SPACE_NAME = 'BugLab'
GITHUB_REPO = 'https://github.com/Someone-9791/BugLab.git'

temp_dir = './temp_buglab_space'

# Clean up if exists
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
    print(f"Cleaned up {temp_dir}")

# Clone the HF space
print(f"\n1. Cloning HuggingFace Space...")
clone_url = f'https://{HF_USERNAME}:{HF_TOKEN}@huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}'
result = subprocess.run(['git', 'clone', clone_url, temp_dir], capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Clone failed: {result.stderr}")
    sys.exit(1)
print(f"✓ Space cloned")

# Change to space directory
os.chdir(temp_dir)

# Add GitHub as remote
print(f"\n2. Adding GitHub repo as upstream...")
result = subprocess.run(['git', 'remote', 'add', 'github', GITHUB_REPO], capture_output=True, text=True)
if result.returncode != 0:
    # Remote might already exist
    result = subprocess.run(['git', 'remote', 'set-url', 'github', GITHUB_REPO], capture_output=True, text=True)
print(f"✓ GitHub remote configured")

# Fetch from GitHub
print(f"\n3. Fetching latest code from GitHub...")
result = subprocess.run(['git', 'fetch', 'github', 'main'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Fetch failed: {result.stderr}")
    sys.exit(1)
print(f"✓ Fetched from GitHub")

# Merge GitHub main into local main
print(f"\n4. Merging GitHub main...")
result = subprocess.run(['git', 'merge', 'github/main'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Note: {result.stderr}")
print(f"✓ Merged GitHub code")

# Push to HF Space
print(f"\n5. Pushing to HuggingFace Space...")
result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Push failed: {result.stderr}")
    sys.exit(1)
print(f"✓ Pushed to HF Space")

# Cleanup
os.chdir('..')
shutil.rmtree(temp_dir)

print(f"\n{'='*60}")
print(f"✅ SUCCESS!")
print(f"{'='*60}")
print(f"\n🚀 BugLab Space is now live at:")
print(f"   https://huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}")
print(f"\n⏳ The Space will build and start in 5-15 minutes.")
print(f"   Check the 'Logs' tab to monitor progress.")
print(f"\n📝 Once running, you can:")
print(f"   1. Click 'Reset' to load a debugging problem")
print(f"   2. Submit your fixed code")
print(f"   3. See quality feedback with full breakdown!")
