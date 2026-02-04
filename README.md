# Strakly Bot

AI-powered chatbot for Strakly gym management platform using RAG (Retrieval-Augmented Generation).

## Features

- Natural language queries about gym data
- Multi-tenant support (extracts context from JWT)
- Calls existing NestJS backend APIs
- Generates human-like responses using OpenAI
- Temporary conversation memory

## Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env with your values
```

Required environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `BACKEND_API_URL` - NestJS backend URL (e.g., http://localhost:3000/api)
- `JWT_SECRET` - Same JWT secret as your backend

## Run the Application

```bash
uvicorn main:app --reload --port 8001
```

The API will be available at: http://localhost:8001

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| POST | `/chat` | Send chat message |
| DELETE | `/chat/{conversation_id}` | Clear conversation |

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Usage

### Chat Request

```bash
curl -X POST http://localhost:8001/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many active members do I have?",
    "conversation_id": "optional-uuid"
  }'
```

### Response

```json
{
  "success": true,
  "response": "You have 230 active members out of 245 total. 15 members are currently inactive.",
  "conversation_id": "uuid",
  "tools_used": ["get_clients_stats"]
}
```

## Example Questions

- "How many active members do I have?"
- "Show me today's attendance"
- "What's my revenue this month?"
- "List members whose membership expires this week"
- "How many trainers do I have?"
- "Show me pending enquiries"

## Project Structure

```
strakly-bot/
├── main.py                 # FastAPI app & endpoints
├── config.py               # Configuration
├── auth.py                 # JWT decoder
├── agent.py                # LangChain agent
├── models/
│   ├── __init__.py
│   └── schemas.py          # Pydantic models
├── tools/
│   ├── __init__.py
│   ├── base.py             # API client
│   ├── clients.py          # Client tools
│   ├── attendance.py       # Attendance tools
│   ├── revenue.py          # Revenue tools
│   ├── trainers.py         # Trainer tools
│   ├── enquiries.py        # Enquiry tools
│   └── gym.py              # Gym tools
├── prompts/
│   ├── __init__.py
│   └── system_prompt.py    # System prompts
├── docs/
│   └── implementation-plan.md
├── requirements.txt
├── .env.example
└── README.md
```
