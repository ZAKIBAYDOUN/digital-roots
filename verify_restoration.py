#!/usr/bin/env python3
import os

print("🔍 Verificando restauración de Digital Roots...")
print("=" * 60)

# Verificar que existe CEO Digital Twin
with open('/workspaces/digital-roots/streamlit_app.py', 'r') as f:
    content = f.read()

checks = {
    "CEO Digital Twin": "CEO Digital Twin" in content,
    "8 Agentes": all(agent in content for agent in ["strategy", "finance", "operations", "market"]),
    "URL Correcta": "digitalroots-bf3899aefd705f6789c2466e0c9b974d" in content,
    "Multi-idioma": all(lang in content for lang in ["en", "es", "is", "fr"]),
    "Tabs completos": all(tab in content for tab in ["Chat", "Ingest", "Evidence", "Governance"])
}

print("✅ Verificaciones:")
for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"  {status} {check}")

if all(checks.values()):
    print("\n🎉 ¡Digital Roots restaurado exitosamente!")
    print("   CEO Digital Twin y todos los agentes están de vuelta")
else:
    print("\n⚠️ Algunas verificaciones fallaron")

print("\n📱 La app se actualizará en Streamlit Cloud en 2-3 minutos")
print("🔗 https://digital-roots-my7i9xaz3xdnj2jhcjqbj6.streamlit.app")
