# Verify GitHub Secrets Configuration
# This script checks if required secrets are configured in GitHub repository

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " VERIFY GITHUB SECRETS CONFIGURATION" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if gh CLI is available
function Test-GitHubCLI {
    try {
        $version = gh --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] GitHub CLI is installed" -ForegroundColor Green
            Write-Host "          $($version.Split("`n")[0])" -ForegroundColor Gray
            return $true
        }
    } catch {
        Write-Host "[ERROR] GitHub CLI is not installed" -ForegroundColor Red
        Write-Host "        Install from: https://cli.github.com/" -ForegroundColor Yellow
        return $false
    }
    return $false
}

# Function to check authentication
function Test-GitHubAuth {
    try {
        # Clear GITHUB_TOKEN env var if it exists to avoid conflicts
        if ($env:GITHUB_TOKEN) {
            Write-Host "[INFO] Clearing GITHUB_TOKEN environment variable temporarily..." -ForegroundColor Yellow
            $script:oldToken = $env:GITHUB_TOKEN
            $env:GITHUB_TOKEN = $null
        }

        $authStatus = gh auth status 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] GitHub CLI is authenticated" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[ERROR] GitHub CLI is not authenticated" -ForegroundColor Red
            Write-Host "        Run: gh auth login --web" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "[ERROR] Failed to check GitHub authentication" -ForegroundColor Red
        return $false
    } finally {
        # Restore GITHUB_TOKEN if it was set
        if ($script:oldToken) {
            $env:GITHUB_TOKEN = $script:oldToken
        }
    }
}

# Function to list secrets
function Get-GitHubSecrets {
    try {
        Write-Host ""
        Write-Host "Fetching secrets from repository..." -ForegroundColor Cyan

        $secretsJson = gh secret list --repo vivekgana/AI-daily-blogs --json name,updatedAt 2>&1

        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to fetch secrets" -ForegroundColor Red
            Write-Host "        Error: $secretsJson" -ForegroundColor Yellow
            return $null
        }

        $secrets = $secretsJson | ConvertFrom-Json
        return $secrets

    } catch {
        Write-Host "[ERROR] Failed to parse secrets: $_" -ForegroundColor Red
        return $null
    }
}

# Main script
Write-Host "Step 1: Checking GitHub CLI..." -ForegroundColor Cyan
if (-not (Test-GitHubCLI)) {
    exit 1
}

Write-Host ""
Write-Host "Step 2: Checking GitHub authentication..." -ForegroundColor Cyan
if (-not (Test-GitHubAuth)) {
    Write-Host ""
    Write-Host "To authenticate, run:" -ForegroundColor Yellow
    Write-Host "  gh auth login --web" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Step 3: Fetching secrets from GitHub repository..." -ForegroundColor Cyan
$secrets = Get-GitHubSecrets

if (-not $secrets) {
    exit 1
}

# Check required secrets
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " GITHUB SECRETS STATUS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$requiredSecrets = @(
    @{Name="KAGGLE_USERNAME"; Required=$true},
    @{Name="KAGGLE_PASSWORD"; Required=$true},
    @{Name="GEMINI_API_KEY"; Required=$true},
    @{Name="MY_GITHUB_ACTION"; Required=$false}
)

$allConfigured = $true

foreach ($required in $requiredSecrets) {
    $secretName = $required.Name
    $found = $secrets | Where-Object { $_.name -eq $secretName }

    if ($found) {
        $updated = $found.updatedAt
        Write-Host "[FOUND] $secretName" -ForegroundColor Green
        Write-Host "        Last updated: $updated" -ForegroundColor Gray
    } else {
        if ($required.Required) {
            Write-Host "[MISSING] $secretName - REQUIRED" -ForegroundColor Red
            $allConfigured = $false
        } else {
            Write-Host "[MISSING] $secretName - Optional" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " SUMMARY" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

if ($allConfigured) {
    Write-Host "[SUCCESS] All required secrets are configured!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps to test locally:" -ForegroundColor Cyan
    Write-Host "  1. Set environment variables with your actual credentials:" -ForegroundColor White
    Write-Host "     Run: .\set_github_secrets_env.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "  2. Test API connectivity:" -ForegroundColor White
    Write-Host "     Run: python test_with_github_secrets.py" -ForegroundColor White
    Write-Host ""
    Write-Host "  3. Run full blog generation:" -ForegroundColor White
    Write-Host "     Run: python test_blog_generation_local.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: GitHub Secrets are encrypted and cannot be read directly." -ForegroundColor Yellow
    Write-Host "      You must manually set environment variables for local testing." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[ERROR] Some required secrets are missing!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Configure secrets at:" -ForegroundColor Yellow
    Write-Host "  https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions" -ForegroundColor White
    Write-Host ""
    Write-Host "Required secrets:" -ForegroundColor Yellow
    Write-Host "  KAGGLE_USERNAME - Your Kaggle username" -ForegroundColor White
    Write-Host "  KAGGLE_PASSWORD - Your Kaggle API key (from kaggle.json)" -ForegroundColor White
    Write-Host "  GEMINI_API_KEY - Your Google Gemini API key" -ForegroundColor White
    Write-Host ""
    Write-Host "Get credentials from:" -ForegroundColor Yellow
    Write-Host "  Kaggle: https://www.kaggle.com/settings/account" -ForegroundColor White
    Write-Host "  Gemini: https://makersuite.google.com/app/apikey" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "======================================================================" -ForegroundColor Cyan
