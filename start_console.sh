#!/bin/bash
set -e
if [ ! -d "venv" ]; then
  python -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -U streamlit chromadb sentence-transformers pypdf python-docx pandas
streamlit run app.py --server.headless true --server.port 8501
