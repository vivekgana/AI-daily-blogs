# Gemini API Rate Limit Handling

**Document Version:** 1.0
**Last Updated:** 2025-12-28
**Status:** ✅ Implemented

---

## Overview

The Gemini API free tier has strict rate limits that must be respected to ensure successful blog generation. This document explains the rate limits, how they're handled in the code, and how to adjust settings if needed.

---

## Gemini API Free Tier Limits

### Rate Limits (as of 2025-12-28)

| Metric | Limit | Window |
|--------|-------|--------|
| **Requests per minute** | 5 | 1 minute |
| **Requests per day** | 1,500 | 24 hours |
| **Tokens per day** | 1,000,000 | 24 hours |

### What This Means

- Maximum **5 API calls per minute**
- To stay safely under the limit: **4 calls per minute** (one call every 15 seconds)
- Exceeding these limits results in `429 ResourceExhausted` errors

---

## Error Example

When rate limit is exceeded, you'll see:

```
ResourceExhausted: 429 You exceeded your current quota, please check your plan and billing details.

Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
limit: 5
model: gemini-2.5-flash

Please retry in 35.798892652s.
```

---

## Implemented Solution

### 1. Rate Limit Enforcement

**Location:** `src/generators/gemini_generator.py`

**Key Features:**

#### A. Time-Based Rate Limiting
```python
self.last_request_time = 0  # Track last API call time

# Before each API call, check time since last request
current_time = time.time()
time_since_last_request = current_time - self.last_request_time

if self.last_request_time > 0 and time_since_last_request < rate_limit_delay:
    wait_time = rate_limit_delay - time_since_last_request
    logger.info(f"Rate limiting: waiting {wait_time:.1f}s before next API call")
    time.sleep(wait_time)

# Make the API call
self.last_request_time = time.time()
response = self.model.generate_content(prompt)
```

This ensures **minimum 15 seconds between API calls** = **4 calls per minute** (safely under 5/min limit)

#### B. Rate Limit Error Detection
```python
# Check if it's a rate limit error (ResourceExhausted or 429)
if 'ResourceExhausted' in str(type(e).__name__) or '429' in error_str or 'quota' in error_str.lower():
    # Extract retry delay from error message if available
    retry_match = re.search(r'retry in (\d+\.?\d*)s', error_str)
    if retry_match:
        suggested_delay = float(retry_match.group(1))
        logger.warning(f"Rate limit exceeded. API suggests waiting {suggested_delay}s")
        # Wait the suggested time plus a buffer
        sleep_time = suggested_delay + 5
    else:
        # Default: wait 60 seconds for rate limit reset
        sleep_time = 60

    logger.info(f"Rate limit hit. Waiting {sleep_time}s before retry...")
    if attempt < max_retries - 1:
        time.sleep(sleep_time)
```

This handles rate limit errors by:
1. Detecting `429` or `ResourceExhausted` errors
2. Extracting the suggested retry delay from error message
3. Waiting the suggested time + 5 second buffer
4. Retrying the request

#### C. Exponential Backoff for Other Errors
```python
if attempt < max_retries - 1:
    sleep_time = retry_delay * (attempt + 1)
    logger.info(f"Retrying in {sleep_time} seconds...")
    time.sleep(sleep_time)
```

For non-rate-limit errors:
- 1st retry: 15 seconds
- 2nd retry: 30 seconds
- 3rd retry: 45 seconds

---

## Configuration Settings

**File:** `config/config.yaml`

```yaml
gemini:
  model: "gemini-2.5-flash"
  temperature: 0.7
  max_tokens: 8000
  retry_attempts: 3  # Number of retry attempts
  retry_delay: 15  # Delay between retries (seconds)
  rate_limit_delay: 15  # Minimum delay between API calls (seconds)
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `retry_attempts` | 3 | Maximum number of retry attempts |
| `retry_delay` | 15 | Base delay between retries (seconds) |
| `rate_limit_delay` | 15 | Minimum delay between consecutive API calls (seconds) |

### Adjusting Rate Limit Behavior

**To be more conservative (slower but safer):**
```yaml
gemini:
  rate_limit_delay: 20  # 3 calls per minute
```

**To be more aggressive (faster but riskier):**
```yaml
gemini:
  rate_limit_delay: 12  # 5 calls per minute (at limit)
```

⚠️ **Warning:** Setting `rate_limit_delay` below 12 seconds will likely cause rate limit errors!

---

## Blog Generation Impact

### API Calls During Blog Generation

A typical blog generation makes **5-8 API calls**:

1. **Competition Overview** (1 call)
2. **Leaderboard Analysis** (0-3 calls, depending on available leaderboards)
3. **Algorithm Summaries** (0-2 calls, depending on available kernels)
4. **Research Papers Summary** (1 call)
5. **GitHub Repos Summary** (1 call)
6. **Trend Predictions** (1 call)

### Estimated Generation Time

With 15-second delays between calls:

- **Minimum:** 5 calls × 15s = **75 seconds** (~1.3 minutes)
- **Typical:** 6 calls × 15s = **90 seconds** (~1.5 minutes)
- **Maximum:** 8 calls × 15s = **120 seconds** (~2 minutes)

Plus data collection time (~30-45 seconds), **total time: 2-3 minutes** for complete blog generation.

---

## Troubleshooting

### Issue: Still Getting Rate Limit Errors

**Possible Causes:**
1. Multiple blog generations running simultaneously
2. `rate_limit_delay` set too low
3. Other applications using the same API key

**Solutions:**
1. Ensure only one blog generation process runs at a time
2. Increase `rate_limit_delay` to 20 seconds
3. Use separate API keys for different applications

### Issue: Blog Generation Taking Too Long

**Possible Causes:**
1. `rate_limit_delay` set too high
2. Multiple retries due to errors

**Solutions:**
1. Reduce `rate_limit_delay` to 12-15 seconds (minimum safe value)
2. Check logs for errors causing retries
3. Ensure API credentials are valid

### Issue: Quota Exceeded for the Day

**Error:**
```
ResourceExhausted: 429 Quota exceeded for daily requests
```

**Solution:**
- Free tier: **1,500 requests per day**
- Each blog generation: **5-8 requests**
- Maximum blogs per day: **~200-300**
- Daily automated run at 7 AM EST uses only **6-8 requests**
- Wait until next day for quota reset (midnight UTC)
- Or upgrade to paid tier for higher limits

---

## Monitoring Rate Limits

### Check Current Usage

Visit: https://ai.google.dev/usage?tab=rate-limit

You can monitor:
- Requests per minute (current)
- Requests per day (cumulative)
- Tokens used
- Quota remaining

### Log Analysis

Check logs for rate limit activity:

```bash
# Check for rate limit warnings
grep -i "rate limit" logs/*.log

# Check for 429 errors
grep "429" logs/*.log

# Check API call timing
grep "Rate limiting: waiting" logs/*.log
```

---

## Upgrading to Paid Tier

If you need higher rate limits:

### Google AI Studio Paid Tier

**Limits:**
- **60 requests per minute** (12x increase)
- **10,000 requests per day** (6.6x increase)
- Same token limits

**Cost:** Pay-per-use based on tokens consumed

**To Upgrade:**
1. Go to: https://aistudio.google.com/billing
2. Set up billing
3. No code changes needed - same API key works

---

## Best Practices

### DO:
- ✅ Use 15-second delays between API calls (default)
- ✅ Monitor logs for rate limit warnings
- ✅ Run blog generation once per day (as scheduled)
- ✅ Handle rate limit errors gracefully
- ✅ Use exponential backoff for retries

### DON'T:
- ❌ Set `rate_limit_delay` below 12 seconds
- ❌ Run multiple blog generations simultaneously
- ❌ Disable retry logic
- ❌ Ignore rate limit warnings in logs
- ❌ Use the same API key for multiple applications

---

## Performance Optimization

### Reduce API Calls

**1. Disable Optional Sections**

In `config.yaml`:
```yaml
blog:
  sections:
    - name: "Leaderboard Highlights"
      enabled: false  # Skip if not critical
    - name: "Algorithm Summaries"
      enabled: false  # Skip if not critical
```

**2. Cache Results**

Consider implementing caching for content that doesn't change frequently.

**3. Batch Processing**

Combine multiple pieces of information in a single prompt to reduce total API calls.

---

## Code Changes Summary

### Files Modified

1. **src/generators/gemini_generator.py**
   - Added `self.last_request_time` tracking
   - Implemented time-based rate limiting
   - Added rate limit error detection
   - Improved retry logic

2. **config/config.yaml**
   - Updated `retry_delay` from 2 to 15 seconds
   - Added `rate_limit_delay` parameter (15 seconds)

### No Changes Required To

- Test files
- GitHub Actions workflows
- Other collectors
- Blog generator orchestration

The rate limiting is **transparent** - existing code works without modification.

---

## Testing Rate Limits

### Test Rate Limit Handling

```bash
# This will make multiple API calls with proper delays
python src/main.py
```

**Expected Behavior:**
- See log messages: `Rate limiting: waiting X.Xs before next API call`
- No `429` errors
- Blog generates successfully
- Takes 2-3 minutes total

### Simulate Rate Limit Error

To test error handling, temporarily reduce the delay:

```yaml
gemini:
  rate_limit_delay: 1  # Too fast - will trigger rate limits
```

Run blog generation and verify:
- Rate limit error is caught
- Code waits suggested time
- Retry succeeds

**Remember to restore the delay to 15 seconds after testing!**

---

## Future Improvements

### Potential Enhancements

1. **Dynamic Rate Limiting**
   - Automatically adjust delays based on actual API response times
   - Learn from rate limit errors

2. **Request Queuing**
   - Queue API requests and process them at optimal rate
   - Better for multiple concurrent operations

3. **Caching Layer**
   - Cache generated content for similar prompts
   - Reduce redundant API calls

4. **Fallback Models**
   - Switch to different model if rate limited
   - Use cached content as fallback

---

## Related Documentation

- [FIX_GEMINI_API_KEY.md](FIX_GEMINI_API_KEY.md) - How to get and configure API key
- [API_STATUS_SUMMARY.md](API_STATUS_SUMMARY.md) - Overall API status
- [FINAL_TEST_RESULTS.md](FINAL_TEST_RESULTS.md) - Complete test results

---

## Official Gemini Documentation

- **Rate Limits:** https://ai.google.dev/gemini-api/docs/rate-limits
- **Usage Monitoring:** https://ai.google.dev/usage?tab=rate-limit
- **Pricing:** https://ai.google.dev/pricing
- **Error Codes:** https://ai.google.dev/gemini-api/docs/troubleshooting

---

**Generated:** 2025-12-28
**Status:** Implemented and tested
**Free Tier Limit:** 5 requests/minute
**Implementation:** 4 requests/minute (15s delay)
**Safety Margin:** 20% headroom under limit
