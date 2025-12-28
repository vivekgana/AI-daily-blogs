# Fix GitHub Token Issue

**Date:** 2025-12-28
**Status:** ⚠️ ACTION REQUIRED
**Issue:** Invalid GitHub Token (401 Bad credentials)

---

## Problem

Your GitHub API token is invalid:
```
Error: 401 Bad credentials
```

Current token in `.env`: `11ABBPU2I0fUeTiiafGmfH_oq44HhOy1LGWFGcgc088aIXv0FKIYEl1dXBHWDjmysbHJRYV7UUjYDhS5JB`

---

## Solution: Get a Valid GitHub Personal Access Token

### Step 1: Go to GitHub Settings

Visit: **https://github.com/settings/tokens**

Or navigate:
1. Click your profile picture (top right)
2. Settings
3. Developer settings (left sidebar, bottom)
4. Personal access tokens → Tokens (classic)

### Step 2: Generate New Token

1. Click "Generate new token" → "Generate new token (classic)"
2. Give it a note/description: `AI-daily-blogs local development`
3. Set expiration: Choose your preference (30 days, 60 days, 90 days, or No expiration)

### Step 3: Select Scopes

For this project, you need:
- ✅ **`public_repo`** - Access public repositories (required)
- ✅ **`read:org`** - Read org data (optional, for better search)

**Note:** You don't need full `repo` access, just `public_repo` is enough.

### Step 4: Generate and Copy Token

1. Click "Generate token" at the bottom
2. **IMPORTANT:** Copy the token immediately - you won't be able to see it again!
3. Token will look like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

Valid GitHub tokens:
- **Classic tokens:** Start with `ghp_` (~40 characters)
  - Example: `ghp_AbCdEf1234567890abcdefghijklmnopqr`
- **Fine-grained tokens:** Start with `github_pat_` (~93 characters)
  - Example: `github_pat_11AXXXXXX_AbCdEf1234567890...`
- **Both types are valid** - use either one

### Step 5: Update .env File

Replace the token in your `.env`:

**Before:**
```env
GITHUB_TOKEN=11ABBPU2I0fUeTiiafGmfH_oq44HhOy1LGWFGcgc088aIXv0FKIYEl1dXBHWDjmysbHJRYV7UUjYDhS5JB
```

**After:**
```env
GITHUB_TOKEN=ghp_your_new_token_here_xxxxxxxxxxxxxxxxxxxxxx
```

### Step 6: Test the New Token

Run the connectivity test:
```bash
python test_api_connectivity.py
```

You should see:
```
============================================================
Testing GitHub API
============================================================
✅ Using authenticated requests
Status Code: 200
✅ API working: XXXXX repositories found
```

---

## Alternative: Use Fine-Grained Tokens (Recommended)

Fine-grained tokens are more secure and have better control.

### Steps:
1. Go to https://github.com/settings/tokens?type=beta
2. Click "Generate new token"
3. Fill in:
   - **Token name:** `AI-daily-blogs`
   - **Expiration:** Your choice
   - **Repository access:** Public Repositories (read-only)
   - **Permissions:**
     - Contents: Read-only
     - Metadata: Read-only
4. Generate and copy the token
5. Update `.env` file

---

## Why is GitHub API Needed?

The GitHub API is used to:
- Search for machine learning repositories
- Find repos related to Kaggle competitions
- Discover algorithms and solutions
- Include in daily blog content

**Impact if not fixed:**
- Blog generation will work but GitHub repository section will be empty
- No trending repos will be included in blogs

---

## Troubleshooting

### "I don't see the token after generating"

GitHub only shows the token once for security. You must:
1. Copy it immediately after generation
2. If you missed it, delete the token and create a new one

### "401 error persists after updating token"

**Possible causes:**
1. **Token not copied correctly** - Check for spaces or missing characters
2. **Wrong token type** - Make sure it starts with `ghp_` or `github_pat_`
3. **Token revoked** - Generate a new one
4. **Scopes missing** - Regenerate with `public_repo` scope

### "Do I need a paid GitHub account?"

No! Free GitHub accounts can create personal access tokens with public repository access.

---

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit tokens to git**
   - `.env` is in .gitignore ✅
   - Always keep it there

2. **Use minimal scopes**
   - Only `public_repo` for this project
   - Don't give unnecessary permissions

3. **Set expiration dates**
   - Use 90 days or less
   - Rotate tokens regularly

4. **Revoke old tokens**
   - After creating new token, revoke old one
   - Visit: https://github.com/settings/tokens

5. **Monitor token usage**
   - GitHub shows when/where tokens are used
   - Revoke immediately if compromised

---

## Rate Limits

GitHub API has rate limits:

### Authenticated (with token):
- **5,000 requests/hour**
- **30 requests/minute** for search API

### Unauthenticated (no token):
- **60 requests/hour**
- **10 requests/minute** for search API

**Recommendation:** Always use a token for better rate limits.

---

## After Fixing

Once the GitHub token is working:

### 1. Test Locally
```bash
python test_api_connectivity.py
```

All three APIs should show ✅

### 2. Update GitHub Secrets

Update the token in GitHub Actions:
1. Go to: https://github.com/vivekgana/AI-daily-blogs/settings/secrets/actions
2. Find `GITHUB_TOKEN`
3. Click "Update"
4. Paste your new token
5. Save

**Note:** GitHub Actions automatically provides a `GITHUB_TOKEN`, but it's limited to the current repo only. For searching other repos, you need your own token.

### 3. Test Blog Generation

```bash
python src/main.py
```

Should now include GitHub repository section with trending repos.

---

## Expected Output After Fix

```bash
$ python test_api_connectivity.py

============================================================
Testing GitHub API
============================================================
✅ Using authenticated requests
Status Code: 200
✅ API working: 28543210 repositories found

============================================================
Test Results Summary
============================================================
✅ Kaggle: PASS
✅ Gemini: PASS
✅ GitHub: PASS

============================================================
✅ All APIs working correctly!
============================================================
```

---

## Current Status Summary

| API | Status | Issue | Priority |
|-----|--------|-------|----------|
| Kaggle | ✅ Working | 404 on some leaderboards (normal) | None |
| Gemini | ✅ Working | Fixed with new key | None |
| GitHub | ❌ Failing | 401 Bad credentials | **HIGH** |

---

## Next Steps

1. ✅ **Generate new GitHub token** from https://github.com/settings/tokens
2. ✅ **Update .env file** with new token
3. ✅ **Test locally** with `python test_api_connectivity.py`
4. ✅ **Update GitHub Secrets** with working token
5. ✅ **Test blog generation** with `python src/main.py`

---

**Generated:** 2025-12-28
**Status:** Awaiting valid GitHub token
**Priority:** MEDIUM - Blog works without it, but misses GitHub content
