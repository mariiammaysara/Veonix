<div align="center">

<img src="frontend/public/veonix-logo.svg" alt="Veonix" width="200"/>

# Veonix

**AI-powered nutrition analysis. Upload a meal photo — get instant, accurate nutrition data.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Live Demo](https://veonix.mariammaysara.com) · [API Docs](https://veonix-api.onrender.com/docs) · [Report Bug](https://github.com/mariiammaysara/Veonix/issues)

</div>

---

## Overview

Veonix is a full-stack AI nutrition dashboard built on a **single-model architecture**: Google Gemini Vision handles both food identification and nutrition calculation in one API call — eliminating the need for external nutrition databases and reducing latency significantly.

The backend follows **Clean Architecture** with strict layer separation. The frontend is built with **Next.js 15 App Router** and communicates exclusively through a typed API client.

---

## Architecture

### System Flow

```
User (image upload)
        │
        ▼
┌───────────────────┐
│   Next.js 15      │  App Router, TypeScript, Tailwind CSS
│   Frontend        │  lib/api.ts → typed API client
└────────┬──────────┘
         │ POST /analyze/image (multipart)
         ▼
┌───────────────────┐
│   FastAPI         │  Python 3.10+, Pydantic, SQLAlchemy
│   Backend         │  Clean Architecture (4 layers)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Google Gemini    │  gemini-2.5-flash
│  Vision API       │  Returns: food_name + full nutrition
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  SQLite DB        │  Meal history, macros, metadata
└───────────────────┘
```

### Backend Layer Diagram

```
controllers/          HTTP interface. Zero business logic.
    │                 Validates input → delegates to service → formats response.
    ▼
services/             Orchestration. Coordinates the pipeline:
    │                 compress image → call provider → save → return.
    ▼
providers/vision/     Gemini integration.
    │                 Protocol-based: swap provider by changing factory.py only.
    ▼
helpers/              Pure utilities.
                      prompts.py — all LLM prompts centralized here.
                      image_processor.py — resize + compress before API call.
                      response_parser.py — validates + deserializes AI output.
    ▼
db/repository.py      Single source of truth for all DB queries.
                      No db.query() calls outside this file.
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single-model (Gemini only) | Eliminates USDA/OFF API dependency, reduces latency, single failure point |
| Provider Protocol pattern | Swap AI providers by changing one file (`factory.py`) without touching services |
| Repository pattern | All SQL isolated in `db/repository.py` — testable, replaceable |
| ErrorCode enum | Single source of truth for HTTP status + user message — no scattered strings |
| `response_mime_type="application/json"` | Forces Gemini to return structured JSON — eliminates regex parsing |

---

## Project Structure

```
Veonix/
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   │   ├── analyze.py          # POST /analyze/image, GET /analyze/history
│   │   │   └── health.py           # GET /health, POST /debug/vision
│   │   ├── services/
│   │   │   └── meal_service.py     # Pipeline orchestration
│   │   ├── providers/
│   │   │   └── vision/
│   │   │       ├── base.py         # VisionProvider Protocol + VisionResult dataclass
│   │   │       ├── gemini_provider.py  # Gemini Vision implementation
│   │   │       └── factory.py      # Provider selection (swap here)
│   │   ├── helpers/
│   │   │   ├── prompts.py          # All LLM prompts — centralized
│   │   │   ├── image_processor.py  # Resize + compress (Pillow)
│   │   │   └── response_parser.py  # Parse + validate Gemini output
│   │   ├── db/
│   │   │   ├── database.py         # Engine, session, init
│   │   │   └── repository.py       # All db.query() calls here only
│   │   ├── models/
│   │   │   └── meal.py             # SQLAlchemy ORM
│   │   ├── schemas/
│   │   │   ├── analyze.py          # AnalysisResponse, MealHistoryItem
│   │   │   └── nutrition.py        # NutritionResponse
│   │   ├── enums/
│   │   │   └── error_codes.py      # ErrorCode enum (code + HTTP status + user message)
│   │   ├── middleware/
│   │   │   ├── request_id.py       # X-Request-ID header
│   │   │   ├── request_logger.py   # Structured request logging
│   │   │   └── timing.py           # X-Process-Time header
│   │   ├── config.py               # Pydantic Settings
│   │   ├── exceptions.py           # VeonixException hierarchy
│   │   └── main.py                 # FastAPI app + lifespan
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── upload/page.tsx     # Upload + results view
│   │   │   └── history/page.tsx    # Meal history
│   │   ├── layout.tsx
│   │   └── page.tsx                # Landing page
│   ├── components/
│   │   ├── upload-box.tsx          # Drag & drop file upload
│   │   ├── results-display.tsx     # Nutrition breakdown card
│   │   ├── LoadingScreen.tsx       # Analysis in-progress view
│   │   └── error-card.tsx          # Standardized error display
│   ├── hooks/
│   │   └── use-meal-history.ts     # Fetch + delete history state
│   ├── lib/
│   │   ├── api.ts                  # All fetch() calls — nowhere else
│   │   ├── types.ts                # MealResult, NutritionData, MealHistoryItem
│   │   └── error-utils.ts          # ApiError → UserFriendlyError mapping
│   ├── .env.example
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## API Reference

### `POST /analyze/image`

Analyzes a food image and returns full nutrition data.

**Request:** `multipart/form-data`

| Field | Type | Required |
|-------|------|----------|
| `file` | image (JPEG/PNG/WEBP, max 10MB) | ✅ |

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "food_name": "Chicken Shawarma Platter",
    "confidence": 0.95,
    "ingredients": ["chicken", "pita", "tahini", "vegetables"],
    "weight_grams": 500,
    "meal_type": "lunch",
    "cuisine": "Middle Eastern",
    "nutrition": {
      "calories": 900,
      "protein": 65,
      "carbs": 90,
      "fat": 40,
      "fiber": 4,
      "sodium": 1250,
      "per_100g": { "calories": 180, "protein": 13, "carbs": 18, "fat": 8, "fiber": 0.8, "sodium": 250 },
      "source": "Gemini",
      "is_estimated": false
    }
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "LOW_CONFIDENCE",
    "message": "Couldn't identify the food clearly. Try a clearer photo with better lighting.",
    "detail": "confidence=42%"
  }
}
```

### Error Codes

| Code | HTTP | When |
|------|------|------|
| `INVALID_IMAGE_FORMAT` | 415 | File is not JPEG/PNG/WEBP |
| `IMAGE_TOO_LARGE` | 413 | File exceeds 10MB |
| `IMAGE_CORRUPTED` | 422 | File cannot be processed |
| `VISION_SERVICE_UNAVAILABLE` | 503 | Gemini API unreachable |
| `LOW_CONFIDENCE` | 422 | AI confidence below threshold |
| `NO_FOOD_DETECTED` | 422 | No food visible in image |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analyze/history` | Paginated meal history (`?limit=50&offset=0`) |
| `GET` | `/analyze/stats` | Average macros across all meals |
| `DELETE` | `/analyze/{id}` | Delete a meal by ID |
| `GET` | `/health` | Service health + Gemini API status |
| `POST` | `/debug/vision` | Raw Gemini response (dev only) |

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API key — [get one free at aistudio.google.com](https://aistudio.google.com/app/apikey)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

cp .env.example .env
# Add your GEMINI_API_KEY to .env

uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

### Docker

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Environment Variables

**Backend (`backend/.env`)**

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Required. [Get free key](https://aistudio.google.com/app/apikey) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `DATABASE_URL` | `sqlite:///./veonix.db` | SQLAlchemy connection string |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS whitelist |
| `DEBUG` | `false` | Enable debug mode |

**Frontend (`frontend/.env.local`)**

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend base URL |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend framework | Next.js 15 (App Router) |
| UI | React 19, Tailwind CSS v4, Shadcn/ui |
| Backend framework | FastAPI |
| Language | Python 3.10+, TypeScript |
| AI Model | Google Gemini 2.5 Flash |
| Database | SQLite via SQLAlchemy |
| Validation | Pydantic v2 |
| Image processing | Pillow |
| Deployment | Docker, Render / Oracle Cloud |

---

## Author

**Mariam Maysara** — Full-Stack AI Engineer

[![Portfolio](https://img.shields.io/badge/Portfolio-mariammaysara.com-10b981?style=flat)](https://mariammaysara.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mariam--maysara-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/mariam-maysara)
[![GitHub](https://img.shields.io/badge/GitHub-mariiammaysara-181717?style=flat&logo=github)](https://github.com/mariiammaysara)

---

## License

This project is open source and available under the terms of the **MIT License**. See the `LICENSE` file for more details.

---

## Author

<p align="center">
  <strong>Developed by Mariam Maysara</strong>
</p>