# OFFSPACE AI Assistant

> A private, customizable, voice-controlled AI assistant for personal productivity and automation.

**Wake phrase:** `"Hey Offspace"`

## 🎯 Mission

Build a production-quality personal AI assistant that:
- Understands voice commands
- Controls your computer with permission
- Remembers important information
- Works across Windows, Linux, and macOS
- Respects your privacy

## ✨ Features

- **Voice Control** - Wake word detection and natural language understanding
- **Memory System** - Short and long-term memory with knowledge graph
- **Computer Automation** - Application control and file operations
- **Specialized Agents** - Coding, Cybersecurity, Research, Productivity
- **Knowledge Management** - Index and search your personal files

## 🚀 Quick Start

```bash
git clone https://github.com/byiringirojd12-afk/offspace.git
cd offspace
python -m venv venv
# Activate the virtual environment:
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OFFSPACE_SECRET_KEY or JWT_SECRET_KEY to a strong secret
python main.py
```

## 🔧 Backend Setup

1. Copy `.env.example` to `.env`.
2. Set `OFFSPACE_SECRET_KEY` or `JWT_SECRET_KEY` to a strong secret.
3. Set `DATABASE_URL` for your local or production database.
4. Run backend tests with:

```bash
.venv\Scripts\python.exe -m pytest backend/tests -q
```

## 📦 API Startup

Start the backend with:

```bash
.venv\Scripts\python.exe backend/main.py
```

Then visit `http://localhost:8000/api/v1/health`.

## 🎓 Development Phases

- **Phase 1: Core Assistant** ✅ - Project structure, orchestrator, routing
- **Phase 2: Memory System** 🔄 - SQLite storage, persistence
- **Phase 3: Voice System** 🔄 - Speech recognition and synthesis
- **Phase 4: Computer Automation** - Application control
- **Phase 5: Advanced Features** - Plugins, desktop UI

## 🔒 Security & Privacy

- Local-first storage by default
- Encrypted sensitive data
- Permission-based system
- No telemetry without consent

## 📝 License

MIT License - See LICENSE file
