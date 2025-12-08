# AI Analyzer Integration Guide

## Overview

The `AIAnalyzer` service uses OpenAI GPT-3.5 Turbo to provide intelligent commit analysis:

- 🆕 **Summary** - What changed in the commit
- ✏️ **Impact** - How it affects the codebase
- ✅ **Strengths** - Positive aspects of the change
- ⚠️ **Concerns** - Potential issues or areas of concern
- 👩‍💻 **Recommendation** - APPROVE/REVIEW/REJECT

## Setup

### 1. Install Dependencies

```bash
pip install openai
```

Or with docker-compose:
```bash
docker-compose build --no-cache
```

### 2. Get OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy the key

### 3. Configure Environment

Add to `.env`:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Or set as environment variable:

```bash
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Usage in Bot

### Basic Usage

```python
from ai_analyzer import AIAnalyzer

# Initialize
ai = AIAnalyzer(api_key="sk-...")
# or
ai = AIAnalyzer()  # Uses OPENAI_API_KEY env var

# Analyze diff
analysis = await ai.analyze_diff(diff_text, commit_message)

if analysis:
    print(f"Summary: {analysis['summary']}")
    print(f"Impact: {analysis['impact']}")
    print(f"Concerns: {analysis['concerns']}")
    print(f"Recommendation: {analysis['recommendation']}")
```

### Security Analysis

```python
security = await ai.analyze_security(diff_text)
if security:
    print(security['security_analysis'])
```

### Quality Score

```python
quality = await ai.get_commit_quality_score(diff_text, commit_message)
if quality:
    print(f"Score: {quality['score']}/10")
    print(quality['analysis'])
```

## Integration in bot.py

### When User Views Commit

```python
# After showing commit details, optionally add AI analysis

if github_service and ai_analyzer:
    # Get diff
    diff = await github_service.get_commit_diff(repo, commit_sha)
    
    if diff:
        # Analyze with AI
        analysis = await ai_analyzer.analyze_diff(diff, commit_message)
        
        if analysis:
            ai_text = (
                f"\n\n🤖 *AI Analysis:*\n"
                f"🆕 {analysis['summary']}\n"
                f"✏️ {analysis['impact']}\n"
                f"✅ {analysis['strengths']}\n"
                f"⚠️ {analysis['concerns']}\n"
                f"👩\u200d💻 {analysis['recommendation']}"
            )
            # Append to commit_details
            commit_details += ai_text
```

## Message Format in Telegram

The AI analysis will be shown as:

```
🤖 AI Analysis:
🆕 Summary of what changed
✏️ Brief impact statement
✅ Positive aspects
⚠️ Potential concerns
👩‍💻 Recommendation
```

## Configuration

### Customize Model

```python
ai.model = "gpt-4"  # Use GPT-4 for better analysis
```

### Adjust Max Diff Size

```python
ai.max_diff_size = 4000  # Smaller diffs process faster
```

## Error Handling

If OpenAI API is unavailable:

```python
try:
    analysis = await ai.analyze_diff(diff, message)
except Exception as e:
    logger.error(f"AI analysis failed: {e}")
    analysis = None  # Fall back to no AI analysis
```

## Cost Considerations

- **GPT-3.5 Turbo**: ~$0.0005 per commit analysis
- **GPT-4**: ~$0.03 per commit analysis (10x more expensive)

For production, consider:
- Caching analysis results
- Rate limiting analysis requests
- Using GPT-3.5 Turbo for cost efficiency

## Troubleshooting

### "OPENAI_API_KEY not found"

```bash
# Check environment variable
echo $OPENAI_API_KEY

# Set in .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

### "Rate limit exceeded"

OpenAI has rate limits. If exceeded, wait and retry.

Enable caching:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_cached_analysis(diff_hash):
    # Cache analysis results
    pass
```

### "Timeout"

Increases timeout:
```python
timeout=60.0  # 60 seconds instead of 30
```

## Features

- ✅ **Async/Await** - Non-blocking analysis
- ✅ **Error Handling** - Graceful fallback
- ✅ **Structured Response** - Parsed analysis fields
- ✅ **Multiple Analysis Types** - General, Security, Quality
- ✅ **Configurable** - Model, size, timeout

## Future Enhancements

- [ ] Caching analysis results
- [ ] Batch analysis for multiple commits
- [ ] Custom analysis prompts per team
- [ ] Integration with code quality tools (SonarQube, etc)
- [ ] Support for multiple AI providers (Claude, PaLM, etc)
- [ ] Training on team's coding standards
