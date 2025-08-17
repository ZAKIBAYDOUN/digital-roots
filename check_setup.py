#!/usr/bin/env python3
"""
Green Hill Digital Roots - Setup Validation Script
Checks system requirements and provides setup guidance.
"""

import sys
import importlib
import subprocess
import platform
from typing import Dict, List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"

def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Check if a package is installed and importable."""
    if import_name is None:
        import_name = package_name
    
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, '__version__', 'unknown')
        return True, f"✅ {package_name} ({version})"
    except ImportError:
        return False, f"❌ {package_name} not installed"

def check_core_packages() -> Dict[str, Tuple[bool, str]]:
    """Check core required packages."""
    core_packages = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'),
        ('pillow', 'PIL'),
        ('requests', 'requests'),
        ('numpy', 'numpy'),
    ]
    
    results = {}
    for package, import_name in core_packages:
        results[package] = check_package(package, import_name)
    
    return results

def check_optional_packages() -> Dict[str, Tuple[bool, str]]:
    """Check optional multimedia packages."""
    optional_packages = [
        ('speechrecognition', 'speech_recognition'),
        ('pytesseract', 'pytesseract'),
        ('duckduckgo-search', 'duckduckgo_search'),
        ('beautifulsoup4', 'bs4'),
        ('lxml', 'lxml'),
        ('opencv-python-headless', 'cv2'),
    ]
    
    results = {}
    for package, import_name in optional_packages:
        results[package] = check_package(package, import_name)
    
    return results

def check_streamlit_app() -> Tuple[bool, str]:
    """Check if streamlit app can be imported."""
    try:
        # Suppress warnings for this test
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import streamlit_app
        return True, "✅ streamlit_app.py imports successfully"
    except Exception as e:
        return False, f"❌ streamlit_app.py import failed: {str(e)}"

def get_install_commands() -> Dict[str, List[str]]:
    """Get installation commands for missing packages."""
    return {
        'core': [
            'pip install streamlit pandas pillow requests numpy',
            'or individually:',
            'pip install streamlit',
            'pip install pandas',
            'pip install pillow',
            'pip install requests',
            'pip install numpy',
        ],
        'audio': [
            'pip install speechrecognition',
            'pip install pyaudio  # May require system dependencies',
        ],
        'ocr': [
            'pip install pytesseract',
            '# Also install system tesseract:',
            '# Ubuntu/Debian: apt-get install tesseract-ocr',
            '# macOS: brew install tesseract',
            '# Windows: Download from GitHub releases',
        ],
        'web': [
            'pip install duckduckgo-search',
            'pip install beautifulsoup4',
            'pip install lxml',
        ],
        'vision': [
            'pip install opencv-python-headless',
        ]
    }

def main():
    """Run the setup validation."""
    print("=" * 60)
    print("🌿 Green Hill Digital Roots - Setup Validation")
    print("=" * 60)
    
    # System info
    print(f"\n📱 System Information:")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    # Python version
    print(f"\n🐍 Python Version:")
    python_ok, python_msg = check_python_version()
    print(f"  {python_msg}")
    
    if not python_ok:
        print("\n❗ Python 3.8+ is required. Please upgrade Python.")
        sys.exit(1)
    
    # Core packages
    print(f"\n📦 Core Packages:")
    core_results = check_core_packages()
    core_missing = []
    
    for package, (status, msg) in core_results.items():
        print(f"  {msg}")
        if not status:
            core_missing.append(package)
    
    # Optional packages
    print(f"\n🎨 Optional Multimedia Packages:")
    optional_results = check_optional_packages()
    optional_missing = []
    
    for package, (status, msg) in optional_results.items():
        print(f"  {msg}")
        if not status:
            optional_missing.append(package)
    
    # Streamlit app
    print(f"\n🚀 Application Status:")
    app_ok, app_msg = check_streamlit_app()
    print(f"  {app_msg}")
    
    # Summary and recommendations
    print(f"\n📊 Summary:")
    
    if core_missing:
        print(f"❌ Missing core packages: {', '.join(core_missing)}")
        print(f"🔧 Install with: pip install {' '.join(core_missing)}")
        print(f"⚠️  Application will not work without core packages.")
    else:
        print(f"✅ All core packages installed - Application ready!")
    
    if optional_missing:
        print(f"🔄 Optional packages not installed: {', '.join(optional_missing)}")
        print(f"ℹ️  These enable additional multimedia features (audio, OCR, web research, vision)")
        
        # Group missing packages by category
        install_commands = get_install_commands()
        audio_packages = ['speechrecognition', 'pyaudio']
        ocr_packages = ['pytesseract']
        web_packages = ['duckduckgo-search', 'beautifulsoup4', 'lxml']
        vision_packages = ['opencv-python-headless']
        
        if any(pkg.replace('-', '_') in optional_missing for pkg in audio_packages):
            print(f"\n🎤 For audio processing:")
            for cmd in install_commands['audio']:
                print(f"   {cmd}")
        
        if any(pkg in optional_missing for pkg in ocr_packages):
            print(f"\n📷 For OCR/image processing:")
            for cmd in install_commands['ocr']:
                print(f"   {cmd}")
        
        if any(pkg.replace('-', '_') in optional_missing for pkg in web_packages):
            print(f"\n🌐 For web research:")
            for cmd in install_commands['web']:
                print(f"   {cmd}")
        
        if any(pkg.replace('-', '_') in optional_missing for pkg in vision_packages):
            print(f"\n👁️  For computer vision:")
            for cmd in install_commands['vision']:
                print(f"   {cmd}")
    
    # Final instructions
    print(f"\n🎯 Next Steps:")
    if not app_ok:
        print(f"1. Fix the streamlit_app.py import issue shown above")
        print(f"2. Install missing core packages")
        print(f"3. Run this script again to verify")
    elif core_missing:
        print(f"1. Install missing core packages")
        print(f"2. Run this script again to verify") 
        print(f"3. Start the app: streamlit run streamlit_app.py")
    else:
        print(f"✅ Setup complete! Start the application:")
        print(f"   streamlit run streamlit_app.py")
        print(f"🌐 Then navigate to: http://localhost:8501")
    
    print(f"\n📚 For detailed help, see: SETUP_GUIDE.md")
    print("=" * 60)

if __name__ == "__main__":
    main()