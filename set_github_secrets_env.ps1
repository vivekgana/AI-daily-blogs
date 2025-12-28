# Set Environment Variables from GitHub Secrets Values
# Run this script before running local tests

Write-Host "======================================================================"  -ForegroundColor Cyan
Write-Host " Set Environment Variables (GitHub Secrets Values)"  -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will help you set environment variables for local testing." -ForegroundColor Yellow
Write-Host "You need to provide your actual API credentials." -ForegroundColor Yellow
Write-Host ""

# Function to read secret input
function Read-SecretValue {
    param(
        [string]$PromptMessage,
        [string]$HelpUrl
    )

    Write-Host $PromptMessage -ForegroundColor Green
    if ($HelpUrl) {
        Write-Host "  Get it from: $HelpUrl" -ForegroundColor Gray
    }

    $value = Read-Host "  Enter value (or press Enter to skip)"
    return $value
}

# Kaggle Username
Write-Host ""
$kaggleUsername = Read-SecretValue `
    -PromptMessage "1. Kaggle Username:" `
    -HelpUrl "https://www.kaggle.com/settings/account"

if ($kaggleUsername) {
    $env:KAGGLE_USERNAME = $kaggleUsername
    Write-Host "   [SUCCESS] KAGGLE_USERNAME set" -ForegroundColor Green
} else {
    Write-Host "   [SKIPPED] KAGGLE_USERNAME not set" -ForegroundColor Yellow
}

# Kaggle API Key
Write-Host ""
$kaggleKey = Read-SecretValue `
    -PromptMessage "2. Kaggle API Key (from kaggle.json):" `
    -HelpUrl "https://www.kaggle.com/settings/account (Create New Token)"

if ($kaggleKey) {
    $env:KAGGLE_KEY = $kaggleKey
    $env:KAGGLE_PASSWORD = $kaggleKey  # GitHub Actions uses KAGGLE_PASSWORD
    Write-Host "   [SUCCESS] KAGGLE_KEY and KAGGLE_PASSWORD set" -ForegroundColor Green
} else {
    Write-Host "   [SKIPPED] KAGGLE_KEY not set" -ForegroundColor Yellow
}

# Gemini API Key
Write-Host ""
$geminiKey = Read-SecretValue `
    -PromptMessage "3. Gemini API Key:" `
    -HelpUrl "https://makersuite.google.com/app/apikey"

if ($geminiKey) {
    $env:GEMINI_API_KEY = $geminiKey
    Write-Host "   [SUCCESS] GEMINI_API_KEY set" -ForegroundColor Green
} else {
    Write-Host "   [SKIPPED] GEMINI_API_KEY not set" -ForegroundColor Yellow
}

# GitHub Token (optional)
Write-Host ""
$githubToken = Read-SecretValue `
    -PromptMessage "4. GitHub Token (optional, press Enter to skip):" `
    -HelpUrl "https://github.com/settings/tokens"

if ($githubToken) {
    $env:GITHUB_TOKEN = $githubToken
    $env:MY_GITHUB_ACTION = $githubToken  # Alternative name
    Write-Host "   [SUCCESS] GITHUB_TOKEN set" -ForegroundColor Green
} else {
    Write-Host "   [SKIPPED] GITHUB_TOKEN not set (optional)" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " SUMMARY" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$required = @(
    @{Name="KAGGLE_USERNAME"; Value=$env:KAGGLE_USERNAME; Required=$true},
    @{Name="KAGGLE_KEY"; Value=$env:KAGGLE_KEY; Required=$true},
    @{Name="GEMINI_API_KEY"; Value=$env:GEMINI_API_KEY; Required=$true},
    @{Name="GITHUB_TOKEN"; Value=$env:GITHUB_TOKEN; Required=$false}
)

$allRequired = $true
foreach ($item in $required) {
    if ($item.Value) {
        $length = $item.Value.Length
        Write-Host "[SET]  $($item.Name) (length: $length)" -ForegroundColor Green
    } else {
        if ($item.Required) {
            Write-Host "[MISSING]  $($item.Name) - REQUIRED" -ForegroundColor Red
            $allRequired = $false
        } else {
            Write-Host "[NOT SET]  $($item.Name) - Optional" -ForegroundColor Gray
        }
    }
}

Write-Host ""

if ($allRequired) {
    Write-Host "[SUCCESS] All required environment variables are set!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: python test_blog_generation_local.py" -ForegroundColor White
    Write-Host "  2. All tests should pass" -ForegroundColor White
    Write-Host "  3. Blog will be generated in blogs/ directory" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: These variables are only set for this PowerShell session." -ForegroundColor Yellow
    Write-Host "      Run this script again if you open a new terminal." -ForegroundColor Yellow
} else {
    Write-Host "[ERROR] Some required environment variables are missing!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this script again and provide all required values." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "How to get credentials:" -ForegroundColor Cyan
    Write-Host "  Kaggle: https://www.kaggle.com/settings/account" -ForegroundColor White
    Write-Host "          Click 'Create New Token' to download kaggle.json" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Gemini: https://makersuite.google.com/app/apikey" -ForegroundColor White
    Write-Host "          Click 'Create API key'" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "======================================================================" -ForegroundColor Cyan
