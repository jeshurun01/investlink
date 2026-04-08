# InvestLink Server Management Scripts

## Quick Start

### Starting the Server

```bash
./start.sh
```

This will:
- ✅ Build Tailwind CSS (minified)
- ✅ Run database migrations
- ✅ Start the Django development server on http://127.0.0.1:8000
- ✅ Save the process ID for easy stopping
- ✅ Collect static files (only in production mode)

### Stopping the Server

```bash
./stop.sh
```

This will:
- ✅ Gracefully stop the running Django server
- ✅ Clean up process ID files
- ✅ Force kill if graceful shutdown fails

---

## Advanced Usage

### Custom Port

Start the server on a different port:

```bash
PORT=8080 ./start.sh
```

### Custom Host

Bind to a specific host (e.g., for network access):

```bash
HOST=0.0.0.0 PORT=8000 ./start.sh
```

### Production Mode with Static Files

```bash
COLLECT_STATIC=true ./start.sh
```

Or set environment variable:

```bash
export DJANGO_ENV=production
./start.sh
```

---

## Tailwind CSS

### Automatic Building

The `start.sh` script automatically builds Tailwind CSS before starting the server using:

```bash
npm run build:css
```

This compiles `static/css/input.css` to `static/css/output.css` (minified).

### Manual CSS Building

Build CSS manually:

```bash
npm run build:css
```

### Watch Mode (Development)

For automatic rebuilding on file changes during development:

```bash
npm run watch:css
```

Run this in a separate terminal while developing. It watches for changes in:
- `templates/**/*.html`
- `static/js/**/*.js`
- All app templates

### Updating Browser Support Data

If you see a browserslist warning, update it (optional):

```bash
npx update-browserslist-db@latest
```

---

## Troubleshooting

### Server already running

If you see "Server already running", use:

```bash
./stop.sh
./start.sh
```

### Port already in use

Change the port:

```bash
PORT=8080 ./start.sh
```

### Finding running servers manually

```bash
ps aux | grep "manage.py runserver"
```

### Killing all Django servers

```bash
pkill -f "manage.py runserver"
```

---

## Features

### start.sh
- 🎨 Builds Tailwind CSS automatically
- 🎨 Colorized output for better visibility
- 🔄 Automatic migration application
- 🛡️ Prevents multiple instances
- 📝 Saves PID for easy management
- ⚡ Fast startup with uv
- 🎯 Supports Ctrl+C to stop

### stop.sh
- 🛑 Graceful shutdown (SIGTERM)
- ⚡ Force kill if needed (SIGKILL)
- 🧹 Automatic cleanup of PID files
- 🔍 Finds orphaned Django processes
- 📊 Progress indication during shutdown

---

## Files Created

- **start.sh** - Main startup script
- **stop.sh** - Shutdown script
- **.server.pid** - Process ID file (auto-generated, don't commit)

## Important Notes

1. **Add to .gitignore**: Make sure `.server.pid` is in your `.gitignore` file
2. **Development Only**: These scripts are for development. For production, use gunicorn/uwsgi
3. **Virtual Environment**: Scripts use `uv run` to manage the Python environment
4. **Background Execution**: The server runs in the background until stopped

---

## Example Workflow

```bash
# Start the server
./start.sh

# Do your development work
# Server is accessible at http://127.0.0.1:8000

# Stop when done
./stop.sh
```

## Integration with Your Workflow

### VS Code Tasks

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Django Server",
      "type": "shell",
      "command": "./start.sh",
      "problemMatcher": []
    },
    {
      "label": "Stop Django Server",
      "type": "shell",
      "command": "./stop.sh",
      "problemMatcher": []
    }
  ]
}
```

### Makefile (Optional)

```makefile
start:
	./start.sh

stop:
	./stop.sh

restart: stop start

.PHONY: start stop restart
```

Then use: `make start`, `make stop`, or `make restart`
