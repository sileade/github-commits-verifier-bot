# 🤖 Local LLM Setup Guide (Ollama)

## Why Use Local LLM?

| Feature | Local Ollama | OpenAI Cloud |
|---------|---|---|
| **Cost** | 💲 **FREE** | ~$0.0005 per analysis |
| **Privacy** | 🔐 100% local | Cloud-based |
| **Speed** | ⚡⚡ 5-30 sec (CPU) or <2 sec (GPU) | 2-5 seconds |
| **Quality** | ⭐⭐⭐⭐ Good (Mistral, Llama2) | ⭐⭐⭐⭐⭐ Excellent |
| **Internet** | ❌ Not required | Required |
| **Control** | 🔐 Full local control | Cloud service |
| **Off-the-shelf** | ✓ Ready to use | Requires API |

**Bottom line:** Local LLM is perfect for privacy-conscious teams and cost-effective deployments!

---

## Quick Start (Docker)

### 1. Start Ollama Container

```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama
```

### 2. Pull a Model

```bash
# Mistral (recommended - fast & good)
docker exec ollama ollama pull mistral

# Or Llama2 (slower but higher quality)
docker exec ollama ollama pull llama2
```

### 3. Configure Bot

Add to `.env`:

```env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://localhost:11434
LOCAL_MODEL=mistral
```

Or in Docker, use container hostname:

```env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral
```

### 4. Start Bot

```bash
docker-compose up -d
```

That's it! 🌟

---

## Model Comparison

### Recommended Models

```
🎉 MISTRAL (7B) - RECOMMENDED
├─ Speed: ⚡⚡⚡ (super fast)
├─ Quality: ⭐⭐⭐⭐ (very good)
├─ RAM: 4GB
└─ Best for: Speed + quality balance

🔏 LLAMA2 (7B)
├─ Speed: ⚡⚡ (medium)
├─ Quality: ⭐⭐⭐⭐⭐ (excellent)
├─ RAM: 4GB
└─ Best for: High quality results

🗨 NEURAL-CHAT (7B)
├─ Speed: ⚡⚡⚡ (very fast)
├─ Quality: ⭐⭐⭐⭐ (very good)
├─ RAM: 4GB
└─ Best for: Chat-optimized

🚀 DOLPHIN-MIXTRAL (8.7B MoE)
├─ Speed: ⚡⚡ (fast)
├─ Quality: ⭐⭐⭐⭐⭐ (excellent, smart)
├─ RAM: 5GB
└─ Best for: Complex analysis

🥪 OPENCHAT (3.5B)
├─ Speed: ⚡⚡⚡⚡ (ultra-fast)
├─ Quality: ⭐⭐⭐ (acceptable)
├─ RAM: 2GB
└─ Best for: Minimal resources

🤦 ZEPHYR (7B)
├─ Speed: ⚡⚡ (medium)
├─ Quality: ⭐⭐⭐⭐ (very good)
├─ RAM: 4GB
└─ Best for: General purpose
```

**TL;DR:** Start with **Mistral** - it's fast, free, and effective! 🚀

---

## Installation Methods

### Method 1: Docker (Recommended)

**Requirements:** Docker

```bash
# Start Ollama
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# Pull model
docker exec ollama ollama pull mistral

# Verify
docker exec ollama ollama list
```

**With GPU (NVIDIA):**

```bash
docker run -d \
  --name ollama \
  --gpus all \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama
```

### Method 2: Local Installation

**Requirements:** Local Ollama

1. Download from [ollama.ai](https://ollama.ai)
2. Install for your OS
3. Run Ollama:
   ```bash
   ollama serve
   ```
4. In another terminal:
   ```bash
   ollama pull mistral
   ```

### Method 3: Docker Compose (Full Stack)

Add to `docker-compose.yml`:

```yaml
services:
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

volumes:
  ollama_data:
    driver: local
```

Then:

```bash
docker-compose up -d ollama
docker-compose exec ollama ollama pull mistral
docker-compose up -d  # Start all services
```

---

## Performance Tips

### With GPU (Much Faster!)

**NVIDIA CUDA:**

```bash
# Install NVIDIA Docker runtime
sudo apt-get install nvidia-docker2

# Update docker-compose
services:
  ollama:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all

# Start
docker-compose up -d
```

**Speed improvement:**
- CPU only: 5-30 seconds per analysis
- With GPU: <2-5 seconds per analysis (10x faster!)

### Memory Optimization

**If you have < 8GB RAM:**

```env
# Use smaller/faster model
LOCAL_MODEL=mistral  # Fast, 7B
# or
LOCAL_MODEL=neural-chat  # Fast, 7B
# or
LOCAL_MODEL=openchat  # Ultra-light, 3.5B
```

**If you have >= 8GB RAM:**

```env
# Use higher quality model
LOCAL_MODEL=llama2  # Best quality, 7B
# or
LOCAL_MODEL=dolphin-mixtral  # Smart, 8.7B
```

---

## Configuration

### Minimal Setup (Local)

```env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://localhost:11434
LOCAL_MODEL=mistral
```

### Docker Setup

```env
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434  # Use container hostname
LOCAL_MODEL=mistral
```

### Advanced Setup (Hybrid)

```env
# Use both OpenAI and Local
OPENAI_API_KEY=sk-...
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral

# Bot will auto-select best option
# (local for speed, OpenAI for quality)
```

---

## Troubleshooting

### "Connection refused"

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Or in Docker
curl http://ollama:11434/api/tags

# If error, restart
docker restart ollama
```

### "Model not found"

```bash
# List available models
docker exec ollama ollama list

# Pull missing model
docker exec ollama ollama pull mistral
```

### "Timeout" or "Very slow"

**Option 1: Reduce model size**

```bash
# Pull smaller model
docker exec ollama ollama pull neural-chat

# Update .env
LOCAL_MODEL=neural-chat
```

**Option 2: Add GPU support**

```bash
# See GPU section above
```

### "Out of memory"

```bash
# Check available RAM
free -h

# Use lighter model
docker exec ollama ollama pull openchat
LOCAL_MODEL=openchat  # 3.5B, minimal
```

---

## Usage Examples

### Check Health

```python
from local_analyzer import LocalAnalyzer

local_ai = LocalAnalyzer()
if await local_ai.check_ollama_health():
    print("✓ Ready!")
else:
    print("⚠️ Ollama not available")
```

### Analyze Commit

```python
analysis = await local_ai.analyze_diff(diff_text, commit_message)

if analysis:
    print(f"Summary: {analysis['summary']}")
    print(f"Impact: {analysis['impact']}")
    print(f"Recommendation: {analysis['recommendation']}")
```

### Security Analysis

```python
security = await local_ai.analyze_security(diff_text)

if security:
    print(security['security_analysis'])
```

---

## Cost Comparison

```
Local Ollama:          💲 $0.00 per analysis
   Initial setup: 1-2 hours
   Hardware: GPU $200-2000+ (optional)
   Monthly: $0 (after initial setup)

OpenAI GPT-3.5:        💵 $0.0005 per analysis
   Monthly for 1000 commits: $0.50
   Monthly for 10000 commits: $5.00

OpenAI GPT-4:          💶 $0.03 per analysis
   Monthly for 1000 commits: $30
   Monthly for 10000 commits: $300
```

**If you do 1000+ commits/month, Local Ollama pays for itself!** 🌟

---

## Hybrid Setup (Best of Both)

**Idea:** Use Local for speed, OpenAI for quality

```env
OPENAI_API_KEY=sk-...
USE_LOCAL_MODEL=true
OLLAMA_HOST=http://ollama:11434
LOCAL_MODEL=mistral
```

**Bot behavior:**
1. Try local Mistral first (instant, free)
2. If slow/unavailable, fallback to OpenAI
3. User never waits, never pays unnecessarily

**Code:**

```python
from hybrid_ai_manager import HybridAIManager, AnalysisMode

manager = HybridAIManager(openai_analyzer, local_analyzer)

# Auto-select best option
analysis = await manager.analyze_diff(
    diff, message,
    prefer_fast=True  # Prefer local (faster)
)

# Or force specific mode
analysis = await manager.analyze_diff(
    diff, message,
    mode=AnalysisMode.LOCAL  # Force local
)
```

---

## Advanced: Fine-tuning

You can fine-tune models on your team's standards:

```bash
# Create training data
cat > training.txt << EOF
Good code:
- Clear variable names
- Proper error handling
- Tests included

Bad code:
- Single letter variables
- No error handling
- No tests
EOF

# Fine-tune (requires Ollama CLI)
ollama create my-model -f Modelfile
```

See [Ollama Custom Models](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) for details.

---

## System Requirements

### Minimum (3.5B model like OpenChat)
- CPU: Modern multi-core
- RAM: 2GB available
- Storage: 4GB
- Speed: 30-60 sec per analysis

### Recommended (7B model like Mistral)
- CPU: Modern multi-core
- RAM: 4-8GB available
- Storage: 8GB
- Speed: 5-15 sec per analysis (CPU)

### Ideal (7B with GPU)
- GPU: NVIDIA RTX 3060+ or better
- RAM: 8GB+ available
- Storage: 12GB
- Speed: <2-5 sec per analysis (GPU)

---

## Next Steps

1. 📄 Choose a model (start with Mistral)
2. 📁 Install Ollama
3. 🚀 Pull the model
4. ⚙️ Configure .env
5. 🌟 Start bot and enjoy free AI analysis!

**Questions?** Check [local_analyzer_integration.md](local_analyzer_integration.md) for detailed docs.
