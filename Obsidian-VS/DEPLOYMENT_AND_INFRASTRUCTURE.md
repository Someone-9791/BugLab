# Deployment & Infrastructure

**Last Updated**: Current Session
**Status**: ✅ LIVE AND OPERATIONAL

---

## Current Deployment Status

### HF Space
- **URL**: https://huggingface.co/spaces/Someone5249/BugLab
- **Status**: ✅ LIVE
- **Container**: Docker-based, auto-deployed from GitHub
- **Response**: ✅ Operational (responds to reset/step)

### GitHub Repository
- **URL**: https://github.com/Someone-9791/BugLab
- **Branch**: main (production)
- **Status**: ✅ CLEAN (no secrets, all code verified)
- **History**: ✅ INTACT (all git history preserved)

### Application Endpoints
```
POST   /reset              → Initialize environment
POST   /step               → Execute action
GET    /state              → Get current state
GET    /health             → Health check
```

---

## Architecture

### Technology Stack
- **Framework**: FastAPI (async Python web framework)
- **Container**: Docker (Python 3.11+)
- **Spec**: OpenEnv (standardized RL environment format)
- **Type System**: Pydantic v2 (type validation)
- **Testing**: Isolated sandbox execution

### Core Components

#### 1. Server Application (`server/app.py`)
- FastAPI application entry point
- Handles HTTP requests
- Manages environment lifecycle
- CORS-enabled for Gradio UI

#### 2. Environment (`server/environment.py`)
- PythonDebugEnvironment class (OpenEnv spec)
- Implements reset(), step(), state()
- Problem selection and management
- Episode tracking

#### 3. Grader (`server/grader.py`)
- Test execution in sandboxed subprocess
- Code quality analysis (static checks)
- Dual reward computation
- Normalization and clamping

#### 4. Models (`models.py`)
- DebugAction (type: fixed_code)
- DebugObservation (problem, feedback, reward)
- DebugState (episode tracking)

#### 5. Problem Bank (`bug_bank.py`)
- 30+ debugging problems
- Categorized by difficulty (easy/medium/hard)
- Test cases bundled with each problem

### Three Task Categories

#### Task 1: Fix Logic Bugs (easy/medium)
- Logic errors in conditionals
- Off-by-one errors
- Missing edge cases
- **Grader**: test_logic_fix

#### Task 2: Fix Algorithm Bugs (medium/hard)
- Type errors in computation
- Loop errors
- Variable shadowing
- Wrong return values
- **Grader**: test_algorithm_fix

#### Task 3: Optimize Code (hard)
- Complex edge cases
- Recursion errors
- Performance optimization
- **Grader**: test_optimization

---

## Containerization

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose API port
EXPOSE 8000

# Run application
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Build
```bash
docker build -t buglab .
docker run -p 8000:8000 buglab
```

### HF Space Configuration
- **Runtime**: Docker
- **Space Type**: Gradio (web UI available)
- **Auto-deployment**: From GitHub main branch
- **Secrets**: HF_TOKEN stored as secret

---

## Dependency Management

### Python Dependencies
```
fastapi >= 0.100.0
uvicorn >= 0.23.0
pydantic >= 2.0.0
requests >= 2.31.0
openenv-core >= 0.2.0
openai >= 1.0.0
```

### Installation
```bash
pip install -r requirements.txt
# OR
uv pip install -r requirements.txt
```

### Virtual Environment
- **Config**: pyvenv.cfg, uv.lock
- **Location**: bin/, include/, share/ (auto-created)

---

## API Specification

### OpenEnv Standard
The application implements the full OpenEnv specification:

```
Environment[Action, Observation, State]
  ├─ reset() → ObservationResult
  ├─ step(action: Action) → StepResult
  ├─ state() → State
  └─ close() → None
```

### OpenEnv Validation
```bash
openenv validate
# Output: [OK] MetaOpenEnv: Ready for multi-mode deployment
```

---

## Environment Variables

### Required for Inference
```bash
OPENAI_API_KEY      # Primary auth (or HF_TOKEN)
MODEL_NAME          # Model to use
API_BASE_URL        # LLM API endpoint
```

### Optional
```bash
ENV_URL             # For local testing (default: localhost:8000)
HF_TOKEN            # Alternative auth for HF models
```

### Configuration
- Defined in inference.py with sensible defaults
- Fallback chain: OPENAI_API_KEY → HF_TOKEN → API_KEY
- Never hardcoded in source

---

## Baseline Inference Script

### Location
`inference.py` (repo root)

### What It Does
1. Connects to environment (HTTP client)
2. Runs 5 test episodes:
   - 2 easy (fix_logic_bug)
   - 2 medium (fix_algorithm_bug)
   - 1 hard (optimize_and_fix)
3. For each episode:
   - Gets problem statement
   - Calls LLM to generate fix
   - Submits code to grader
   - Measures reward
4. Reports results with proper logging

### Logging Format
```
[START] task=fix_logic_bug_1 env=BugLab model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action="def string_length..." reward=0.85 done=false error=null
[STEP] step=2 action="def string_length..." reward=1.00 done=true error=null
[END] success=true steps=2 rewards=0.85,1.00
```

### Runtime
- Expected: 5-15 minutes
- Maximum: < 20 minutes
- Memory: ~2GB (with model caching)
- CPU: Works on 2 vCPU

---

## Testing & QA

### Test Suite
- ✅ openenv validate (spec compliance)
- ✅ Docker build (containerization)
- ✅ inference.py (baseline execution)
- ✅ Quality scoring (normalization)
- ✅ Reward calculation (clamping)

### Test Results
- ✅ All critical tests pass
- ✅ No mathematical errors
- ✅ Scores in correct range
- ✅ Graders deterministic

### Live Testing
- ✅ HF Space responsive
- ✅ reset() works
- ✅ step() works
- ✅ Scores generated correctly

---

## Security

### No Hardcoded Secrets
- ✅ .env.example for template
- ✅ Environment variables only
- ✅ Git history clean (no tokens)

### Sandboxed Execution
- ✅ Submitted code runs in subprocess
- ✅ Timeout protection (5 seconds)
- ✅ No access to filesystem

### Validation
- ✅ Input validation (Pydantic models)
- ✅ Type checking throughout
- ✅ Error handling with timeouts

---

## Performance

### Scalability
- Can handle multiple concurrent requests (async)
- Each episode takes ~2-3 minutes
- Supports batch testing

### Optimization
- Async I/O for concurrency
- Lazy problem loading
- Efficient test execution

### Resource Usage
- Memory: ~500MB base + model cache
- CPU: Single core minimum, multi-core recommended
- Disk: ~1GB for dependencies

---

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
- Available on HF Space (Logs tab)
- Buildlog: `curl -N -H "Authorization: Bearer $HF_TOKEN" https://huggingface.co/api/spaces/Someone5249/BugLab/logs/build`
- Runtime: `curl -N -H "Authorization: Bearer $HF_TOKEN" https://huggingface.co/api/spaces/Someone5249/BugLab/logs/run`

---

## Troubleshooting

### HF Space Not Responding
1. Check Space status on HF page
2. View build logs for errors
3. Check git repo for corrupt commits
4. Rebuild Space if needed

### Baseline Script Fails
1. Verify API key is valid
2. Check internet connectivity
3. Verify model name is correct
4. Check Environment URL is reachable

### Scoring Issues
- Verify normalization implemented (server/grader.py:503)
- Verify clamping implemented (server/environment.py:247)
- Run local test of grader function

---

## Deployment History

### Current Deployment
- **Deployed**: Session 8+ (post-fix)
- **Status**: ✅ LIVE
- **Issues**: All resolved

### Previous Attempts
- Session 7: Initial deployment
- Session 8: Scoring fixes and redeployment
- Current: Final cleanup and consolidation

---

## Maintenance

### Regular Checks
- ✅ Space responsive (daily)
- ✅ Logs checked for errors
- ✅ Dependency updates monitored

### Version Control
- ✅ Main branch: production
- ✅ All changes committed
- ✅ History preserved

---

## References

- **Environment Code**: server/ directory
- **Infrastructure Config**: Dockerfile, openenv.yaml, pyproject.toml
- **Scoring Details**: SCORING_SYSTEM_FIXES.md
- **Compliance**: COMPLIANCE_AND_REQUIREMENTS.md
