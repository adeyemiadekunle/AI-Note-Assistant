# AI Note-Taking Assistant Backend

AI-powered backend service that records meetings, generates transcripts, summarises key themes, extracts action items, and prepares mind-map friendly data structures. Built with FastAPI, Whisper, GPT, and MongoDB.
Summarisation now uses a LangChain agent that orchestrates OpenAI chat models to produce structured JSON notes.

## Getting Started

### Prerequisites
- Python 3.11+
- MongoDB instance (local or Atlas)

### Installation

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate # On macOS/Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the required secrets before running the application.

Key environment variables:
- `OPENAI_API_KEY` / `OPENAI_MODEL` configure the LLM used for summarisation.
- `WHISPER_MODEL_SIZE` selects the Whisper checkpoint (`tiny`, `base`, `small`, etc.).
- `MONGO_URI` should point at your MongoDB instance (Docker Compose sets this automatically).
- `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES` configure bearer token issuance.

### Run the API

```bash
uvicorn app.main:app --reload
```

The interactive docs are available at `http://127.0.0.1:8000/docs` when the server is running.

### Run with Docker Compose

Ensure your `.env` file exists. Then start the API and MongoDB services together:

```bash
docker compose up --build
```

The FastAPI app will be available on `http://127.0.0.1:8000` and MongoDB will listen on `mongodb://localhost:27017`.

## API Endpoints (Preview)
- `POST /api/upload-audio` - Accept audio uploads for transcription.
- `POST /api/summarise` - Generate summaries, actions, and topics from transcripts.
- `POST /api/auth/signup` - Register a new user and receive a bearer token.
- `POST /api/auth/login` - Authenticate and receive a bearer token.
- `GET /api/auth/me` - Fetch the profile for the current bearer token.
- `GET /api/notes` - List stored notes (backed by MongoDB).
- `GET /api/mindmap/{id}` - Retrieve mind map data for a given note.

### Authentication

Routes under `/api/notes` and `/api/mindmap` require an `Authorization: Bearer <token>` header issued by the signup/login endpoints.

### Tests

```bash
pytest
```

## Project Layout

Key directories are outlined in PROJECT_STRUCTURE.md and mirror the intended implementation phases for the assistant.
