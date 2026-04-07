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

# Add root endpoint for HuggingFace Spaces compatibility
@app.get("/")
async def root():
    """Root endpoint - provides API info for HuggingFace Spaces."""
    return JSONResponse({
        "name": "BugLab",
        "version": "0.1.0",
        "description": "An RL environment where agents debug broken Python code",
        "status": "healthy",
        "endpoints": {
            "health": "/health - Check server health",
            "reset": "POST /reset - Reset environment and get new problem",
            "step": "POST /step - Submit code fix and get reward",
            "websocket": "WS /ws - WebSocket connection for streaming",
        },
        "documentation": "https://github.com/Someone-9791/BugLab",
        "huggingface_space": "https://huggingface.co/spaces/Someone5249/BugLab",
    })


def main():
    """Entry point for running the server."""
    import uvicorn
    import os
    # Allow PORT override for local development, but default to 7860 for HF Spaces
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

