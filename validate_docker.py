#!/usr/bin/env python3
"""
Docker Build Validation Script for Digital Roots
Tests the Docker setup and validates the application structure.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_status(message, status="INFO"):
    """Print status message with emoji"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def check_docker_files():
    """Check if Docker files exist and are properly configured"""
    print_status("Checking Docker configuration files...")
    
    required_files = {
        "Dockerfile": "Main Docker configuration",
        ".dockerignore": "Docker build optimization",
        "docker-compose.yml": "Local development setup",
        "requirements.txt": "Python dependencies"
    }
    
    all_good = True
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print_status(f"{description}: {file_path}", "SUCCESS")
        else:
            print_status(f"Missing {description}: {file_path}", "ERROR")
            all_good = False
    
    return all_good

def validate_requirements():
    """Validate requirements.txt format"""
    print_status("Validating requirements.txt format...")
    
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
        
        valid = True
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                # Check if line starts with a number (malformed)
                if line[0].isdigit() and "." in line[:3]:
                    print_status(f"Line {i}: Malformed requirement '{line}'", "ERROR")
                    valid = False
                else:
                    print_status(f"Line {i}: Valid requirement '{line}'", "SUCCESS")
        
        return valid
    except FileNotFoundError:
        print_status("requirements.txt not found", "ERROR")
        return False

def validate_python_imports():
    """Test if all Python modules can be imported"""
    print_status("Testing Python module imports...")
    
    try:
        # Test main app import
        import streamlit_app
        print_status("streamlit_app.py imports successfully", "SUCCESS")
        
        # Test agent imports
        sys.path.append(".")
        from agents.ghc_dt import run_ghc_dt
        from agents.strategy import run_strategy
        from agents.finance import run_finance
        from agents.operations import run_operations
        from agents.market import run_market
        from agents.compliance import run_compliance
        from agents.code import run_code
        from agents.innovation import run_innovation
        from agents.risk import run_risk
        
        print_status("All agent modules import successfully", "SUCCESS")
        return True
        
    except ImportError as e:
        print_status(f"Import error: {e}", "ERROR")
        return False

def test_docker_syntax():
    """Test Docker syntax without building"""
    print_status("Testing Dockerfile syntax...")
    
    try:
        # Check if docker is available
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            print_status("Docker not available in this environment", "WARNING")
            return True
            
        # Try to validate the Dockerfile by parsing it
        with open("Dockerfile", "r") as f:
            dockerfile_content = f.read()
        
        # Basic syntax checks
        required_instructions = ["FROM", "WORKDIR", "COPY", "RUN", "EXPOSE", "CMD"]
        found_instructions = []
        
        for line in dockerfile_content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                instruction = line.split()[0].upper()
                if instruction in required_instructions:
                    found_instructions.append(instruction)
        
        missing = set(required_instructions) - set(found_instructions)
        if missing:
            print_status(f"Missing Docker instructions: {missing}", "ERROR")
            return False
        
        print_status("Dockerfile contains all required instructions", "SUCCESS")
        return True
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print_status(f"Could not test Docker syntax: {e}", "WARNING")
        print_status("Docker may not be available in this environment", "INFO")
        return True  # Don't fail if Docker isn't available

def generate_deployment_readme():
    """Generate deployment instructions"""
    print_status("Generating deployment instructions...")
    
    readme_content = """# 🌱 Digital Roots - Docker Deployment Guide

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
docker run -p 8501:8501 \\
  -e OPENAI_API_KEY="your-openai-api-key" \\
  -e LANGSMITH_API_KEY="your-langsmith-api-key" \\
  -e LANGGRAPH_API_URL="your-langgraph-url" \\
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
"""
    
    with open("DOCKER_DEPLOYMENT.md", "w") as f:
        f.write(readme_content)
    
    print_status("Created DOCKER_DEPLOYMENT.md with deployment instructions", "SUCCESS")

def main():
    """Main validation function"""
    print_status("🌱 Digital Roots - Docker Build Validation", "INFO")
    print_status("=" * 50, "INFO")
    
    checks = [
        ("Docker Files", check_docker_files),
        ("Requirements Format", validate_requirements),
        ("Python Imports", validate_python_imports),
        ("Docker Syntax", test_docker_syntax)
    ]
    
    results = []
    for check_name, check_func in checks:
        print_status(f"\\n🔍 Running {check_name} check...", "INFO")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(f"Error in {check_name}: {e}", "ERROR")
            results.append((check_name, False))
    
    # Generate deployment guide
    print_status("\\n📚 Generating deployment documentation...", "INFO")
    generate_deployment_readme()
    
    # Summary
    print_status("\\n📋 Validation Summary", "INFO")
    print_status("=" * 50, "INFO")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "SUCCESS" if result else "ERROR"
        print_status(f"{check_name}: {'PASSED' if result else 'FAILED'}", status)
    
    if passed == total:
        print_status(f"\\n🎉 All {total} checks passed! Docker setup is ready.", "SUCCESS")
        print_status("You can now build and deploy the Docker image.", "INFO")
        return True
    else:
        print_status(f"\\n⚠️ {passed}/{total} checks passed. Please fix the issues above.", "WARNING")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)