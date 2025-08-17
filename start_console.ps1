$ErrorActionPreference = "Stop"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install --upgrade streamlit chromadb sentence-transformers pypdf python-docx pandas
streamlit run app.py --server.headless true --server.port 8501
