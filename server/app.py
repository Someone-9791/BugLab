"""
FastAPI application factory for BugLab.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from openenv.core import create_app
from server.environment import PythonDebugEnvironment
from models import DebugAction, DebugObservation

# Create FastAPI app with OpenEnv
app = create_app(
    PythonDebugEnvironment,
    DebugAction,
    DebugObservation
)

# Add CORS middleware for local testing UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PRIORITY 1.2: Add validation error handler for malformed JSON
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle malformed JSON requests with helpful error message."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid action format",
            "details": "Request must contain 'fixed_code' field with valid Python code",
            "example": {"fixed_code": "def foo():\n    return 42"}
        }
    )

# Add tasks enumeration endpoint for validator
@app.get("/tasks")
async def list_tasks():
    """List all available tasks with graders."""
    from server.environment import TASKS
    tasks_info = []
    for task_id, task_config in TASKS.items():
        tasks_info.append({
            "id": task_config.get("id"),
            "name": task_config.get("name"),
            "description": task_config.get("description"),
            "difficulty_range": task_config.get("difficulty_range"),
            "grader": task_config.get("grader"),
            "num_problems": len(task_config.get("problem_ids", []))
        })
    return {"tasks": tasks_info, "total": len(tasks_info)}


# Add graders endpoint to expose available grader functions
@app.get("/graders")
async def list_graders():
    """List all available grader functions."""
    from server.grader import test_logic_fix, test_algorithm_fix, test_optimization
    graders = {
        "test_logic_fix": {
            "name": "Logic Fix Grader",
            "description": "Grades fix_logic_bug task submissions",
            "callable": True
        },
        "test_algorithm_fix": {
            "name": "Algorithm Fix Grader",
            "description": "Grades fix_algorithm_bug task submissions",
            "callable": True
        },
        "test_optimization": {
            "name": "Optimization Grader",
            "description": "Grades optimize_and_fix task submissions",
            "callable": True
        }
    }
    return {"graders": graders, "total": len(graders)}


# Add root endpoint for HuggingFace Spaces compatibility
@app.get("/")
async def root():
    """Root endpoint - provides API info for HuggingFace Spaces."""
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BugLab - OpenEnv API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #0d1117; color: #c9d1d9; }
            h1 { color: #58a6ff; }
            h2 { color: #8b949e; margin-top: 30px; }
            .status { color: #3fb950; font-weight: bold; }
            code { background: #161b22; padding: 2px 6px; border-radius: 3px; color: #ff7b72; }
            .endpoint { background: #161b22; padding: 15px; margin: 10px 0; border-left: 3px solid #58a6ff; }
            .method { color: #79c0ff; font-weight: bold; }
            a { color: #58a6ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🐛 BugLab - OpenEnv API Server</h1>
        <p><span class="status">✓ Status: HEALTHY</span></p>
        <p>An RL environment where AI agents learn to debug broken Python code using deterministic evaluation.</p>
        
        <h2>🔌 API Endpoints</h2>
        <div class="endpoint">
            <div><span class="method">POST</span> <code>/reset</code></div>
            <div>Reset environment and get a new debugging problem</div>
        </div>
        <div class="endpoint">
            <div><span class="method">POST</span> <code>/step</code></div>
            <div>Submit code fix and receive reward (0.0-1.0)</div>
        </div>
        <div class="endpoint">
            <div><span class="method">GET</span> <code>/state</code></div>
            <div>Get current episode state</div>
        </div>
        <div class="endpoint">
            <div><span class="method">GET</span> <code>/health</code></div>
            <div>Check server health</div>
        </div>
        
        <h2>📚 Resources</h2>
        <ul>
            <li><a href="https://github.com/Someone-9791/BugLab" target="_blank">GitHub Repository</a></li>
            <li><a href="https://github.com/Someone-9791/BugLab#readme" target="_blank">Documentation</a></li>
            <li><a href="https://huggingface.co/spaces/Someone5249/BugLab" target="_blank">HuggingFace Space</a></li>
        </ul>
        
        <h2>👥 Team Not Found</h2>
        <ul>
            <li>Pranatpal Sharma - Main Developer</li>
            <li>Shloka Chourasiya - Team Leader</li>
            <li>Vedant Sharma - UI/UX Developer</li>
        </ul>
        
        <p style="margin-top: 40px; color: #8b949e; font-size: 0.9em;">
            OpenEnv Hackathon 2026 | Version 0.1.0
        </p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


def main():
    """Entry point for running the server."""
    import uvicorn
    import os
    # Allow PORT override for local development, but default to 7860 for HF Spaces
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

