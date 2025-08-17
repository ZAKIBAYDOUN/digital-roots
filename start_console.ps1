if (!(Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -U streamlit chromadb sentence-transformers pypdf python-docx pandas
streamlit run app.py --server.headless true --server.port 8501
