# ?? Digital Roots Ingest Setup Guide

## Current Status: ? Ready for Final Setup

Your Digital Roots deployment is **fully functional** with all components working:
- ? All 9 AI agents operational
- ? CEO Digital Twin functioning
- ? Ingest workflow configured
- ? 91 documentation files ready for ingestion
- ? Multi-language support active

## ?? Next Steps to Complete Ingest Integration

### Step 1: Create Global Workflow in GHC-DT Repository

**Go to your GHC-DT repository:** https://github.com/ZAKIBAYDOUN/GHC-DT

1. Click **"Add file"** ? **"Create new file"**
2. Set path: `.github/workflows/ghc-global-ingest.yml`
3. Copy the content from `reference/ghc-global-ingest.yml` (created in this repo)
4. Commit the file

### Step 2: Add GitHub Secrets to Digital Roots

**Go to:** https://github.com/ZAKIBAYDOUN/digital-roots/settings/secrets/actions

Add these repository secrets:

| Secret Name | Value |
|-------------|-------|
| `TWIN_API_URL` | `https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app` |
| `INGEST_TOKEN` | Same value as `INGEST_AUTH_TOKEN` in your Cloud deployment |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `LANGSMITH_API_KEY` | Your LangSmith API key |

### Step 3: Test the Ingest Workflow

1. **Manual trigger:** Go to Actions ? "Ingest digital-roots ? Twin" ? "Run workflow"
2. **Automatic trigger:** Push any change to trigger on main branch

### Step 4: Verify Integration

1. Check the workflow run in GitHub Actions
2. Test queries in your GHC-DT Streamlit Tester UI
3. Ask questions about Digital Roots content to verify ingestion

## ?? What Will Be Ingested

The workflow will automatically ingest:
- All `.md` files in `docs/` and `content/` directories
- All `.md`, `.txt`, `.pdf` files in the repository
- Currently: **91 documentation files** ready for processing

### Content Structure:
- `docs/README.md` - Platform overview
- `docs/agents.md` - AI agent documentation
- `docs/api.md` - API documentation
- `README.md` - Project README
- All agent files documentation
- Any other markdown/text files in your repo

## ?? Automation Schedule

- **Push Trigger:** Every push to main branch with content changes
- **Daily Sync:** Every day at 03:17 UTC
- **Manual:** Anytime via GitHub Actions UI

## ?? Monitoring

After setup, monitor:
1. GitHub Actions runs for successful ingestion
2. LangSmith logs for agent interactions
3. Streamlit app responses mentioning Digital Roots content

## ?? Troubleshooting

If ingestion fails:
1. Check GitHub Actions logs
2. Verify all secrets are set correctly
3. Ensure GHC-DT global workflow exists
4. Confirm TWIN_API_URL is accessible

---

**Status:** Ready for production deployment with automated content ingestion! ??