# Local LLM Analyzer Integration Guide

## Overview

The `LocalAnalyzer` uses **Ollama** to run open-source LLMs locally for commit analysis:

- 🔍 **Summary** - What changed
- ✏️ **Impact** - How it affects code
- ✅ **Strengths** - Positive aspects
- ⚠️ **Concerns** - Potential issues
- 👨‍💻 **Recommendation** - APPROVE/REVIEW/REJECT

### Benefits vs OpenAI

| Feature | Local (Ollama) | OpenAI |
|---------|---|---|
| **Cost** | Free (💲) | ~$0.0005 per analysis (💵) |
| **Privacy** | 100% local (🔐) | Cloud-based (⚠️) |
| **Speed** | 5-30 sec (depends on GPU) | 2-5 seconds |
| **Quality** | Good (Mistral, Llama2) | Excellent (GPT-3.5) |
| **Internet** | Not required | Required |
| **Setup** | Docker + Ollama | API key |

---

## Installation

### Option 1: Docker (Recommended)

```bash
# Pull Ollama Docker image
docker pull ollama/ollama

# Run Ollama container
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# Pull a model (choose one)
docker exec ollama ollama pull mistral          # 7B, super fast
docker exec ollama ollama pull llama2           # 7B, good quality
docker exec ollama ollama pull neural-chat      # 7B, optimized for chat
docker exec ollama ollama pull dolphin-mixtral  # Fast and smart

# Verify
docker exec ollama ollama list
```

### Option 2: Local Installation

1. **Download Ollama** from [ollama.ai](https://ollama.ai)
2. **Install** for your OS (macOS, Linux, Windows)
3. **Run Ollama**
   ```bash
   ollama serve
   ```
4. **In another terminal, pull model**
   ```bash
   ollama pull mistral
   # or
   ollama pull llama2
   ```

### Option 3: Update docker-compose.yml

Add Ollama service to docker-compose.yml:

```yaml
  ollama:
    image: ollama/ollama
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      OLLAMA_HOST: 0.0.0.0:11434
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  ollama_data:
    driver: local
```

Then:
```bash
docker-compose up -d ollama
docker-compose exec ollama ollama pull mistral
```

---

## Model Selection

### Recommended Models

| Model | Size | Speed | Quality | RAM | Best For |
|-------|------|-------|---------|-----|----------|
| **mistral** | 7B | ⚡⚡⚡ | ⭐⭐⭐⭐ | 4GB | General, fastest |
| **neural-chat** | 7B | ⚡⚡⚡ | ⭐⭐⭐⭐ | 4GB | Conversations, optimized |
| **llama2** | 7B | ⚡⚡ | ⭐⭐⭐⭐⭐ | 4GB | Best quality |
| **llama2** | 13B | ⚡ | ⭐⭐⭐⭐⭐ | 8GB | Very high quality |
| **dolphin-mixtral** | 8.7B | ⚡⚡ | ⭐⭐⭐⭐⭐ | 5GB | Smart + fast |
| **openchat** | 3.5B | ⚡⚡⚡⚡ | ⭐⭐⭐ | 2GB | Ultra-light |
| **zephyr** | 7B | ⚡⚡ | ⭐⭐⭐⭐ | 4GB | Good balance |

### Setup

#### Download Model

```bash
# Mistral (recommended for speed)
ollama pull mistral

# Llama2 (recommended for quality)
ollama pull llama2

# Or:
ollama pull neural-chat
ollama pull dolphin-mixtral
```

#### Configure Bot

Add to `.env`:

```env
# Use local model instead of OpenAI
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://localhost:11434
LOCAL_MODEL=mistral
# LOCAL_MODEL options: mistral, llama2, neural-chat, dolphin-mixtral, openchat, orca-mini, zephyr
```

Or for Docker:

```env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434  # Use container hostname
LOCAL_MODEL=mistral
```

---

## Usage

### Python Code

```python
from local_analyzer import LocalAnalyzer

# Initialize with Ollama
local_ai = LocalAnalyzer(
    ollama_host="http://localhost:11434",
    model="mistral",
    timeout=60
)

# Check if ready
if await local_ai.check_ollama_health():
    print("✓ Ollama and model ready")

# Analyze diff
analysis = await local_ai.analyze_diff(diff_text, commit_message)

if analysis:
    print(f"Summary: {analysis['summary']}")
    print(f"Impact: {analysis['impact']}")
    print(f"Concerns: {analysis['concerns']}")
    print(f"Recommendation: {analysis['recommendation']}")
```

### Environment Variables

```bash
# Use local model
export USE_LOCAL_MODEL=true
export OLLAMA_HOST=http://localhost:11434
export LOCAL_MODEL=mistral
```

---

## Integration in bot.py

### Option A: Local Only

```python
from local_analyzer import LocalAnalyzer

async def main():
    # Use local model
    local_ai = LocalAnalyzer()
    
    # Check health on startup
    if not await local_ai.check_ollama_health():
        logger.warning("Ollama not available, local analysis disabled")
        local_ai = None
    
    # Use in handlers
    if local_ai:
        analysis = await local_ai.analyze_diff(diff, message)
```

### Option B: Cloud + Local Fallback

```python
from ai_analyzer import AIAnalyzer
from local_analyzer import LocalAnalyzer

async def get_analysis(diff, message):
    # Try OpenAI first
    if openai_available:
        return await ai_analyzer.analyze_diff(diff, message)
    
    # Fallback to local
    elif local_available:
        return await local_analyzer.analyze_diff(diff, message)
    
    # No analysis
    else:
        return None
```

### Option C: Hybrid (User Choice)

```python
# Store user preference
USER_PREFERENCES = {}  # user_id -> 'openai' or 'local'

async def get_analysis(user_id, diff, message):
    preference = USER_PREFERENCES.get(user_id, 'auto')
    
    if preference == 'openai' and openai_available:
        return await ai_analyzer.analyze_diff(diff, message)
    elif preference == 'local' and local_available:
        return await local_analyzer.analyze_diff(diff, message)
    elif preference == 'auto':
        # Auto-select: use local if available, otherwise OpenAI
        if local_available:
            return await local_analyzer.analyze_diff(diff, message)
        elif openai_available:
            return await ai_analyzer.analyze_diff(diff, message)
    
    return None
```

---

## Docker Setup

### Complete docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: github-commits-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-github_verifier}
      POSTGRES_USER: ${POSTGRES_USER:-github_bot}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secure_password}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - bot_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-github_bot}"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      OLLAMA_HOST: 0.0.0.0:11434
    networks:
      - bot_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      timeout: 5s
      retries: 5

  github-commits-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: github-commits-verifier-bot
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_healthy
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-github_bot}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-github_verifier}
      OLLAMA_HOST: http://ollama:11434
      LOCAL_MODEL: ${LOCAL_MODEL:-mistral}
      PYTHONUNBUFFERED: "1"
    volumes:
      - ./logs:/app/logs
    networks:
      - bot_network
    healthcheck:
      test: ["CMD", "python", "-c", "print('Bot OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

networks:
  bot_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
  ollama_data:
    driver: local
```

Then:

```bash
# First time - pull model
docker-compose up -d ollama
docker-compose exec ollama ollama pull mistral

# Then start all services
docker-compose up -d
```

---

## Performance Tuning

### With GPU (NVIDIA CUDA)

```bash
# Install NVIDIA Docker runtime
sudo apt-get install nvidia-docker2

# Update docker-compose.yml
services:
  ollama:
    image: ollama/ollama:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

Then Ollama will use GPU automatically and be **5-10x faster**!

### CPU-Only Optimization

```env
# Use smaller model
LOCAL_MODEL=mistral  # or neural-chat

# Reduce timeout if too slow
OLLAMA_TIMEOUT=30  # 30 seconds max
```

---

## Troubleshooting

### "Connection refused"

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Or in Docker
curl http://ollama:11434/api/tags
```

### "Model not found"

```bash
# List available models
ollama list

# Pull missing model
ollama pull mistral
```

### "Timeout" or "Very slow"

```bash
# Model is too large for your hardware
# Switch to smaller model:
ollama pull mistral  # 7B (fastest)
ollama pull neural-chat  # 7B (optimized)

# Or get GPU support
docker-compose up -d ollama  # with GPU runtime
```

### "Out of memory"

```bash
# Models need RAM:
# - 7B model: ~4GB
# - 13B model: ~8GB

# Use smaller model or add swap
# Check available RAM:
free -h
```

---

## Cost Comparison

| Method | Setup | Cost/Analysis | Cost/1000 |
|--------|-------|---------------|----------|
| **Local (Ollama)** | 1x docker pull | $0 | $0 |
| **OpenAI GPT-3.5** | 1x API key | $0.0005 | $0.50 |
| **OpenAI GPT-4** | 1x API key | $0.03 | $30 |

**Local is FREE after initial setup!** 🌟

---

## Features

- ✅ **Privacy** - 100% local, no data to cloud
- ✅ **Cost** - Free (except hardware)
- ✅ **Fast** - With GPU, faster than cloud
- ✅ **Offline** - Works without internet
- ✅ **Open Source** - Full control
- ✅ **Customizable** - Fine-tune models

---

## Future Enhancements

- [ ] Support for larger models (34B, 70B)
- [ ] Model fine-tuning on team standards
- [ ] Multi-GPU support
- [ ] Model switching per analysis type
- [ ] Streaming responses for long analyses
- [ ] Local embeddings for similarity search
