# BugLab Project Hub 🎯

> **Main Dashboard for Meta PyTorch OpenEnv Hackathon 2026**
> Last Updated: 2026-04-07

---

## 🚨 Critical Information

- **Deadline:** April 8th, 2026 (HARD DEADLINE)
- **Time Remaining:** ~3 days, 16 hours
- **Prize Pool:** $30,000
- **Reward:** Direct interview opportunity at Meta & HuggingFace AI teams

---

## 📊 Project Status Dashboard

### Overall Progress: 95% Complete ✅

| Phase | Status | Progress | Priority |
|-------|--------|----------|----------|
| Phase 1: Models & Data | ✅ DONE | 100% | - |
| Phase 2: Core Environment | ✅ DONE | 100% | - |
| Phase 2.5: Inference Script | ✅ DONE | 100% | - |
| Phase 3: LLM Judge | ✅ DONE | 100% | - |
| Phase 4: Docker + Validation | ✅ DONE | 100% | - |
| Phase 5: Polish (Recommended) | ✅ DONE | 100% | - |
| Phase 5: Deploy (Critical) | ⏳ TODO | 0% | 🔥 NEXT |

**Completed Today (April 5):**
- ✅ Inference testing & validation
- ✅ README polish (+135 lines)
- ✅ Code quality pass

---

## 🔗 Quick Links

### 🚨 Latest: Scoring System Fixes (CRITICAL)
- **[[INDEX_SCORING_FIXES]]** ⭐ START HERE
- [[12_SCORING_FORMULAS]] - Mathematical formulas
- [[14_EXPECTED_RESULTS]] - What you'll see after deployment
- [[11_SCORING_DEFECTS_FIXED]] - Complete defect analysis

### Project Documentation
- [[Project Context]] - Full technical specification
- [[New Requirements Analysis]] - 🚨 UPDATED REQUIREMENTS (April 4)
- [[Development Timeline]] - Timeline and milestones
- [[Phase 2 - Core Environment]] - Current work focus
- [[Bug Bank Status]] - Dataset details
- [[System Configuration]] - Hardware and software setup
- [[Deployment Checklist]] - Pre-submission requirements

---

## 📁 Project Structure

```
/home/someone/python_debug_env/
├── ✅ models.py (65 lines)
├── ✅ bug_bank.py (611 lines, 30 problems)
├── ✅ openenv.yaml
├── ✅ pyproject.toml
├── ✅ README.md (246 lines)
├── ✅ .env (all required variables configured)
├── ✅ .gitignore
├── ✅ client.py (EnvClient subclass)
├── ✅ inference.py (OpenAI baseline script) 
├── ✅ Dockerfile (container ready)
├── ✅ .dockerignore
├── ✅ uv.lock (dependencies locked)
└── server/
    ├── ✅ __init__.py
    ├── ✅ environment.py (Environment class)
    ├── ✅ grader.py (sandboxed runner + LLM judge)
    └── ✅ app.py (FastAPI with main())
```

---

## 🎯 Current Focus: Phase 2

**What needs to be built NOW:**
1. `server/grader.py` - Sandboxed test runner + LLM judge
2. `server/environment.py` - Environment class (reset/step/state)
3. `server/app.py` - FastAPI server
4. `client.py` - Client implementation

---

## 📝 Recent Activity Log

### 2026-04-04 07:52 UTC
- ✅ Analyzed complete workspace
- ✅ Confirmed Phase 1 completion (April 2nd)
- ✅ Connected Obsidian vault as project memory
- 🎯 Identified critical path: server/* files must be built today

### 2026-04-02 22:35 UTC (Last Development)
- ✅ Completed Phase 1: Models & Data
- ✅ Created all foundation files
- ✅ Validated 30 bug problems across 8 categories
- ⏸️ Development paused (2-day gap)

---

## ⚠️ Critical Constraints

1. **Never use eval()/exec()** - Always subprocess with timeout
2. **8GB RAM limit** - Use HF Inference API, not local models
3. **numpy 1.26.4 locked** - Do not upgrade (ROCm compatibility)
4. **HF_TOKEN in .env** - Never hardcode in source
5. **Port 8000** - OpenEnv standard for Docker

---

## 🔧 Environment

- **Location:** `/home/someone/python_debug_env/`
- **Python venv:** `/home/someone/ml` (must activate: `source ~/ml/bin/activate`)
- **GPU:** AMD RX 9060 XT (16GB VRAM, ROCm 7.2.1)
- **RAM:** 8GB (bottleneck)
- **HF Token:** Configured in `.env`

---

## 📚 Related Notes

- [[Code Patterns]] - Sandboxed execution and LLM judge patterns
- [[Reward Formula]] - 0.6 * test_score + 0.4 * llm_score
- [[Testing Strategy]] - How to validate each component
- [[Common Issues]] - Known gotchas and solutions

---

*This is a living document. Update after each development session.*
