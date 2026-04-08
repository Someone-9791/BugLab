# BugLab - OpenEnv Docker Image
# Runs the debugging environment server
# Version: 2.1 (Code Quality Transparency Feature)

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy dependency files first for better caching
COPY requirements.txt pyproject.toml uv.lock* ./

# Install dependencies from requirements.txt (includes gradio, httpx, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY models.py bug_bank.py ./
COPY server/ ./server/

# Note: .env is not copied (provided via environment variables at runtime)
# Only .env.example is copied if it exists (for reference)

# Expose ports
EXPOSE 7860 8000

# Health check on port 7860 (OpenEnv API)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Run FastAPI server on port 7860 (HuggingFace Spaces standard)
# This exposes the OpenEnv API endpoints: /reset, /step, /state
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
