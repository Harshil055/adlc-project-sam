# Todo API - ADLC Test Project

Simple FastAPI Todo application for testing the ADLC platform.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn main:app --reload --port 8080

# Test it
curl http://localhost:8080/
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /todos` - Create a todo
- `GET /todos` - List all todos
- `GET /todos/{id}` - Get specific todo
- `PUT /todos/{id}` - Update a todo
- `DELETE /todos/{id}` - Delete a todo

## Testing in ADLC

This project is designed to test the ADLC platform with real tickets. See `SAMPLE_ISSUES.md` for GitHub issues you can create.
