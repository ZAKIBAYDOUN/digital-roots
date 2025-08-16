# GHC-DT (Green Hill CEO Digital Twin)

Minimal grounded agent for LangGraph, with FAISS vectorstore and a Streamlit control.

## Quick start
pip install -r requirements.txt
cp .env.example .env  # fill keys
# copy plan files into ./data (PDF/DOCX incl. Appendix + SHA)
python ingest/index_plan.py

## Streamlit test
streamlit run apps/ghc_dt_control.py

## Deploy (LangGraph Cloud)
After uploading this repo as a graph (ghc_dt), your deployment will auto-create an assistant.
Use the API flow: assistants.search -> threads.create -> runs.stream
