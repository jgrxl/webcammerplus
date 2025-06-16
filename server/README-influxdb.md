# InfluxDB Development Setup

This project uses InfluxDB for time-series analytics of Chaturbate events. For local development, we use Docker to run InfluxDB.

## Quick Start

### 1. Start Development Environment
```bash
# This will start InfluxDB and the Flask app
./scripts/start-dev.sh
```

### 2. Stop Development Environment
```bash
./scripts/stop-dev.sh
```

## Manual Setup

### 1. Start InfluxDB with Docker
```bash
docker-compose up -d influxdb
```

### 2. Verify InfluxDB is Running
```bash
# Check if container is healthy
docker-compose ps

# Test connection
curl -i http://localhost:8086/ping
```

### 3. Access InfluxDB UI
- Open http://localhost:8086 in your browser
- Username: `admin`
- Password: `adminpassword`

### 4. Start Flask Application
```bash
# Make sure .env.local is copied to .env
cp .env.local .env
python app.py
```

## Configuration

### Environment Variables (`.env.local`)
```bash
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=dev-token-webcammer-plus-2024
INFLUXDB_ORG=webcammer
INFLUXDB_BUCKET=chaturbate_events
```

### Docker Configuration
- **Image**: `influxdb:2.7`
- **Port**: `8086`
- **Data**: Persisted in Docker volumes
- **Auto-setup**: Organization, bucket, and admin user created automatically

## Data Structure

### Measurements
- `chaturbate_events` - All Chaturbate events

### Tags
- `method` - Event type (tip, chatMessage, etc.)
- `username` - User who triggered the event

### Fields
- `object.tip.tokens` - Tip amount in tokens
- `object.user.username` - Username
- `object.tip.message` - Tip message
- `object.message` - Chat message

## Useful Commands

### View Logs
```bash
docker-compose logs influxdb
```

### Connect to InfluxDB CLI
```bash
docker-compose exec influxdb influx
```

### Reset Data (Clean Start)
```bash
docker-compose down -v  # This removes volumes
docker-compose up -d influxdb
```

### Backup Data
```bash
docker-compose exec influxdb influx backup /tmp/backup
docker cp $(docker-compose ps -q influxdb):/tmp/backup ./influx-backup
```

## Troubleshooting

### Port 8086 Already in Use
```bash
# Check what's using the port
lsof -i :8086

# Stop any existing InfluxDB
brew services stop influxdb  # if installed via Homebrew
```

### Connection Refused
- Make sure Docker is running
- Check if InfluxDB container is healthy: `docker-compose ps`
- View logs: `docker-compose logs influxdb`

### Data Not Persisting
- Check Docker volumes: `docker volume ls`
- Verify volume mounts in `docker-compose.yml`