# Reads codex-job.yaml, exports env, and launches the app with auto-restart

$ErrorActionPreference = 'Stop'
Set-Location "C:\Users\zakib\OneDrive\Documentos\GitHub\digital-roots"

# --- ENV (mirror the YAML) ---
$env:GH_PERSIST    = "C:\Users\zakib\OneDrive\Documentos\GitHub\digital-roots\vector_store\store_A"
$env:GH_COLLECTION = "gh_plan_A"
$env:GH_EMBED_MODEL= "sentence-transformers/all-MiniLM-L6-v2"
$env:PORT          = "8501"
$env:BIND          = "127.0.0.1"

# --- Ensure store path exists ---
New-Item -ItemType Directory $env:GH_PERSIST -Force | Out-Null

# --- Start loop: restart on crash ---
while ($true) {
  try {
    Write-Host "Starting GHC hub on http://$($env:BIND):$($env:PORT) ..."
    # Always run via 'python -m streamlit' to avoid PATH issues
    python -m streamlit run .\streamlit_app.py --server.address $env:BIND --server.port $env:PORT *>&1 |
      Tee-Object -FilePath "$env:LOCALAPPDATA\ghc-hub.log"
  } catch {
    Write-Warning "Hub crashed: $($_.Exception.Message)"
  }
  Start-Sleep -Seconds 2
  Write-Host "Restarting..."
}


Register to auto-start at login (one time):

schtasks /Create /TN "GHC Codex Agent" /SC ONLOGON /RL HIGHEST ^
 /TR "powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File C:\Users\zakib\OneDrive\Documentos\GitHub\digital-roots\run-codex-job.ps1"


Start it now (manual):

powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\zakib\OneDrive\Documentos\GitHub\digital-roots\run-codex-job.ps1


Open: http://localhost:8501
