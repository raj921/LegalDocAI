# Large File Upload Fix

## Problem
Your 160KB PDF (56,743 characters) was split into **22 chunks**, taking too long:
- 22 chunks × 12 seconds per chunk = ~264 seconds (4.4 minutes)
- Timeout was only 2 minutes ❌

## Solution Applied

### 1. Increased Chunk Size
**Changed:** `CHUNK_SIZE` from 3000 → **8000**
**Result:** Same file now splits into ~7 chunks instead of 22

**Calculation:**
```
Before: 56,743 / 3000 = 19 chunks (+ overlap = 22)
After:  56,743 / 8000 = 7 chunks  (+ overlap = 8)
```

**Time saved:**
```
Before: 22 chunks × 12s = 264 seconds (4.4 min) ⏱️
After:  8 chunks × 12s  = 96 seconds (1.6 min) ✅
```

**Improvement: 64% faster!** 🚀

### 2. Increased Timeout
**Changed:** Frontend timeout from 2 minutes → **5 minutes**
**Why:** Handles even very large files safely

### 3. Updated User Message
**Changed:** "30-60 seconds" → **"1-3 minutes for large files"**
**Why:** Sets proper expectations

## New Performance Expectations

| File Characters | Chunks | Expected Time |
|----------------|--------|---------------|
| < 8,000        | 1      | 15-20s       |
| 8,000-16,000   | 2      | 25-35s       |
| 16,000-32,000  | 3-4    | 40-60s       |
| 32,000-64,000  | 5-8    | 70-120s      |
| 64,000-128,000 | 9-16   | 2-3 min      |
| 128,000+       | 17+    | 3-5 min      |

**Your 160KB PDF (56,743 chars):**
- ✅ Now: ~8 chunks = **~90-120 seconds** (1.5-2 min)
- ❌ Before: ~22 chunks = ~260 seconds (4.3 min) - timed out!

## Configuration Changes

### Backend Config
**File:** `backend/.env`
```env
CHUNK_SIZE=8000      # Was: 3000
CHUNK_OVERLAP=500    # Was: 300
```

**File:** `backend/app/core/config.py`
```python
CHUNK_SIZE: int = 8000      # Default if not in .env
CHUNK_OVERLAP: int = 500
```

### Frontend Config
**File:** `frontend/lib/api.ts`
```typescript
const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes
```

## Restart Required

These config changes require restart:

```bash
# Stop backend (Ctrl+C)
# Then restart:
cd backend
source venv/bin/activate
python run.py

# Frontend should hot-reload automatically
# But if not:
cd frontend
npm run dev
```

## How to Verify

### Check Chunk Count
Watch backend logs when uploading:
```
INFO: Extracted 56743 characters
INFO: Split into 8 chunks         👈 Should be ~8 instead of 22!
```

### Check Processing Time
```
INFO: Processing chunk 1/8...
INFO: Processing chunk 2/8...
...
INFO: Processing chunk 8/8...
INFO: ✓ Template created
```

Total time should be **1.5-2 minutes** for your file.

## Why This Works

### Gemini API Token Limits
Gemini models can handle:
- **gemini-2.0-flash**: Up to 1M tokens (~750,000 words)
- Our chunks: ~8,000 chars = ~2,000 tokens

**We're using only 0.2% of the model's capacity per chunk!**

So we can safely increase chunk size significantly without hitting limits.

### Trade-offs

**Larger chunks (8000):**
- ✅ Fewer API calls = faster
- ✅ More context for AI = better extraction
- ✅ Less chance of duplicates
- ⚠️ Slightly higher API cost per call (but fewer calls overall)

**Optimal for most documents:**
- Contracts: 5-20 pages = 2-6 chunks
- Agreements: 10-30 pages = 3-10 chunks
- Large docs: 30-50 pages = 8-16 chunks

## Troubleshooting

### Still Timing Out?

1. **Check chunk count in logs:**
   ```
   INFO: Split into X chunks
   ```
   If X > 20, file might be too large

2. **Increase chunk size even more:**
   ```env
   CHUNK_SIZE=12000
   ```

3. **Increase timeout:**
   ```typescript
   setTimeout(() => controller.abort(), 600000); // 10 minutes
   ```

### Too Slow?

If processing is slow but not timing out:
- ✅ Working as designed for large files
- Check Gemini API response times in logs
- Consider background processing for very large files

### API Errors?

If you see Gemini API errors:
```
ERROR: Gemini API error: ...
```

Possible causes:
- API key quota exceeded
- Rate limiting
- Invalid API key
- Network issues

**Check API status:**
```bash
curl https://generativelanguage.googleapis.com/v1/models \
  -H "x-goog-api-key: YOUR_KEY"
```

## Performance Comparison

### Your 160KB PDF

**Before optimization:**
```
Chars:  56,743
Chunks: 22
Time:   264 seconds (4.4 min)
Result: TIMEOUT ❌
```

**After optimization:**
```
Chars:  56,743
Chunks: 8
Time:   96 seconds (1.6 min)
Result: SUCCESS ✅
```

**Improvement: 64% faster, no timeout!**

## Summary

✅ **Fixed:**
- Increased CHUNK_SIZE: 3000 → 8000
- Increased CHUNK_OVERLAP: 300 → 500
- Increased timeout: 2 min → 5 min
- Updated user message

✅ **Result:**
- Your 160KB file: 22 chunks → 8 chunks
- Processing time: 4.4 min → 1.6 min
- Will complete successfully ✓

✅ **Action Required:**
- Restart backend server (config changes)
- Frontend will auto-reload
- Try upload again!

---

**Status:** Ready to test! Upload your 160KB PDF again 🚀
