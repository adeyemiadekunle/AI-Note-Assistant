# AI Note-Taking Assistant - Backend Development Blueprint

FastAPI + Whisper + GPT + MongoDB stack for recording, transcribing, and summarising lectures or meetings. This document outlines objectives, structure, dependencies, and development phases for both human developers and LLM assistants.

## 1. Project Objectives
- Convert spoken lectures or meetings into accurate transcripts (dialect-aware).
- Use LLMs to summarise, extract key actions, and shape mind-map data.
- Store results in MongoDB for retrieval and dashboard visualisation.
- Provide a REST API for frontend or external integrations (Notion, Calendar).

## 2. Core Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Framework | FastAPI | RESTful backend API |
| Database | MongoDB via `motor` | Asynchronous NoSQL data store |
| Speech-to-Text | Whisper / `openai-whisper` | Transcribe audio |
| NLP Layer | GPT-5 API via LangChain | Summarisation and action extraction |
| Storage | Local, AWS S3, or Firebase | Audio file storage |
| Auth | JWT / `fastapi-users` | Secure access |
| Visualisation | React, Mermaid.js | Mind maps (later phase) |

## 3. Folder Structure

```text
ai_note_assistant_backend/
|-- app/
|   |-- main.py
|   |-- config.py
|   |-- routes/
|   |   |-- audio.py
|   |   |-- notes.py
|   |   |-- auth.py
|   |   `-- nlp.py
|   |-- services/
|   |   |-- auth_service.py
|   |   |-- whisper_service.py
|   |   |-- nlp_service.py
|   |   |-- mindmap_service.py
|   |   `-- note_service.py
|   |-- middleware/
|   |   `-- auth_middleware.py
|   |-- models/
|   |   |-- user_model.py
|   |   `-- note_model.py
|   |-- database/
|   |   `-- mongodb.py
|   `-- utils/
|       |-- s3_upload.py
|       `-- helpers.py
|-- tests/
|   |-- test_auth.py
|   |-- test_transcription.py
|   |-- test_nlp.py
|   |-- test_routes_audio.py
|   `-- test_routes_nlp.py
|-- requirements.txt
|-- .env.example
|-- Dockerfile
|-- docker-compose.yml
|-- .gitignore
|-- README.md
|-- PROJECT_STRUCTURE.md
`-- AGENTS.md
```

## 4. Key Dependencies

```text
fastapi
uvicorn
pydantic
pydantic-settings
python-multipart
motor
pymongo
openai
openai-whisper
torch
langchain
langchain-openai
passlib[bcrypt]
python-jose[cryptography]
python-dotenv
boto3
fastapi-users
networkx
```

## 5. Environment Variables

```env
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
MONGO_URI=mongodb://mongo:27017/ai_note_assistant
DATABASE_NAME=ai_note_assistant
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
S3_BUCKET=your_bucket_name
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
WHISPER_MODEL_SIZE=base
```

## 6. Core Modules

### whisper_service.py
Loads the Whisper model and handles transcription.

### nlp_service.py
Uses GPT models to summarise transcripts and extract action items.

### mindmap_service.py
Transforms structured summaries into JSON for front-end mind-map rendering.

### auth_service.py
Handles password hashing, JWT creation, and user authentication helpers.

### note_model.py
Pydantic model capturing transcripts, summaries, topics, actions, and mind-map payloads.

### mongodb.py
Initialises the async MongoDB client and exposes helpers for database access.

## 7. API Endpoints Summary

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/upload-audio` | POST | Upload audio, transcribe via Whisper |
| `/api/summarise` | POST | Summarise transcript and extract actions |
| `/api/notes` | GET / POST | Retrieve or create notes |
| `/api/notes/{id}` | GET / PUT / DELETE | Manage a single note |
| `/api/auth/signup` | POST | User registration |
| `/api/auth/login` | POST | User login |
| `/api/auth/me` | GET | Fetch the current authenticated user |
| `/api/mindmap/{id}` | GET | Retrieve mind map JSON |

## 8. Run and Deploy

### Local Development
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker Compose (API + MongoDB)
```bash
docker compose up --build
```

MongoDB will be reachable at `mongodb://localhost:27017` while the FastAPI service listens on port `8000`.

### Docker Deployment
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 9. Development Phases

1. Speech-to-text: `/upload-audio` endpoint plus Whisper integration.
2. Summarisation: `/summarise` endpoint backed by GPT-5.
3. Persistence: MongoDB models and CRUD APIs.
4. Mind map builder: JSON graph output via `networkx`.
5. Authentication: JWT-based user login/signup.
6. Integration: Notion, Google Calendar APIs.
7. Deployment: Docker, hosting on Render or AWS.

## 10. Future Enhancements
- Speaker diarisation.
- Accent fine-tuning for Whisper.
- Offline transcription mode.
- Mobile app (React Native) for recording and syncing.
- Supervisor feedback tracker with versioned meeting logs.

## 11. References
- OpenAI Whisper: https://github.com/openai/whisper
- FastAPI: https://fastapi.tiangolo.com
- Motor: https://motor.readthedocs.io
- LangChain: https://python.langchain.com
