# Project Startup Guide

## Initial Setup

### Backend

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running the Project

### Backend

```bash
# Activate venv if not already active
source venv/bin/activate

pip install -r requirements.txt
pip install fastapi sse-starlette uvicorn

# Start server
python server/app.py
```

### Frontend

npm i

```bash
cd frontend
npm run dev
```

## Notes

- Backend runs on the default Flask port (usually 5000)
- Frontend development server will display the local URL after starting
