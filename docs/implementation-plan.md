# Strakly Bot - RAG Implementation Plan

## Overview

A FastAPI-based chatbot that uses RAG (Retrieval-Augmented Generation) to answer tenant-specific questions by querying the existing NestJS backend APIs and generating human-like responses using OpenAI.

---

## Architecture

```
┌─────────────────┐      ┌─────────────────────────────────────────────┐
│   Frontend      │      │            strakly-bot (FastAPI)            │
│   (Chat UI)     │      │                                             │
│                 │ JWT  │  ┌─────────────┐    ┌──────────────────┐   │
│  User Message   │─────►│  │  /chat API  │───►│  LangChain Agent │   │
│                 │      │  └─────────────┘    └────────┬─────────┘   │
│                 │      │                              │             │
│                 │      │         ┌────────────────────┼─────────┐   │
│                 │      │         │      Tools         ▼         │   │
│                 │      │         │  ┌─────────────────────────┐ │   │
│                 │      │         │  │ get_clients            │ │   │
│                 │      │         │  │ get_attendance         │ │   │
│                 │      │         │  │ get_revenue_stats      │ │   │
│                 │      │         │  │ get_memberships        │ │   │
│                 │      │         │  │ get_trainers           │ │   │
│                 │      │         │  │ get_enquiries          │ │   │
│                 │      │         │  │ ...more tools          │ │   │
│                 │      │         │  └───────────┬─────────────┘ │   │
│                 │      │         └──────────────┼───────────────┘   │
│                 │      │                        │                   │
└─────────────────┘      └────────────────────────┼───────────────────┘
                                                  │ JWT (forwarded)
                                                  ▼
                                    ┌─────────────────────────────┐
                                    │   strakly_backend (NestJS)  │
                                    │       Port 3000             │
                                    │                             │
                                    │   /api/clients              │
                                    │   /api/attendance           │
                                    │   /api/memberships          │
                                    │   /api/reports              │
                                    │   /api/trainers             │
                                    │   /api/enquiries            │
                                    │   ...                       │
                                    └─────────────────────────────┘
```

---

## Flow

1. **User sends message** with JWT token from frontend
2. **Bot extracts tenant context** from JWT (gymId, userId, role)
3. **LangChain Agent** analyzes the question and decides which tools to use
4. **Tools call NestJS APIs** with the same JWT token for authentication
5. **Data is retrieved** and passed back to the agent
6. **OpenAI generates** a human-like response based on the data
7. **Response sent** back to frontend

---

## API Endpoints

### POST /chat

Main chat endpoint for conversation.

**Request:**
```json
{
  "message": "How many active members do I have?",
  "conversation_id": "optional-uuid-for-context"
}
```

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "response": "You currently have 245 active clients.",
  "conversation_id": "uuid",
  "tools_used": ["get_clients_stats"]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Tools (LangChain)

Tools that the agent can use to fetch data from NestJS backend:

| Tool | Description | Backend API |
|------|-------------|-------------|
| `get_clients_stats` | Get client statistics | GET /api/clients/stats |
| `get_clients_list` | Get list of clients with filters | GET /api/clients |
| `get_attendance_today` | Get today's attendance | GET /api/attendance/today |
| `get_attendance_stats` | Get attendance statistics | GET /api/attendance/stats |
| `get_revenue_stats` | Get revenue/financial stats | GET /api/reports/income-expense |
| `get_memberships_expiring` | Get expiring memberships | GET /api/memberships?status=expiring |
| `get_memberships_stats` | Get membership statistics | GET /api/memberships/stats |
| `get_trainers_list` | Get trainers list | GET /api/trainers |
| `get_enquiries` | Get enquiry/leads list | GET /api/enquiries |
| `get_gym_info` | Get gym information | GET /api/gyms/me |
| `get_subscription_info` | Get SaaS subscription | GET /api/saas-subscriptions/me |

---

## Project Structure

```
strakly-bot/
├── main.py                 # FastAPI app & endpoints
├── config.py               # Configuration & env loader
├── auth.py                 # JWT decoder & tenant extraction
├── agent.py                # LangChain agent orchestrator
├── tools/
│   ├── __init__.py
│   ├── base.py             # Base tool with API client
│   ├── clients.py          # Client tools
│   ├── attendance.py       # Attendance tools
│   ├── revenue.py          # Revenue/financial tools
│   ├── memberships.py      # Membership tools
│   ├── trainers.py         # Trainer tools
│   ├── enquiries.py        # Enquiry tools
│   └── gym.py              # Gym tools
├── prompts/
│   └── system_prompt.py    # System prompts for agent
├── models/
│   └── schemas.py          # Pydantic models
├── docs/
│   ├── implementation-plan.md
│   └── user_guide.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## Dependencies

```
fastapi
uvicorn[standard]
langchain
langchain-openai
langchain-core
httpx
python-dotenv
pyjwt
```

---

## Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-your-key

# Backend API
BACKEND_API_URL=http://localhost:3000/api

# JWT (same secret as backend)
JWT_SECRET=your-jwt-secret

# App
APP_ENV=development
LOG_LEVEL=INFO
```

---

## Example Conversations

### Example 1: Client Count
**User:** "How many active clients do I have?"

**Agent thinks:** Need to get client statistics
**Tool called:** `get_clients_stats`
**API Response:** `{"total": 245, "active": 230, "inactive": 15}`

**Bot Response:** "You have 230 active clients out of 245 total. 15 clients are currently inactive."

---

### Example 2: Today's Attendance
**User:** "Show me today's attendance"

**Agent thinks:** Need attendance data for today
**Tool called:** `get_attendance_today`
**API Response:** `{"total": 89, "checkIns": [...], "peakHour": "6:00 PM"}`

**Bot Response:** "Today you've had 89 check-ins so far. The peak hour was 6:00 PM with 23 clients checking in."

---

### Example 3: Revenue
**User:** "What's my revenue this month?"

**Agent thinks:** Need financial/revenue data
**Tool called:** `get_revenue_stats`
**API Response:** `{"thisMonth": 125000, "lastMonth": 118000, "growth": 5.9}`

**Bot Response:** "Your revenue this month is ₹1,25,000. That's a 5.9% increase compared to last month (₹1,18,000)."

---

### Example 4: Expiring Memberships
**User:** "Which clients' subscriptions are expiring this week?"

**Agent thinks:** Need expiring membership data
**Tool called:** `get_memberships_expiring`
**API Response:** `{"expiring": [{"name": "John", "expiresAt": "..."}, ...]}`

**Bot Response:** "You have 12 memberships expiring this week:
1. John Doe - expires Feb 6
2. Jane Smith - expires Feb 7
..."

---

## Implementation Steps

### Phase 1: Setup (Current)
- [x] Create FastAPI project
- [x] Create docs folder
- [ ] Add dependencies
- [ ] Setup environment config

### Phase 2: Core
- [ ] Implement JWT decoder (auth.py)
- [ ] Create base API client for tools
- [ ] Implement LangChain agent

### Phase 3: Tools
- [ ] Implement client tools
- [ ] Implement attendance tools
- [ ] Implement revenue tools
- [ ] Implement membership tools
- [ ] Implement other tools

### Phase 4: Integration
- [ ] Create /chat endpoint
- [ ] Test with frontend
- [ ] Add conversation history (optional)

### Phase 5: Enhancement
- [ ] Add rate limiting
- [ ] Add caching for common queries
- [ ] Add conversation memory

---

## Backend API Requirements

**IMPORTANT:** The bot depends on these NestJS backend endpoints. Verify they exist or create them.

### Required Endpoints (Need to Verify/Create)

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/clients` | GET | ✅ Likely exists | List clients with filters |
| `/api/clients/stats` | GET | ⚠️ Verify | Total, active, inactive counts |
| `/api/attendance/today` | GET | ⚠️ Verify | Today's check-ins |
| `/api/attendance/stats` | GET | ⚠️ Verify | Attendance trends, peak hours |
| `/api/memberships/expiring` | GET | ⚠️ Verify | Memberships expiring in X days |
| `/api/reports/income-expense` | GET | ✅ Likely exists | Revenue stats |
| `/api/reports/membership-sales` | GET | ⚠️ Verify | Membership sales stats |
| `/api/trainers` | GET | ✅ Likely exists | List trainers |
| `/api/trainers/stats` | GET | ⚠️ Verify | Trainer statistics |
| `/api/enquiries` | GET | ✅ Likely exists | List enquiries |
| `/api/enquiries/stats` | GET | ⚠️ Verify | Enquiry statistics |
| `/api/gyms/me` | GET | ⚠️ Verify | Current gym info |
| `/api/products/sales/:id` | DELETE | ✅ New | Void/delete a sale |
| `/api/products/sales/batch/:paymentId` | DELETE | ✅ New | Void/delete sales by payment |

### Expected Response Formats

**GET /api/clients/stats**
```json
{
  "total": 245,
  "active": 230,
  "inactive": 15,
  "newThisMonth": 12
}
```

**GET /api/attendance/today**
```json
{
  "total": 89,
  "checkIns": [...],
  "currentlyIn": 12,
  "peakHour": "18:00"
}
```

**GET /api/attendance/stats?period=week**
```json
{
  "averageDaily": 75,
  "total": 525,
  "peakDay": "Monday",
  "peakHour": "18:00"
}
```

### JWT Token Payload (Expected Structure)

```json
{
  "sub": 123,
  "userId": 123,
  "gymId": 1,
  "role": "admin",
  "email": "user@gym.com",
  "name": "John Doe"
}
```

⚠️ **Verify** these fields exist in your JWT token payload.

---

## Security Considerations

1. **JWT Validation**: Validate JWT token before processing
2. **Token Forwarding**: Forward same JWT to backend APIs (maintains auth context)
3. **Role-based Access**: Bot only returns data user has permission to see
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Input Sanitization**: Sanitize user input before processing

---

## Questions for Implementation

1. Should we store conversation history in database for context?
2. Do you want streaming responses (typing effect)?
3. Should the bot handle multiple languages?
4. Any specific response format preferences (markdown, plain text)?
