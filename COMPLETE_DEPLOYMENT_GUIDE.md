# ?? Digital Roots - Complete Deployment Guide

## ?? Status: READY FOR LANGGRAPH CLOUD DEPLOYMENT

Your Digital Roots platform is now fully configured with:

### ? **Core Platform (Streamlit)**
- **CEO Digital Twin** + **9 AI Agents** operational
- **Multi-language support** (EN, ES, IS, FR)
- **Complete interface** (Chat, Ingest, Evidence, Governance)
- **92+ documentation files** ready for ingestion

### ? **LangGraph Cloud Integration** 
- **StateGraph app** at `app.ghc_twin:app`
- **RAG-enabled Digital Twin** with ChromaDB vector store
- **FastAPI endpoints** for external access
- **Document ingestion** with authentication
- **CORS support** for frontend integration

### ? **Automated Ingest Pipeline**
- **GitHub Actions workflow** (`.github/workflows/ingest.yml`)
- **Daily sync** at 03:17 UTC
- **Push-triggered** content ingestion
- **Global workflow** integration with GHC-DT

---

## ?? **Final Deployment Steps**

### 1. **Push to GitHub**
```bash
git add .
git commit -m "Add complete LangGraph Cloud structure with RAG-enabled Digital Twin"
git push origin main
```

### 2. **Setup GitHub Secrets**
Go to: https://github.com/ZAKIBAYDOUN/digital-roots/settings/secrets/actions

Add these repository secrets:
| Secret | Value |
|--------|--------|
| `TWIN_API_URL` | `https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app` |
| `INGEST_TOKEN` | Same as `INGEST_AUTH_TOKEN` in Cloud |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `LANGSMITH_API_KEY` | Your LangSmith API key |

### 3. **Create Global Workflow in GHC-DT**
1. Go to: https://github.com/ZAKIBAYDOUN/GHC-DT
2. Create: `.github/workflows/ghc-global-ingest.yml`
3. Copy content from `reference/ghc-global-ingest.yml`

### 4. **Deploy to LangGraph Cloud**
1. **Connect repository** to LangGraph Cloud
2. **Set environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `VECTOR_STORE_DIR`: `vector_store` (default)
   - `ALLOWED_ORIGINS`: `*` or specific domains
   - `INGEST_AUTH_TOKEN`: Secure token for ingestion

3. **Deploy**: LangGraph will automatically detect `langgraph.json` and deploy

---

## ?? **API Endpoints**

Once deployed, your Digital Twin will have these endpoints:

### **Health Check**
```
GET https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app/health
```

### **Query Digital Twin**
```
POST https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app/api/twin/query
Content-Type: application/json

{
  "question": "What are the key features of Digital Roots?"
}
```

### **Ingest Documents**
```
POST https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app/api/twin/ingest_texts
Content-Type: application/json
X-INGEST-TOKEN: your-secure-token

{
  "texts": ["Document content..."],
  "metadatas": [{"source": "docs", "path": "README.md"}]
}
```

### **System Status**
```
GET https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app/api/twin/status
```

---

## ?? **How It Works**

### **Document Flow**
1. **Push to GitHub** ? Triggers ingest workflow
2. **Extract content** ? From docs/, *.md, *.txt, *.pdf files
3. **Send to Twin** ? Via `/api/twin/ingest_texts` endpoint  
4. **Store in vector DB** ? ChromaDB with embeddings
5. **Ready for queries** ? RAG-enhanced responses

### **Query Flow**
1. **User question** ? Sent to `/api/twin/query`
2. **Search vector store** ? Find relevant context
3. **Generate answer** ? GPT-4 with context
4. **Return response** ? JSON with answer and metadata

---

## ?? **Testing the Integration**

### **1. Test Ingest Workflow**
```bash
# Trigger manually in GitHub Actions
# Or push any change to trigger automatically
git commit --allow-empty -m "Test ingest workflow"
git push origin main
```

### **2. Test Digital Twin Query**
```bash
curl -X POST "https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app/api/twin/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Digital Roots and what agents does it have?"}'
```

### **3. Verify in Streamlit**
- Visit: https://digital-roots-my7i9xaz3xdnj2jhcjqbj6.streamlit.app
- Test all 9 agents in the Chat interface
- Check Evidence log for interactions

---

## ?? **Architecture Overview**

```
Digital Roots Ecosystem:
???????????????????    ????????????????????    ???????????????????
?   Streamlit     ?    ?   LangGraph      ?    ?   GitHub        ?
?   Frontend      ??????   Cloud API      ??????   Actions       ?
?                 ?    ?                  ?    ?   Ingest        ?
? • 9 AI Agents   ?    ? • RAG Digital    ?    ?                 ?
? • CEO Digital   ?    ?   Twin           ?    ? • Auto Sync     ?
?   Twin          ?    ? • Vector Store   ?    ? • Daily Cron    ?
? • Multi-lang    ?    ? • FastAPI        ?    ? • Manual Run    ?
? • Evidence Log  ?    ? • ChromaDB       ?    ?                 ?
???????????????????    ????????????????????    ???????????????????
```

---

## ?? **Next Steps**

1. **Deploy immediately** - All components are ready
2. **Test end-to-end** - Ingest ? Query ? Response
3. **Monitor performance** - Check LangSmith traces
4. **Scale as needed** - Add more content, agents, features

Your Digital Roots platform is now a **complete AI-powered ecosystem** ready for production! ????