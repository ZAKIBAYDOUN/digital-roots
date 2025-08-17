# Green Hill Digital Roots - Setup Guide

## 🚀 Quick Start

### 1. Install Core Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Or install individually if you encounter timeout issues:
pip install streamlit pandas pillow requests numpy
```

### 2. Install Optional Multimedia Features (Optional)
```bash
# Audio processing
pip install speechrecognition pyaudio

# OCR (Optical Character Recognition)  
pip install pytesseract

# Web research
pip install duckduckgo-search beautifulsoup4 lxml

# Computer vision
pip install opencv-python-headless
```

### 3. Run the Application
```bash
# Start the Streamlit app
streamlit run streamlit_app.py
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: `bash: import: command not found`
**Problem**: You're trying to run Python code directly in bash terminal.

**Solution**: 
- Save Python code in a `.py` file
- Or run in Python REPL: `python` then enter your code
- Or run inline: `python -c "import streamlit; print('OK')"`

#### Issue: `ModuleNotFoundError: No module named 'streamlit'`
**Problem**: Dependencies not installed.

**Solution**:
```bash
pip install streamlit
# or
pip install -r requirements.txt
```

#### Issue: Network timeout during pip install
**Problem**: Network connectivity issues.

**Solution**:
```bash
# Try installing with timeout and retry
pip install --timeout 300 --retries 3 streamlit

# Or install from cache if available
pip install --cache-dir ~/.pip/cache streamlit
```

#### Issue: Multimedia features not working
**Problem**: Optional dependencies not installed.

**Solution**: The app gracefully handles missing optional features. Install them separately:
```bash
pip install speechrecognition  # for audio
pip install pytesseract        # for OCR
pip install duckduckgo-search  # for web research
```

## 🎯 Feature Status

The application automatically detects available features:

- ✅ **Core Chat**: Always available (uses Streamlit + core dependencies)
- 🔄 **Audio Processing**: Requires `speechrecognition` + `pyaudio`
- 🔄 **OCR/Image**: Requires `pytesseract` + system tesseract
- 🔄 **Web Research**: Requires `duckduckgo-search` + `beautifulsoup4`
- 🔄 **Computer Vision**: Requires `opencv-python-headless`

## 📋 System Requirements

- Python 3.8+
- 4GB RAM minimum (8GB recommended)
- Network connection for package installation
- Optional: Tesseract OCR system package for text recognition

## 🎨 Usage Examples

### Basic Chat
```bash
streamlit run streamlit_app.py
# Navigate to http://localhost:8501
# Use the chat interface in the first tab
```

### With Audio Processing
1. Install: `pip install speechrecognition`
2. Upload audio files in the "Audio" tab
3. Convert speech to text automatically

### With OCR
1. Install: `pip install pytesseract`
2. Upload images in the "Visual" tab  
3. Extract text from images automatically

## 🛡️ Safe Execution

The app is designed with safe execution in mind:
- All multimedia functions have graceful fallbacks
- Clear error messages guide users to install missing dependencies
- No crashes when optional features are unavailable
- Secure handling of uploaded files in temporary directories

## 🆘 Getting Help

If you encounter issues:

1. Check this troubleshooting guide first
2. Verify Python version: `python --version`
3. Check installed packages: `pip list`
4. Run basic test: `python -c "import streamlit; print('OK')"`
5. Check application logs in the Streamlit interface

---

**Last Updated**: August 2025  
**Status**: ✅ Production Ready