# Green Hill Canarias - LangGraph Cloud Deployment Guide

## 🚀 Ready for LangGraph Cloud!

This repository is now configured for **LangGraph Cloud** deployment with:

- ✅ **Wolfi Container**: Secure, lean base image
- ✅ **Minimal Dependencies**: Only essential packages
- ✅ **Graceful Error Handling**: No KeyError crashes
- ✅ **Real Document Integration**: Vector store with canonical docs
- ✅ **Production Environment Variables**: Secure configuration

## 📁 Repository Structure

```
/workspaces/green-hill-app/
├── main.py                 # Main graph with cloud-ready agents
├── models.py              # State models with optional fields
├── document_store.py      # Vector store integration
├── langgraph.json         # Cloud deployment configuration
├── requirements.txt       # Minimal dependencies
├── .env                   # Local environment (not deployed)
└── vectorstore/           # Prebuilt vector store with canonical docs
```

## 🌐 Deploy to LangGraph Cloud

### Step 1: Push to GitHub
```bash
cd /workspaces/green-hill-app
git init
git add .
git commit -m "Green Hill Canarias - Cloud-ready LangGraph deployment"
git remote add origin https://github.com/ZAKIBAYDOUN/green-hill-app.git
git push -u origin main
```

### Step 2: LangGraph Cloud Setup
1. Go to **LangGraph Cloud** (https://langsmith.langchain.com/)
2. Navigate to **LangGraph Platform → Deployments**
3. Click **"New Deployment"**
4. Connect to your **GitHub repository**: `ZAKIBAYDOUN/green-hill-app`
5. Set **Branch**: `main`
6. **Auto-deploy**: Enable

### Step 3: Environment Variables
Set these in the LangGraph Cloud deployment (placeholders; do not commit real keys):

```bash
# Required (choose ONE of these)
# For development with LangGraph Platform access
LANGSMITH_API_KEY=<your_langsmith_api_key>
# OR for production licensing
LANGGRAPH_CLOUD_LICENSE_KEY=<your_langgraph_license_key>

# Recommended for LLMs/RAG
OPENAI_API_KEY=<your_openai_key>
OPENAI_CHAT_MODEL=gpt-4o-mini

# Embeddings (choose backend)
EMBEDDING_BACKEND=hf                     # or: openai
HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
# If using OpenAI embeddings instead:
# OPENAI_EMBED_MODEL=text-embedding-3-small

# Optional RAG bootstrap
VECTOR_STORE_DIR=vector_store
# VECTOR_STORE_URL=https://example.com/chroma_store.zip

# Optional LangSmith tracing
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_PROJECT=green-hill-canarias
```

### Step 4: Deploy
- Click **"Deploy"**
- Wait for build completion (~3-5 minutes)
- Your endpoints will be available at: `https://your-deployment-id.langchain.app`

## 🎯 Key Features

### Multi-Agent Orchestration
- **Strategy Agent**: High-level planning with real document context
- **Finance Agent**: CAPEX/OPEX analysis and ROI projections  
- **Construction Agent**: Timeline and facility planning
- **QMS Agent**: Quality management and compliance
- **Governance Agent**: Decision tracking and ownership
- **Regulation Agent**: Regulatory pathway and permits
- **Investor Relations Agent**: Final reporting and deliverables

### Real Document Integration
- **Vector Store**: ChromaDB with embedded canonical documents
- **Retrieval**: Semantic search across Green Hill Canarias docs
- **Context**: Real business data informs agent decisions

## 📊 Your Green Hill Canarias Strategic Intelligence system is now production-ready! 🎉
