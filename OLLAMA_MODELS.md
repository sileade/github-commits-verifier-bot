# Available Ollama Models

## Quick Reference

```
🎉 MISTRAL (7B) - START HERE
   Size: 4GB RAM, 4GB disk
   Speed: ⚡⚡⚡ Super fast (5-10 sec)
   Quality: ⭐⭐⭐⭐ Excellent
   Setup: ollama pull mistral

🔏 LLAMA2 (7B)
   Size: 4GB RAM, 4GB disk
   Speed: ⚡⚡ Medium (10-20 sec)
   Quality: ⭐⭐⭐⭐⭐ Very Excellent
   Setup: ollama pull llama2

🗨 NEURAL-CHAT (7B)
   Size: 4GB RAM, 4GB disk
   Speed: ⚡⚡⚡ Super fast (5-10 sec)
   Quality: ⭐⭐⭐⭐ Excellent
   Setup: ollama pull neural-chat

🚀 DOLPHIN-MIXTRAL (8.7B)
   Size: 5GB RAM, 5GB disk
   Speed: ⚡⚡ Medium (10-15 sec)
   Quality: ⭐⭐⭐⭐⭐ Very Excellent (smart)
   Setup: ollama pull dolphin-mixtral

🥪 OPENCHAT (3.5B)
   Size: 2GB RAM, 2GB disk
   Speed: ⚡⚡⚡⚡ Ultra fast (<5 sec)
   Quality: ⭐⭐⭐ Good
   Setup: ollama pull openchat

🤦 ZEPHYR (7B)
   Size: 4GB RAM, 4GB disk
   Speed: ⚡⚡ Medium (10-20 sec)
   Quality: ⭐⭐⭐⭐ Excellent
   Setup: ollama pull zephyr

🙙 ORCA-MINI (3B)
   Size: 2GB RAM, 2GB disk
   Speed: ⚡⚡⚡ Very fast (5-15 sec)
   Quality: ⭐⭐⭐ Good
   Setup: ollama pull orca-mini
```

## Setup Commands

```bash
# List all available models
ollama list

# Pull a model
ollama pull mistral
ollama pull llama2
ollama pull neural-chat
ollama pull dolphin-mixtral
ollama pull openchat
ollama pull zephyr
ollama pull orca-mini

# In Docker:
docker exec ollama ollama pull mistral

# Run interactively (chat)
ollama run mistral
```

## Comparison Table

| Model | Size | Params | RAM | Disk | Speed | Quality | Type |
|-------|------|--------|-----|------|-------|---------|------|
| **mistral** | 7B | 7.2B | 4GB | 4GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | General |
| **llama2** | 7B | 7B | 4GB | 4GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | General |
| **neural-chat** | 7B | 7B | 4GB | 4GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Chat |
| **dolphin-mixtral** | 8.7B | 8.7B MoE | 5GB | 5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Smart |
| **openchat** | 3.5B | 3.5B | 2GB | 2GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Efficient |
| **zephyr** | 7B | 7B | 4GB | 4GB | ⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| **orca-mini** | 3B | 3B | 2GB | 2GB | ⚡⚡⚡ | ⭐⭐⭐ | Efficient |

## Recommendations by Scenario

### 🚀 Speed Priority (Real-time users)
→ Use **mistral** or **neural-chat**
- Get results in 5-10 seconds
- Still very good quality
- Perfect for interactive use

### ⭐ Quality Priority (Best results)
→ Use **llama2** or **dolphin-mixtral**
- Get best analysis quality
- Slightly slower (10-20 sec)
- Worth the wait for important code

### 💲 Resource Constrained (<4GB RAM)
→ Use **openchat** or **orca-mini**
- Minimum footprint
- Still decent quality
- Fast enough

### ⚙️ Balanced (Recommended)
→ Use **mistral**
- Best speed/quality ratio
- Proven in production
- Easy to set up
- 5-10 second analysis

### 🤛 Smart Analysis (Complex code)
→ Use **dolphin-mixtral**
- Understands complex patterns
- Better reasoning
- Slightly slower but worth it

## Performance with GPU

If you have NVIDIA GPU:

```bash
# Enable GPU in docker-compose.yml
services:
  ollama:
    runtime: nvidia  # Add this
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

Speed improvement with GPU:
- CPU: 5-30 seconds per analysis
- GPU: <2-5 seconds per analysis (10x faster!)

## Testing Different Models

```bash
# Pull and test mistral
docker exec ollama ollama pull mistral
docker exec ollama ollama run mistral "What is 2+2?"

# Pull and test llama2
docker exec ollama ollama pull llama2
docker exec ollama ollama run llama2 "What is 2+2?"
```

## Memory Usage

Each model loaded in memory:
- 3B models: ~2GB
- 7B models: ~4GB
- 13B models: ~8GB
- Larger models: ~16GB+

**Tip:** Docker can swap if needed, but it's slow. Add RAM or use smaller model.

## Downloading Models

```bash
# Fast way (concurrent downloads)
for model in mistral llama2 neural-chat; do
  docker exec ollama ollama pull $model &
done
wait

# View download progress
docker logs -f ollama
```

Each model is ~4-8GB. First download takes 5-15 minutes depending on internet.

## Using in Bot

```env
# .env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral  # Change to any model above
```

Then restart bot:

```bash
docker-compose up -d
```

## Switching Models

```bash
# Pull new model
docker exec ollama ollama pull llama2

# Update .env
LOCAL_MODEL=llama2

# Restart bot
docker-compose restart github-commits-bot
```

No need to remove old model - Ollama keeps them all.
