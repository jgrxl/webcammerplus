# WebCammer+ Development Setup

Quick start guide for running the WebCammer+ application locally.

## Prerequisites

- **Node.js** (for frontend)
- **Python 3.10+** (for backend)
- **Docker** (for InfluxDB)

## 🚀 Quick Start

### 1. Start InfluxDB
```bash
# IMPORTANT: Must be in the server directory!
cd server
docker compose up -d influxdb
```
*Wait for InfluxDB to be ready (about 30 seconds)*

### 2. Start Backend (Server)
```bash
cd server
source .venv/bin/activate  # Activate virtual environment
cp .env.local .env         # Copy local config
python app.py              # Start Flask server
```
*You should see: "✅ InfluxDB connection successful"*

### 3. Start Frontend (Extension)
```bash
cd sider
npm run serve              # Start Vite development server
```
*OR open `sider/index.html` directly in browser*

## 📍 Access Points

- **Frontend**: http://localhost:3000 (or check npm output)
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs/
- **InfluxDB UI**: http://localhost:8086
  - Username: `admin`
  - Password: `adminpassword`

## 🛑 Stop Everything

### Stop InfluxDB
```bash
cd server
docker compose down
```

### Stop Backend
```
Ctrl+C in the terminal running app.py
```

### Stop Frontend
```
Ctrl+C in the terminal running npm run serve
```

## 📂 Project Structure

```
webcammer+/
├── server/           # Flask backend
│   ├── app.py       # Main server file
│   ├── .env.local   # Local environment config
│   └── docker-compose.yml
└── sider/           # Vue.js frontend extension
    └── package.json
```

## ✅ Verification Steps

After starting all services, verify everything is working:

### 1. Check InfluxDB
```bash
# In server directory
docker compose ps
# Should show "webcammer-influxdb" as running

# Test connection
curl http://localhost:8086/ping
# Should return "pong"
```

### 2. Check Backend
- Visit http://localhost:5000 - should return `{"status": "ok"}`
- Visit http://localhost:5000/docs/ - should show API documentation
- Check terminal for "✅ InfluxDB connection successful"

### 3. Check Frontend
- Open browser to frontend URL (shown in npm output)
- Click the "Attach" button at bottom
- Should see "Connected to Chaturbate" message
- Events should start appearing in the tabs

## ⚡ Development Workflow

1. Start InfluxDB first (only needs to be done once)
2. Start backend in one terminal
3. Start frontend in another terminal
4. Open extension in browser and click "Attach" to connect to Chaturbate events

## 🔧 Troubleshooting

**"no such service: influxdb" error:**
```bash
# Make sure you're in the server directory!
cd server
docker compose up -d influxdb
```

**Docker not running:**
```bash
# Start Docker Desktop application first
```

**Port conflicts:**
- InfluxDB: 8086
- Backend: 5000
- Frontend: varies (check npm output)

**InfluxDB connection failed:**
- Make sure Docker is running
- Check: `docker compose ps` in server directory
- Restart: `docker compose restart influxdb`

**Python dependencies:**
```bash
cd server
source .venv/bin/activate
pip install -r requirements.txt
```

**InfluxDB client missing:**
```bash
cd server
source .venv/bin/activate
pip install influxdb-client
```

**Node dependencies:**
```bash
cd sider
npm install
```