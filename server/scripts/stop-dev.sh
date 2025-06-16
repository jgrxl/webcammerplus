#!/bin/bash

# Stop development environment

echo "🛑 Stopping WebCammer+ Development Environment"

# Stop InfluxDB
echo "📊 Stopping InfluxDB..."
docker-compose down

echo "✅ Development environment stopped"