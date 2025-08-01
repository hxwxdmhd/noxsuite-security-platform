FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y     curl     && rm -rf /var/lib/apt/lists/*

# Install Langflow and dependencies
RUN pip install langflow fastapi uvicorn

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3     CMD curl -f http://localhost:7860/health || exit 1

EXPOSE 7860 7443

CMD ["python", "-m", "langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
