#!/bin/bash
# WebCammerPlus Platform Launcher
# This script starts all required services for the platform

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ╦ ╦┌─┐┌┐ ╔═╗┌─┐┌┬┐┌┬┐┌─┐┬─┐╔═╗┬  ┬ ┬┌─┐                  ║
║  ║║║├┤ ├┴┐║  ├─┤│││││││├┤ ├┬┘╠═╝│  │ │└─┐                  ║
║  ╚╩╝└─┘└─┘╚═╝┴ ┴┴ ┴┴ ┴└─┘┴└─╩  ┴─┘└─┘└─┘                  ║
║                                                              ║
║              AI-Powered Webcam Platform                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for $service_name to be ready...${NC}"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $service_name is ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}✗ $service_name failed to start${NC}"
    return 1
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    # Kill backend if running
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill frontend if running
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop Docker containers
    cd server && docker-compose down
    
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

# Set trap for cleanup on exit
trap cleanup EXIT INT TERM

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Python
if ! command_exists python3; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"

# Check Docker
if ! command_exists docker; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check ports
echo -e "\n${BLUE}Checking port availability...${NC}"

if port_in_use 5000; then
    echo -e "${RED}✗ Port 5000 is already in use (Backend)${NC}"
    echo "Please stop the service using port 5000 or change the backend port"
    exit 1
fi
echo -e "${GREEN}✓ Port 5000 is available (Backend)${NC}"

if port_in_use 5173; then
    echo -e "${RED}✗ Port 5173 is already in use (Frontend)${NC}"
    echo "Please stop the service using port 5173 or change the frontend port"
    exit 1
fi
echo -e "${GREEN}✓ Port 5173 is available (Frontend)${NC}"

if port_in_use 8086; then
    echo -e "${YELLOW}! Port 8086 is in use (InfluxDB) - will use existing instance${NC}"
else
    echo -e "${GREEN}✓ Port 8086 is available (InfluxDB)${NC}"
fi

# Start InfluxDB
echo -e "\n${BLUE}Starting InfluxDB...${NC}"
cd server

if ! port_in_use 8086; then
    docker-compose up -d
    wait_for_service "http://localhost:8086/health" "InfluxDB"
else
    echo -e "${YELLOW}InfluxDB appears to be running already${NC}"
fi

# Check environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file - please configure your API keys${NC}"
    else
        echo -e "${RED}✗ No .env or .env.example file found${NC}"
        exit 1
    fi
fi

# Install Python dependencies if needed
if [ ! -d "venv" ] && [ ! -f "../.venv/bin/activate" ]; then
    echo -e "\n${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    # Activate existing venv
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "../.venv/bin/activate" ]; then
        source ../.venv/bin/activate
    fi
fi

# Start Backend
echo -e "\n${BLUE}Starting Backend Server...${NC}"
python3 app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
wait_for_service "http://localhost:5000/" "Backend API"

# Start Frontend
echo -e "\n${BLUE}Starting Frontend Development Server...${NC}"
cd ../sider

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
fi

# Start frontend dev server
npm run serve > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to be ready
wait_for_service "http://localhost:5173/" "Frontend"

# Display status
echo -e "\n${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ WebCammerPlus Platform is running!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Services:${NC}"
echo -e "  📊 InfluxDB:     ${GREEN}http://localhost:8086${NC}"
echo -e "  🔧 Backend API:  ${GREEN}http://localhost:5000${NC}"
echo -e "  🌐 Frontend:     ${GREEN}http://localhost:5173${NC}"
echo -e "  📚 API Docs:     ${GREEN}http://localhost:5000/docs${NC}"

echo -e "\n${BLUE}Quick Actions:${NC}"
echo -e "  • View API documentation: ${YELLOW}open http://localhost:5000/docs${NC}"
echo -e "  • Open frontend: ${YELLOW}open http://localhost:5173${NC}"
echo -e "  • View logs: ${YELLOW}tail -f backend.log${NC} or ${YELLOW}tail -f frontend.log${NC}"
echo -e "  • Stop all services: ${YELLOW}Press Ctrl+C${NC}"

echo -e "\n${BLUE}Test Pages:${NC}"
echo -e "  • Integration Test: ${YELLOW}http://localhost:5173/test-integration.html${NC}"
echo -e "  • API Test: ${YELLOW}http://localhost:5173/test-all-frontend-api-calls.html${NC}"

# Check for missing API keys
echo -e "\n${BLUE}Configuration Status:${NC}"
cd ../server
source .env 2>/dev/null || true

if [ -z "$AUTH0_DOMAIN" ] || [ "$AUTH0_DOMAIN" = "your-auth0-domain.auth0.com" ]; then
    echo -e "  ${YELLOW}⚠ Auth0 not configured - authentication features disabled${NC}"
else
    echo -e "  ${GREEN}✓ Auth0 configured${NC}"
fi

if [ -z "$STRIPE_SECRET_KEY" ] || [ "$STRIPE_SECRET_KEY" = "sk_test_your_stripe_secret_key" ]; then
    echo -e "  ${YELLOW}⚠ Stripe not configured - payment features disabled${NC}"
else
    echo -e "  ${GREEN}✓ Stripe configured${NC}"
fi

if [ -z "$NOVITA_API_KEY" ] || [ "$NOVITA_API_KEY" = "your-novita-api-key-here" ]; then
    echo -e "  ${YELLOW}⚠ Novita AI not configured - AI features disabled${NC}"
else
    echo -e "  ${GREEN}✓ Novita AI configured${NC}"
fi

echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Keep script running and show logs
tail -f ../backend.log ../frontend.log