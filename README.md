
# AI Debate Arena

AI Debate Arena is a full-stack application where users can engage in real-time structured debates—either Human vs Human or Human vs AI. It leverages speech-to-text, LLM and NLP-based evaluation, and a point-based scoring system to judge arguments and declare winners.

---

## Features

- Real-time speech and text input
- Two debate modes: Human vs Human and Human vs AI
- Argument evaluation using LLMs (via Groq API with Llama 3 8b)
- Speech-to-Text Transcription using Whisper API
- Debate scoring, winner declaration, and leaderboard
- Debate history and user stats
- Full-stack: FastAPI backend + React frontend + PostgreSQL DB

---

## Tech Stack

- **Frontend**: React.js, HTML/CSS
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL with SQLAlchemy & Alembic
- **AI Tools**: Groq API (LLM), Whisper API (ASR)

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js + npm
- PostgreSQL
- Groq & Whisper API keys

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables

Create a `.env` file in the `backend` directory with the following:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/debates
GROQ_API_KEY=your_groq_api_key
WHISPER_API_KEY=your_whisper_api_key
```

---

## Running Database Migrations

```bash
alembic revision --autogenerate -m "Your message"
alembic upgrade head
```

---

## API Overview

Main endpoints (see full schema in FastAPI docs):

- `POST /debates/` – Start a new debate
- `POST /arguments/` – Submit a new argument
- `GET /leaderboard/` – View current rankings
- `GET /debates/{id}` – Get full debate history

---

## 📷 Project Screenshots:

![image](https://github.com/user-attachments/assets/3ca92b26-9f5b-4b2f-9750-b138bc810270)
![image](https://github.com/user-attachments/assets/0fd06e19-d409-4de4-a8a0-9ea9520cd259)
![image](https://github.com/user-attachments/assets/456dd60b-2393-4bd3-8179-6032ac0ff495)
![image](https://github.com/user-attachments/assets/5b9a9254-15c1-484a-ad3f-b6db0525ffec)

---

