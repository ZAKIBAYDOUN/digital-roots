#!/usr/bin/env bash
set -e
python3 -m venv venv || true
source venv/bin/activate
python -m pip install --upgrade pip
pip install --upgrade streamlit chromadb sentence-transformers pypdf python-docx pandas
exec streamlit run streamlit_app.py --server.headless true --server.port 8501
