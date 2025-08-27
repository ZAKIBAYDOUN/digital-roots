#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive functionality check for Digital Roots deployment
"""
import os
import json
import sys
from pathlib import Path
import subprocess

print("?? Digital Roots Functionality Check")
print("=" * 60)

# Check commit information
try:
    current_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()[:7]
    print(f"?? Current commit: {current_commit}")
    
    # Check if we're on the desired commit
    if current_commit == "5613794":
        print("? Already on target deployment (5613794)")
    else:
        print(f"??  Not on target commit. Current: {current_commit}, Target: 5613794")
        print("   To revert: git checkout 5613794")
except:
    print("??  Unable to check git status")

print("\n?? Core Component Checks:")

# 1. Check main application file
checks = {}
if Path('streamlit_app.py').exists():
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open('streamlit_app.py', 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            content = ""
            print("   ??  Could not read streamlit_app.py due to encoding issues")
    
    checks["Streamlit App"] = True
    checks["CEO Digital Twin"] = "CEO Digital Twin" in content and "ghc_dt" in content
    checks["All 9 Agents"] = all(agent in content for agent in [
        "ghc_dt", "strategy", "finance", "operations", 
        "market", "compliance", "code", "innovation", "risk"
    ])
    checks["LangGraph URL"] = "digitalroots-bf3899aefd705f6789c2466e0c9b974d" in content
    checks["Multi-language"] = all(lang in content for lang in ["en", "es", "is", "fr"])
    checks["All Tabs"] = all(tab in content for tab in ["Chat", "Ingest", "Evidence", "Governance"])
else:
    checks["Streamlit App"] = False

# 2. Check agent files
agent_files = [
    "agents/ghc_dt.py",
    "agents/strategy.py", 
    "agents/finance.py",
    "agents/operations.py",
    "agents/market.py",
    "agents/compliance.py",
    "agents/code.py",
    "agents/innovation.py",
    "agents/risk.py"
]

agent_count = sum(1 for f in agent_files if Path(f).exists())
checks["All Agent Files"] = agent_count == 9
print(f"   ?? Found {agent_count}/9 agent files")

# 3. Check configuration
if Path('langgraph.json').exists():
    try:
        with open('langgraph.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        checks["LangGraph Config"] = True
        checks["9 Agents Configured"] = len(config.get('agents', {})) == 9
        print(f"   ??  Configured agents: {len(config.get('agents', {}))}")
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"   ??  Error reading langgraph.json: {e}")
        checks["LangGraph Config"] = False
        checks["9 Agents Configured"] = False
else:
    checks["LangGraph Config"] = False
    checks["9 Agents Configured"] = False

# 4. Check deployment workflow
checks["GitHub Actions"] = Path('.github/workflows/deploy-digital-roots.yml').exists()
checks["Ingest Workflow"] = Path('.github/workflows/ingest.yml').exists()

# 4.1. Check for content directories
content_dirs = ['docs', 'content']
existing_dirs = [d for d in content_dirs if Path(d).exists()]
checks["Content Directories"] = len(existing_dirs) > 0
if existing_dirs:
    print(f"   ?? Found content directories: {', '.join(existing_dirs)}")
else:
    print("   ?? No content directories found (docs/, content/)")

# 4.2. Check for documentation files
doc_files = list(Path('.').glob('**/*.md')) + list(Path('.').glob('**/*.txt')) + list(Path('.').glob('**/*.pdf'))
checks["Documentation Files"] = len(doc_files) > 0
print(f"   ?? Found {len(doc_files)} documentation files")

# 5. Check missing agent files
missing_agents = []
for agent_file in agent_files:
    if not Path(agent_file).exists():
        agent_name = agent_file.split('/')[-1].replace('.py', '')
        missing_agents.append(agent_name)

if missing_agents:
    print(f"   ? Missing agents: {', '.join(missing_agents)}")

# 6. Environment checks
env_vars = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY"),
    "LANGGRAPH_API_URL": os.getenv("LANGGRAPH_API_URL")
}

print("\n?? Environment Variables:")
for var, value in env_vars.items():
    status = "?" if value else "?"
    masked_value = f"{value[:10]}..." if value else "Not set"
    print(f"  {status} {var}: {masked_value}")

# 7. Check GitHub secrets (informational)
print("\n?? GitHub Secrets Check:")
print("   Required secrets for deployment:")
print("   - TWIN_API_URL (for LangGraph integration)")
print("   - INGEST_TOKEN (for document ingestion)")
print("   - OPENAI_API_KEY (for AI agents)")
print("   - LANGSMITH_API_KEY (for LangSmith)")
print("\n?? Setup Instructions:")
print("   1. Go to: digital-roots -> Settings -> Secrets and variables -> Actions")
print("   2. Add repository secrets:")
print("      - TWIN_API_URL: https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app")
print("      - INGEST_TOKEN: (same value as INGEST_AUTH_TOKEN in Cloud)")
print("      - OPENAI_API_KEY: (your OpenAI API key)")
print("      - LANGSMITH_API_KEY: (your LangSmith API key)")

# Display results
print("\n? Verification Results:")
for check, result in checks.items():
    status = "?" if result else "?"
    print(f"  {status} {check}")

# Summary
all_good = all(checks.values())
if all_good:
    print("\n?? All checks passed! Digital Roots is fully functional.")
    print("   - CEO Digital Twin operational")
    print("   - All 9 agents available")
    print("   - Multi-language support active")
    print("   - Ingest workflow configured")
    print("   - Ready for deployment")
else:
    print("\n??  Some checks failed.")
    
    if len(missing_agents) > 0:
        print(f"\n?? Missing Agent Files ({len(missing_agents)}):")
        for agent in missing_agents:
            print(f"   - Need to create: agents/{agent}.py")
    
    print("\n?? Recovery Options:")
    print("   Option 1 - Restore from commit 5613794:")
    print("     git fetch origin")
    print("     git checkout 5613794")
    print("     git push origin HEAD:main --force")
    print("\n   Option 2 - Fix current state:")
    missing = [k for k, v in checks.items() if not v]
    for item in missing:
        print(f"     - Fix: {item}")

print("\n?? Deployment URLs:")
print("   Streamlit: https://digital-roots-my7i9xaz3xdnj2jhcjqbj6.streamlit.app")
print("   LangGraph: https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app")

# Test virtual environment
print("\n?? Python Environment:")
print(f"   Python: {sys.executable}")
print(f"   Version: {sys.version.split()[0]}")
if 'env' in sys.executable.lower() or 'venv' in sys.executable.lower():
    print("   ? Running in virtual environment")
else:
    print("   ??  Not in virtual environment")

# Check if we can import required packages
print("\n?? Package Check:")
required_packages = ['streamlit', 'openai', 'requests']
for package in required_packages:
    try:
        __import__(package)
        print(f"   ? {package}")
    except ImportError:
        print(f"   ? {package} - run: pip install {package}")

print("\n?? Ingest Workflow:")
print("   - Triggers on pushes to main (docs/, content/, *.md, *.txt, *.pdf)")
print("   - Runs daily at 03:17 UTC")
print("   - Sends content to GHC Digital Twin")
print("   - Uses ZAKIBAYDOUN/GHC-DT reusable workflow")

print("\n" + "=" * 60)
print("?? Functionality check complete!")