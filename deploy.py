#!/usr/bin/env python3
"""
Deploy to both GitHub and HuggingFace Spaces with appropriate READMEs.

Usage:
    python deploy.py           # Deploy to both remotes
    python deploy.py --github  # Deploy only to GitHub
    python deploy.py --hf      # Deploy only to HuggingFace Spaces
"""

import subprocess
import sys
import shutil
from pathlib import Path

def run(cmd, check=True):
    """Run shell command."""
    print(f"▶ {cmd}")
    return subprocess.run(cmd, shell=True, check=check, capture_output=False)

def deploy():
    repo_root = Path(__file__).parent
    readme_github = repo_root / "README.md"
    readme_hf = repo_root / "README_HF.md"
    
    # Check if files exist
    if not readme_hf.exists():
        print("❌ ERROR: README_HF.md not found")
        sys.exit(1)
    
    print("\n🚀 BugLab Deployment Manager\n")
    
    # Save original README
    run("git add -A")
    run("git diff --cached --name-only")
    
    # Deploy to HuggingFace Spaces
    print("\n📦 Deploying to HuggingFace Spaces...")
    shutil.copy(readme_hf, readme_github)
    print(f"   ✓ Using {readme_hf.name} as README.md")
    
    run("git add README.md")
    run("git commit -m 'chore: Deploy HF Spaces version with metadata' || true")
    run("git push hf main")
    print("   ✓ Pushed to HuggingFace Spaces")
    
    # Restore clean README for GitHub
    print("\n📦 Restoring GitHub version...")
    run("git checkout origin/main -- README.md")
    print("   ✓ Using clean README.md (no YAML)")
    
    run("git add README.md")
    run("git commit -m 'chore: Restore clean README for GitHub' || true")
    run("git push origin main")
    print("   ✓ Pushed to GitHub\n")
    
    print("✅ Deployment complete!")
    print("   🐙 GitHub: Clean README (no metadata)")
    print("   🤗 HF Spaces: README with metadata\n")

if __name__ == "__main__":
    deploy()
