#!/bin/bash

# Start development environment with InfluxDB

echo "🚀 Starting WebCammer+ Development Environment"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start InfluxDB with Docker Compose
echo "📊 Starting InfluxDB..."
docker-compose up -d influxdb

# Wait for InfluxDB to be healthy
echo "⏳ Waiting for InfluxDB to be ready..."
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose exec -T influxdb influx ping > /dev/null 2>&1; then
        echo "✅ InfluxDB is ready!"
        break
    fi
    
    if [ $counter -eq 30 ]; then
        echo "⏰ Still waiting for InfluxDB..."
    fi
    
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "❌ InfluxDB failed to start within $timeout seconds"
    docker-compose logs influxdb
    exit 1
fi

# Copy local environment file
if [ -f ".env.local" ]; then
    cp .env.local .env
    echo "📝 Using .env.local configuration"
else
    echo "⚠️  .env.local not found, using .env if it exists"
fi

# Show InfluxDB access information
echo ""
echo "🎯 InfluxDB Access Information:"
echo "   URL: http://localhost:8086"
echo "   Username: admin"
echo "   Password: adminpassword"
echo "   Organization: webcammer"
echo "   Bucket: chaturbate_events"
echo "   Token: dev-token-webcammer-plus-2024"
echo ""

# Start the Flask application
echo "🐍 Starting Flask application..."
python app.py