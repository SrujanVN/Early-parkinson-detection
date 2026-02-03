# Setup script for virtual environment
# This script creates a new venv and installs all required packages

Write-Host "======================================================================"
Write-Host "VIRTUAL ENVIRONMENT SETUP FOR MODEL LOADING"
Write-Host "======================================================================"
Write-Host ""

# Step 1: Remove old venv if it exists
Write-Host "Step 1: Cleaning up old virtual environments..."
Write-Host "----------------------------------------------------------------------"

if (Test-Path ".venv_models") {
    Write-Host "Removing existing .venv_models directory..."
    Remove-Item -Recurse -Force .venv_models
}

Write-Host "Done: Cleanup complete"
Write-Host ""

# Step 2: Create new virtual environment
Write-Host "Step 2: Creating new virtual environment..."
Write-Host "----------------------------------------------------------------------"

python -m venv .venv_models

if ($LASTEXITCODE -eq 0) {
    Write-Host "Done: Virtual environment created successfully"
}
else {
    Write-Host "Error: Failed to create virtual environment"
    exit 1
}
Write-Host ""

# Step 3: Upgrade pip
Write-Host "Step 3: Upgrading pip..."
Write-Host "----------------------------------------------------------------------"

& .\.venv_models\Scripts\python.exe -m pip install --upgrade pip

Write-Host ""

# Step 4: Install requirements
Write-Host "Step 4: Installing requirements from backend\requirements.txt..."
Write-Host "----------------------------------------------------------------------"

& .\.venv_models\Scripts\python.exe -m pip install -r backend\requirements.txt

Write-Host ""

# Step 5: Verify installation
Write-Host "Step 5: Verifying installation..."
Write-Host "----------------------------------------------------------------------"

Write-Host "Installed packages:"
& .\.venv_models\Scripts\python.exe -m pip list

Write-Host ""
Write-Host "======================================================================"
Write-Host "SETUP COMPLETE"
Write-Host "======================================================================"
Write-Host ""
Write-Host "To activate the virtual environment, run:"
Write-Host "  .\.venv_models\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To test model loading, run:"
Write-Host "  .\.venv_models\Scripts\python.exe backend\test_model_loading.py"
Write-Host ""
