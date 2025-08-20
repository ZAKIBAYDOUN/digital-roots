#!/usr/bin/env python3
import re

# Leer el archivo
with open('streamlit_app.py', 'r') as f:
    content = f.read()

# Reemplazar SOLO la URL de LangGraph (mantener todo lo demás intacto)
old_url = 'https://ground-control-a0ae430fa0b85ca09ebb486704b69f2b.us.langgraph.app'
new_url = 'https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app'

content = content.replace(old_url, new_url)

# Escribir de vuelta
with open('streamlit_app.py', 'w') as f:
    f.write(content)

print("✅ URL actualizada sin tocar el resto del código")
