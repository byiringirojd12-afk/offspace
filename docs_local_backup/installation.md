# Installation

## Requirements
- Python 3.11+ (3.14 recommended)
- Node.js 20+ and npm
- Rust toolchain for Tauri builds

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/byiringirojd12-afk/offspace.git
   cd offspace
   ```
2. Install Python dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   python -m pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   npm install
   ```
4. Copy environment template and configure secrets:
   ```bash
   cp .env.example .env
   # Edit .env and set OFFSPACE_SECRET_KEY or JWT_SECRET_KEY
   ```

## Running Locally
### Python backend
```bash
.venv\Scripts\python.exe main.py
```
### Frontend
```bash
npm run dev
```

## Desktop Application
### Tauri dev
```bash
npm run tauri dev
```

## Notes
- The application is currently a development preview.
- Critical production features such as authentication, cloud sync, and secure installer are not yet completed.
