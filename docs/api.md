# Digital Roots API Documentation

## Base URLs

- **Streamlit App**: https://digital-roots-my7i9xaz3xdnj2jhcjqbj6.streamlit.app
- **LangGraph API**: https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app

## Authentication

The API uses OpenAI API keys for agent communication and LangSmith API keys for logging and analytics.

## Endpoints

### Chat with CEO Digital Twin
```
POST /api/twin/query
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <INGEST_TOKEN>
```

**Body:**
```json
{
  "question": "What's our current market position?",
  "agent": "ghc_dt",
  "source_type": "public"
}
```

**Response:**
```json
{
  "final_answer": "Based on current market analysis...",
  "agent": "ghc_dt",
  "tokens": 150,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Agent-Specific Queries

You can query specific agents directly:

- `ghc_dt` - CEO Digital Twin
- `strategy` - Strategy Agent
- `finance` - Finance Agent
- `operations` - Operations Agent
- `market` - Market Agent
- `compliance` - Compliance Agent
- `code` - Code Agent
- `innovation` - Innovation Agent
- `risk` - Risk Agent

### Health Check
```
GET /health
```

Returns system status and agent availability.

## Environment Variables

### Required
- `OPENAI_API_KEY` - OpenAI API key for agent responses
- `LANGSMITH_API_KEY` - LangSmith API key for logging
- `LANGGRAPH_API_URL` - LangGraph deployment URL

### Optional
- `GHC_DT_MODEL` - Override default model (gpt-4o-mini)
- `GHC_DT_TEMPERATURE` - Override temperature (0.2)
- `GHC_DT_SYSTEM_PROMPT` - Custom system prompt
- `GHC_DT_EVIDENCE_LOG` - Evidence log file path

## CORS Configuration

For web integration, configure `ALLOWED_ORIGINS` in your deployment to include your domain.