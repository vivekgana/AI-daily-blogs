# Trigger GitHub Actions Workflow
# This script bypasses SSL verification issues

param(
    [string]$TestSuite = "credentials",
    [string]$Token = $env:MY_GITHUB_ACTION
)

Write-Host "=" -NoNewline
Write-Host ("=" * 69)
Write-Host " TRIGGERING GITHUB ACTIONS WORKFLOW"
Write-Host "=" -NoNewline
Write-Host ("=" * 69)

# Check token
if (-not $Token) {
    Write-Host "`nERROR: GitHub token not provided!" -ForegroundColor Red
    Write-Host "`nUsage:"
    Write-Host "  Option 1: Set environment variable first"
    Write-Host "    `$env:MY_GITHUB_ACTION=`"your_token_here`""
    Write-Host "    .\trigger_test.ps1"
    Write-Host "`n  Option 2: Pass token as parameter"
    Write-Host "    .\trigger_test.ps1 -Token `"your_token_here`""
    Write-Host "`nGet token from: https://github.com/settings/tokens"
    exit 1
}

Write-Host "Repository: vivekgana/AI-daily-blogs"
Write-Host "Workflow: test-on-demand.yml"
Write-Host "Branch: fix/gemini-api-and-kaggle-leaderboard"
Write-Host "Test Suite: $TestSuite"
Write-Host "=" -NoNewline
Write-Host ("=" * 69)

# API endpoint
$url = "https://api.github.com/repos/vivekgana/AI-daily-blogs/actions/workflows/test-on-demand.yml/dispatches"

# Request headers
$headers = @{
    "Accept" = "application/vnd.github+json"
    "Authorization" = "token $Token"
    "X-GitHub-Api-Version" = "2022-11-28"
}

# Request body
$body = @{
    "ref" = "fix/gemini-api-and-kaggle-leaderboard"
    "inputs" = @{
        "test_suite" = $TestSuite
        "verbose" = "false"
    }
} | ConvertTo-Json

Write-Host "`nSending request to GitHub API..."

try {
    # Ignore SSL certificate errors
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

    # Use .NET WebClient for better SSL control
    $webClient = New-Object System.Net.WebClient
    $webClient.Headers.Add("Accept", "application/vnd.github+json")
    $webClient.Headers.Add("Authorization", "token $Token")
    $webClient.Headers.Add("X-GitHub-Api-Version", "2022-11-28")
    $webClient.Headers.Add("Content-Type", "application/json")

    $response = $webClient.UploadString($url, "POST", $body)

    Write-Host "`n✅ SUCCESS! Workflow triggered successfully!" -ForegroundColor Green
    Write-Host "`nView workflow run:"
    Write-Host "  https://github.com/vivekgana/AI-daily-blogs/actions" -ForegroundColor Cyan
    Write-Host "`nThe workflow will start in a few seconds."
    Write-Host "Refresh the Actions page to see it running."

    exit 0
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__

    if ($statusCode -eq 204) {
        Write-Host "`n✅ SUCCESS! Workflow triggered successfully!" -ForegroundColor Green
        Write-Host "`nView workflow run:"
        Write-Host "  https://github.com/vivekgana/AI-daily-blogs/actions" -ForegroundColor Cyan
        exit 0
    }
    elseif ($statusCode -eq 401) {
        Write-Host "`n❌ ERROR: Authentication failed (401)" -ForegroundColor Red
        Write-Host "`nPossible issues:"
        Write-Host "  1. Token is invalid or expired"
        Write-Host "  2. Token doesn't have 'repo' or 'workflow' scope"
        Write-Host "`nFix:"
        Write-Host "  1. Go to: https://github.com/settings/tokens"
        Write-Host "  2. Generate new token (classic)"
        Write-Host "  3. Select scopes: 'repo' and 'workflow'"
        exit 1
    }
    elseif ($statusCode -eq 404) {
        Write-Host "`n❌ ERROR: Workflow not found (404)" -ForegroundColor Red
        Write-Host "`nWorkflow may not exist on this branch yet."
        Write-Host "Make sure the branch has been pushed to GitHub."
        exit 1
    }
    else {
        Write-Host "`n❌ ERROR: Request failed" -ForegroundColor Red
        Write-Host "Status Code: $statusCode"
        Write-Host "Error: $($_.Exception.Message)"

        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response: $responseBody"
        }

        exit 1
    }
}
finally {
    # Reset certificate validation
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = $null
}
