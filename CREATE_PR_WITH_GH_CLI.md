# Create Pull Request with GitHub CLI

**Status:** GitHub CLI installed ✅
**Next:** Restart terminal and run these commands

## Step 1: Restart Your Terminal/IDE

GitHub CLI was just installed. You need to restart your terminal or VSCode to make the `gh` command available.

**Quick restart:**
- Close and reopen your terminal/command prompt, OR
- Close and reopen VSCode

## Step 2: Verify GitHub CLI is Available

After restarting, run:
```bash
gh --version
```

Expected output:
```
gh version 2.83.2 (or later)
```

## Step 3: Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts:
1. Select: **GitHub.com**
2. Select: **HTTPS**
3. Select: **Login with a web browser**
4. Copy the one-time code shown
5. Press Enter to open browser
6. Paste the code and authorize
7. Return to terminal

## Step 4: Create the Pull Request

Navigate to your project directory (if not already there):
```bash
cd c:\Users\gekambaram\source\personal\AI-daily-blogs
```

Create the PR:
```bash
gh pr create \
  --title "Fix: Gemini API 404 error and Kaggle leaderboard rank bug + comprehensive testing" \
  --body-file .github/PR_DESCRIPTION.md \
  --base main \
  --head fix/gemini-api-and-kaggle-leaderboard
```

## Alternative: Single Line Command

```bash
gh pr create --title "Fix: Gemini API 404 error and Kaggle leaderboard rank bug + comprehensive testing" --body-file .github/PR_DESCRIPTION.md --base main --head fix/gemini-api-and-kaggle-leaderboard
```

## Expected Output

```
Creating pull request for fix/gemini-api-and-kaggle-leaderboard into main in vivekgana/AI-daily-blogs

https://github.com/vivekgana/AI-daily-blogs/pull/123
```

## Step 5: Verify PR Created

The command will output a URL to your new PR. You can:
1. Click the URL to view it in browser
2. Or run: `gh pr view --web`

## Step 6: Check GitHub Actions

After PR is created:
1. Go to the PR page
2. Scroll to the bottom
3. See "Checks" section
4. GitHub Actions will automatically run tests

Expected checks:
- ✅ Unit Tests
- ✅ Integration Tests
- ✅ Verify Credentials

## Troubleshooting

### Issue: "gh: command not found"
**Fix:** Restart your terminal/IDE and try again

### Issue: "Not authenticated"
**Fix:** Run `gh auth login` first

### Issue: "No commits between main and fix/..."
**Fix:** Branch is already pushed, this shouldn't happen

### Issue: "Pull request already exists"
**Fix:** PR already created! Run `gh pr view --web` to see it

## Manual Alternative (If GitHub CLI Issues)

If GitHub CLI still doesn't work after restart, use the web interface:

**Direct Link:**
https://github.com/vivekgana/AI-daily-blogs/compare/main...fix/gemini-api-and-kaggle-leaderboard?expand=1

See `CREATE_PR.md` for web interface instructions.

---

## Quick Command Summary

```bash
# After restarting terminal:
gh --version                 # Verify installation
gh auth login               # Authenticate (first time only)
cd c:\Users\gekambaram\source\personal\AI-daily-blogs
gh pr create --title "Fix: Gemini API 404 error and Kaggle leaderboard rank bug + comprehensive testing" --body-file .github/PR_DESCRIPTION.md --base main --head fix/gemini-api-and-kaggle-leaderboard
gh pr view --web            # View PR in browser
```

---

**Remember:** You must restart your terminal/IDE first for the `gh` command to be available!
