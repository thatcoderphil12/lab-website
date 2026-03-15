# Exit on errors
$ErrorActionPreference = "Stop"

$AppDir = "$env:USERPROFILE\lab-website\app"
$VenvDir = Join-Path $AppDir "venv"

# Navigate to app directory
if (-Not (Test-Path $AppDir)) {
    Write-Host "Directory $AppDir not found."
    exit 1
}
Set-Location $AppDir

# Check for requirements.txt
if (-Not (Test-Path "requirements.txt")) {
    Write-Host "requirements.txt not found in $AppDir"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-Not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
}

# Activate virtual environment
$activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (-Not (Test-Path $activateScript)) {
    Write-Host "Activation script not found in $VenvDir"
    exit 1
}
Write-Host "Activating virtual environment..."
& $activateScript

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

Write-Host "Setup complete! Virtual environment is located at $VenvDir"
Write-Host "To activate it in the future, run: & '$VenvDir\Scripts\Activate.ps1'"
