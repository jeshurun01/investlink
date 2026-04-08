#!/usr/bin/env bash
# Stop script for InvestLink Django Application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Stopping InvestLink Application${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if PID file exists
if [ ! -f .server.pid ]; then
    echo -e "${YELLOW}⚠️  No server PID file found${NC}"
    echo -e "${YELLOW}   Server may not be running${NC}"
    echo ""
    
    # Try to find Django runserver process
    echo -e "${BLUE}🔍 Searching for Django runserver processes...${NC}"
    DJANGO_PIDS=$(pgrep -f "manage.py runserver" || echo "")
    
    if [ -z "$DJANGO_PIDS" ]; then
        echo -e "${GREEN}✓ No Django server processes found${NC}"
        exit 0
    else
        echo -e "${YELLOW}   Found Django processes: $DJANGO_PIDS${NC}"
        echo -e "${YELLOW}   Attempting to stop them...${NC}"
        
        for PID in $DJANGO_PIDS; do
            kill -TERM $PID 2>/dev/null && echo -e "${GREEN}✓ Stopped process $PID${NC}" || echo -e "${RED}✗ Failed to stop process $PID${NC}"
        done
        exit 0
    fi
fi

# Read PID from file
PID=$(cat .server.pid)

# Check if process is running
if ! ps -p $PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Server process (PID: $PID) not found${NC}"
    echo -e "${YELLOW}   Cleaning up PID file...${NC}"
    rm .server.pid
    echo -e "${GREEN}✓ PID file removed${NC}"
    exit 0
fi

# Stop the server gracefully
echo -e "${BLUE}⏹️  Stopping server (PID: $PID)...${NC}"

# Try SIGTERM first (graceful shutdown)
kill -TERM $PID 2>/dev/null

# Wait up to 5 seconds for process to stop
TIMEOUT=5
COUNTER=0

while ps -p $PID > /dev/null 2>&1 && [ $COUNTER -lt $TIMEOUT ]; do
    sleep 1
    COUNTER=$((COUNTER + 1))
    echo -e "${YELLOW}   Waiting for server to stop... ($COUNTER/${TIMEOUT})${NC}"
done

# Check if process stopped
if ps -p $PID > /dev/null 2>&1; then
    echo -e "${RED}⚠️  Server did not stop gracefully, forcing shutdown...${NC}"
    kill -KILL $PID 2>/dev/null
    sleep 1
fi

# Verify process is dead
if ps -p $PID > /dev/null 2>&1; then
    echo -e "${RED}✗ Failed to stop server${NC}"
    exit 1
else
    rm .server.pid
    echo -e "${GREEN}✓ Server stopped successfully${NC}"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Server has been stopped${NC}"
    echo -e "${BLUE}========================================${NC}"
fi
