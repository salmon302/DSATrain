# DSATrain Platform Batch Scripts

This directory contains convenient batch scripts to manage the DSATrain platform on Windows.

## Quick Start

1. **First Time Setup**: Run `setup_environment.bat`
2. **Launch Platform**: Run `launch_dsatrain.bat`
3. **Stop Platform**: Run `stop_dsatrain.bat`

## Script Descriptions

### 🚀 `launch_dsatrain.bat`
**Main launcher script** - Starts the complete DSATrain platform.

**What it does:**
- Activates Python virtual environment
- Starts FastAPI backend server on http://localhost:8000
- Starts React frontend on http://localhost:3000
- Opens the application in your default browser
- Runs both servers in separate command windows

**Prerequisites:** Run `setup_environment.bat` first

---

### ⚙️ `setup_environment.bat`
**One-time environment setup** - Prepares your development environment.

**What it does:**
- Creates Python virtual environment (`.venv`)
- Installs all Python dependencies from `requirements.txt`
- Installs Node.js dependencies for the frontend
- Sets up the database with initial migrations
- Validates the installation

**Requirements:**
- Python 3.9+ installed and in PATH
- Node.js 16+ installed and in PATH

---

### 🛑 `stop_dsatrain.bat`
**Platform shutdown script** - Cleanly stops all DSATrain processes.

**What it does:**
- Terminates backend Python/uvicorn processes
- Stops frontend Node.js development server
- Cleans up any remaining processes using ports 3000 and 8000

---

### 🔧 `dev_utils.bat`
**Development utilities menu** - Interactive script for common development tasks.

**Features:**
- Launch full platform or individual components
- Run database migrations
- Reset database (with confirmation)
- Update dependencies
- Run test suite
- View logs
- Open API documentation

## Usage Examples

### First Time Setup
```batch
# Run this once to set up everything
setup_environment.bat

# Then launch the platform
launch_dsatrain.bat
```

### Daily Development
```batch
# Start working
launch_dsatrain.bat

# When done
stop_dsatrain.bat
```

### Development Tasks
```batch
# Interactive development menu
dev_utils.bat
```

## Troubleshooting

### Common Issues

**"Virtual environment not found"**
- Run `setup_environment.bat` first

**"Python is not installed"**
- Install Python 3.9+ from https://python.org/
- Make sure it's added to your PATH

**"Node.js is not installed"**
- Install Node.js 16+ from https://nodejs.org/
- Make sure it's added to your PATH

**Backend won't start**
- Check if port 8000 is already in use
- Run `setup_environment.bat` to install missing dependencies

**Frontend won't start**
- Check if port 3000 is already in use
- Navigate to `frontend/` and run `npm install`

**Database errors**
- Delete `dsatrain_phase4.db` and run `setup_environment.bat`
- Or use the "Reset Database" option in `dev_utils.bat`

### Manual Commands

If the batch scripts don't work, you can run these commands manually:

**Backend:**
```batch
call .venv\Scripts\activate.bat
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```batch
cd frontend
npm start
```

## Platform URLs

When running, the platform will be available at:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Run `setup_environment.bat` to reset the environment
4. Check the main project README.md for additional help

---

**Happy Coding! 🚀**
