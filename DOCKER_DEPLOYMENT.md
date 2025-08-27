# 🌱 Digital Roots - Docker Deployment Guide

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone the repository
git clone https://github.com/ZAKIBAYDOUN/digital-roots.git
cd digital-roots

# Set environment variables (optional)
export OPENAI_API_KEY="your-openai-api-key"
export LANGSMITH_API_KEY="your-langsmith-api-key"
export LANGGRAPH_API_URL="your-langgraph-url"

# Build and run
docker-compose up --build
```

### Using Docker directly
```bash
# Build the image
docker build -t digital-roots .

# Run the container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY="your-openai-api-key" \
  -e LANGSMITH_API_KEY="your-langsmith-api-key" \
  -e LANGGRAPH_API_URL="your-langgraph-url" \
  digital-roots
```

## Deployment Platforms

### Streamlit Cloud
The app is configured for automatic deployment to Streamlit Cloud from the GitHub repository.

### Cloud Run, Railway, Render
Use the Dockerfile for deployment to container platforms:
- **Cloud Run**: `gcloud run deploy --source .`
- **Railway**: Connect GitHub repo and enable auto-deploy
- **Render**: Connect GitHub repo and set build command to use Dockerfile

### Heroku
Create a `heroku.yml` file:
```yaml
build:
  docker:
    web: Dockerfile
run:
  web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

## Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI agents
- `LANGSMITH_API_KEY`: LangSmith API key for monitoring
- `LANGGRAPH_API_URL`: LangGraph deployment URL

## Health Check
The container includes a health check endpoint at `/_stcore/health`

## Security
- Runs as non-root user (UID 1000)
- Minimal base image (Python 3.11 slim)
- No unnecessary system packages

---
🌿 Built for cannabis professionals by ZAKIBAYDOUN
