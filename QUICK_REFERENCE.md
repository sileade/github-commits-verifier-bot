# Quick Reference - Common Commands

## Startup

```bash
# First time only
./setup.sh

# Every time
./start.sh
```

## Monitoring

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f github-commits-bot

# All logs
docker-compose logs -f

# Bot logs only
docker-compose logs -f github-commits-bot --tail=20
```

## Control

```bash
# Restart
./restart.sh

# Stop
./stop.sh

# Rebuild
docker-compose build --no-cache
./start.sh
```

## Database

```bash
# Connect
docker exec -it github-commits-postgres psql -U github_bot -d github_verifier

# Backup
docker exec github-commits-postgres pg_dump -U github_bot github_verifier > backup.sql

# Size
docker exec -it github-commits-postgres psql -U github_bot -d github_verifier \
  -c "SELECT pg_size_pretty(pg_database_size('github_verifier'));"
```

## Ollama (if enabled)

```bash
# List models
docker exec ollama ollama list

# Pull model
docker exec ollama ollama pull llama2

# Test
docker exec ollama ollama run mistral "echo test"
```

## Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data!)
docker-compose down -v

# Prune unused images
docker image prune -a

# Remove dangling volumes
docker volume prune
```

## Troubleshooting

```bash
# Recent logs
docker-compose logs --tail=50

# Error logs
docker-compose logs | grep -i error

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
./start.sh

# Detailed status
docker-compose ps -a
```

## Configuration

```bash
# View .env
cat .env

# Edit .env
nano .env

# Reload after edit
./restart.sh
```

## Testing

```bash
# Test local LLM
python test-local-llm.py

# Test database
docker exec github-commits-bot python -c "print('OK')"

# Container shell
docker exec -it github-commits-bot /bin/bash
```
