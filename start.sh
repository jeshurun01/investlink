#!/usr/bin/env bash
# Start script for InvestLink Django Application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting InvestLink Application${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if PID file exists and server is already running
if [ -f .server.pid ]; then
    PID=$(cat .server.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Server already running on PID $PID${NC}"
        echo -e "${YELLOW}   Use ./stop.sh to stop it first${NC}"
        exit 1
    else
        # PID file exists but process is dead, remove it
        rm .server.pid
    fi
fi

# Step 1: Build Tailwind CSS
echo -e "${BLUE}🎨 Building Tailwind CSS...${NC}"
if command -v npm > /dev/null 2>&1; then
    npm run build:css
    echo -e "${GREEN}✓ Tailwind CSS built successfully${NC}"
else
    echo -e "${YELLOW}⚠️  npm not found, skipping Tailwind build${NC}"
    echo -e "${YELLOW}   Install Node.js and npm to enable CSS building${NC}"
fi
echo ""

# Step 2: Run migrations
echo -e "${BLUE}📦 Running database migrations...${NC}"
uv run python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations applied${NC}"
echo ""

# Step 3: Collect static files (optional for development)
if [ "$DJANGO_ENV" = "production" ] || [ "$COLLECT_STATIC" = "true" ]; then
    echo -e "${BLUE}📁 Collecting static files...${NC}"
    uv run python manage.py collectstatic --noinput
    echo -e "${GREEN}✓ Static files collected${NC}"
    echo ""
fi

# Step 4: Start the server
echo -e "${BLUE}🚀 Starting development server...${NC}"
echo -e "${GREEN}   Server will run at: http://${HOST}:${PORT}${NC}"
echo -e "${YELLOW}   Press Ctrl+C to stop the server${NC}"
echo ""

# Start server in background and save PID
uv run python manage.py runserver ${HOST}:${PORT} &
SERVER_PID=$!
echo $SERVER_PID > .server.pid

# Wait a moment to check if server started successfully
sleep 2

if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server started successfully (PID: $SERVER_PID)${NC}"
    echo -e "${GREEN}  Access the application at: http://${HOST}:${PORT}${NC}"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Server is running in background${NC}"
    echo -e "${BLUE}  Use ./stop.sh to stop the server${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Wait for the process (so Ctrl+C will work)
    wait $SERVER_PID
else
    echo -e "${RED}✗ Failed to start server${NC}"
    rm .server.pid
    exit 1
fi
