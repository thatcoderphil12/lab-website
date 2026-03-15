# lab-start.ps1

$ErrorActionPreference = "Stop"

$URL = "https://localhost"
$BASE = "$HOME\lab-website"

Write-Host "Starting lab website..."

# Activate Python virtual environment

Write-Host "Activating virtual environment..."
& "$BASE\venv\Scripts\Activate.ps1"

# Start Paper 1

Write-Host "Starting Paper 1..."
$paper1Path = "$BASE\app\paper-1"

Start-Process powershell -ArgumentList @(
"-NoExit",
"-Command",
"cd '$paper1Path'; streamlit run app.py --server.port 8080 --server.baseUrlPath paper1"
)

# Start Paper 2

Write-Host "Starting Paper 2..."
$paper2Path = "$BASE\app\paper-2"

Start-Process powershell -ArgumentList @(
"-NoExit",
"-Command",
"cd '$paper2Path'; streamlit run app.py --server.port 8081 --server.baseUrlPath paper2"
)

# Start nginx if installed

Write-Host "Starting nginx..."
try {
nginx
} catch {
Write-Host "nginx not found in PATH. Skipping..."
}

# Wait a moment before opening browser

Start-Sleep -Seconds 3

Write-Host "Opening browser..."
Start-Process $URL

Write-Host "Done."
