<div align="center">
<svg width="100" height="100" viewBox="0 0 100 100" fill="none">
  <path d="M20 75L50 20L80 75" stroke="#34d399" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" />
  <circle cx="50" cy="55" r="6" fill="#10b981" />
</svg>

# Veonix
**AI-powered nutrition analysis. Upload a meal photo — get instant, accurate nutrition data.**

[![Status](https://img.shields.io/badge/Status-Beta-brightgreen)](https://github.com/mariiammaysara/Veonix)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js_15-000000)](https://nextjs.org/)
[![AI](https://img.shields.io/badge/AI-Gemini_2.5_Flash-4285F4)](https://deepmind.google/technologies/gemini/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Live Demo] · [API Docs] · [Report Bug]
</div>

---

## Features

### Backend
- **Gemini 2.5 Flash Integration**: Leverages Google's latest multimodal AI for simultaneous food identification and nutritional estimation.
- **Clean Architecture**: Modular design separating Controllers, Services, Providers, and Repositories for scalability and testability.
- **Provider Protocol Pattern**: Decoupled AI integration allowing for easy swapping of vision providers (e.g., Gemini, OpenAI, Claude).
- **Repository Pattern**: Centralized data access layer using SQLAlchemy to manage SQLite persistence.
- **Image Optimization**: Automatic compression and normalization using Pillow to minimize API payload size.
- **Advanced Middleware**:
  - `RequestIdMiddleware`: Tracks every request with a unique UUID.
  - `RequestLoggerMiddleware`: Detailed execution logging.
  - `TimingMiddleware`: Measures and logs API performance metrics.
- **Pydantic v2 Validation**: Strict schema enforcement for all incoming requests and outgoing responses.
- **Diagnostics**: Specialized debug endpoint to inspect raw, un-parsed AI model responses.

### Frontend  
- **Next.js 15 App Router**: Built on the latest React framework for optimal performance and SEO.
- **Modern TypeScript**: Strict typing across the entire UI for robust error prevention.
- **Drag & Drop Upload**: Secure and intuitive interface for meal photo submission with real-time preview.
- **Interactive Loading State**: Multi-step real-time progress screen (Scanning image, Identifying ingredients, etc.).
- **Data Visualization**: 
  - Animated macro progress bars (Protein, Carbs, Fat, Fiber).
  - Macro ratio comparison charts.
- **Dynamic UX**: Floating food icon background system that evolves as the user interacts.
- **Meal History**: Persistent dashboard allowing users to track, review, and delete previous meal analyses.
- **Premium Design System**: Dark Emerald aesthetic using high-contrast slate and vibrant brand accents.
- **Micro-animations**: Seamless transitions (fade-up, float, shimmer) powered by Vanilla CSS and Framer Motion logic.

---

## Architecture

### System Flow
```text
  [ User ]                        [ Cloud ]
      |                               |
      v                               v
[ Frontend ] -- (Multipart Image) -> [ FastAPI ] 
    (Next.js)                         (Backend)
                                          |
                                          |-- [ Image Processor ] (Pillow)
                                          |-- [ Vision Provider ] (Gemini API)
                                          |-- [ Data Repository ] (Sqlite/Alchemy)
                                          |
[ Dashboard ] <--- (Analyzed Data) --- [ Controller ]
```

### Backend Layer Diagram
```text
┌───────────────────────────────────────────┐
│              API Controllers              │ (FastAPI Routes)
└─────────────────────┬─────────────────────┘
                      v
┌───────────────────────────────────────────┐
│               Service Layer               │ (MealService)
└─────────────────────┬─────────────────────┘
           ┌──────────┴──────────┐
           v                     v
┌────────────────────┐ ┌────────────────────┐
│ Vision Provider    │ │  Meal Repository   │ (Data Access)
│ (Gemini/Multimodal)│ │ (SQLAlchemy CRUD)  │
└────────────────────┘ └─────────┬──────────┘
                                 v
                       ┌────────────────────┐
                       │     SQLite DB      │ (Persistence)
                       └────────────────────┘
```

### Key Design Decisions
| Decision | Rationale |
| :--- | :--- |
| **Clean Architecture** | Ensures business logic is independent of frameworks (FastAPI) and external agencies (AI APIs). |
| **Provider Protocol** | Allows the app to switch AI models (e.g., from Gemini to OpenAI) by changing a single env variable. |
| **FastAPI + Pydantic** | Provides high-performance asynchronous execution and automatic API documentation. |
| **SQLite with DB Volumes** | Zero-config persistence that works out-of-the-box in Docker and local environments. |

---

## Project Structure
```text
Veonix/
├── backend/                  # FastAPI Application Root
│   ├── src/                  # Application Source Code
│   │   ├── controllers/      # Route handlers (Analyze, Health)
│   │   ├── db/               # Persistence logic (Repository, Database setup)
│   │   ├── enums/            # Shared constants and ErrorCodes
│   │   ├── helpers/          # Utilities (Image compression, Response parser)
│   │   ├── middleware/       # System observability (ID, Logging, Timing)
│   │   ├── models/           # SQLAlchemy DB models
│   │   ├── providers/        # AI Service Integrations (Gemini implementation)
│   │   ├── schemas/          # Pydantic data validation schemas
│   │   ├── services/         # Core business logic orchestration
│   │   ├── main.py           # Application entry point
│   │   └── config.py         # Environmental settings management
│   ├── requirements.txt      # Python package dependencies
│   └── Dockerfile            # Optimized Python container definition
├── frontend/                 # Next.js 15 Application Root
│   ├── app/                  # App Router: Pages, Layouts, and Styles
│   ├── components/           # Reusable UI components (UploadBox, Results)
│   ├── hooks/                # Custom React hooks (Fetch, Form handling)
│   ├── lib/                  # Client-side helpers and API client
│   ├── public/               # Static assets, Icons, and Logos
│   ├── tailwind.config.js    # Design system configuration
│   └── Dockerfile            # Multi-stage production container
├── docker-compose.yml        # Multi-service orchestration config
├── LICENSE                   # MIT License
└── README.md                 # Project Documentation
```

---

## Installation

### Prerequisites
- [Docker & Docker Compose](https://docs.docker.com/get-docker/) (Recommended)
- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 20+](https://nodejs.org/)
- [Gemini API Key](https://aistudio.google.com/app/apikey)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY to .env
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment:
   ```bash
   cp .env.example .env.local
   # Ensure NEXT_PUBLIC_API_URL points to your backend
   ```

### Running the Application

#### Option 1: Local Development
**Terminal 1 (Backend):**
```bash
cd backend
uvicorn src.main:app --reload
```
**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

#### Option 2: Docker
Start the entire stack with one command:
```bash
docker-compose up --build
```
The app will be available at `http://localhost:3000`.

---

## Usage

### Web Interface
1. **Introduction Screen**: A smooth animated entry point explaining the app's purpose.
2. **Upload Interface**: Drag or click to upload a high-quality photo of your meal.
3. **Analysis Engine**: Watch real-time scanning steps as the AI processes the image.
4. **Nutrition Dashboard**: View a detailed breakdown of calories, macros, and ingredients.
5. **History Management**: Re-visit past meals or delete records to clean up your profile.

### API Endpoints

#### POST /analyze/image
Analyzes a multipart image and returns nutrition data.
- **Request**: `multipart/form-data` containing `file`.
- **Response Example**:
```json
{
  "status": "success",
  "data": {
    "food_name": "Chicken Avocado Salad",
    "confidence": 0.94,
    "ingredients": ["Chicken breast", "Avocado", "Mixed greens", "Balsamic dressing"],
    "nutrition": {
      "calories": 450,
      "protein": 32.5,
      "carbs": 12.0,
      "fat": 28.5,
      "fiber": 8.0,
      "sodium": 320
    }
  }
}
```

#### GET /analyze/history
Retrieves paginated meal history.
- **Params**: `limit` (default: 50), `offset` (default: 0).
- **Response**: Array of `MealHistoryItem` objects.

#### GET /analyze/stats
Retrieves average diet stats.
- **Response**: Aggregated averages for calories, protein, carbs, and fat.

#### DELETE /analyze/{id}
Deletes a specific meal record by its unique ID.

#### GET /health
Check system uptime and API connectivity status.

#### POST /debug/vision
Sends image directly to Gemini to see raw AI text output (strictly for developers).

### Error Codes
| Code | HTTP | Description |
| :--- | :--- | :--- |
| `INVALID_IMAGE_FORMAT` | 415 | Unsupported file type (JPEG, PNG, WEBP only). |
| `IMAGE_TOO_LARGE` | 413 | File exceeds 10MB limit. |
| `LOW_CONFIDENCE` | 422 | AI confidence below 50% threshold. |
| `VISION_SERVICE_UNAVAILABLE` | 503 | Upstream Google API is down. |

### Example Usage with cURL
```bash
# Analyze Image
curl -X POST -F "file=@meal.jpg" http://localhost:8000/analyze/image

# Get History
curl http://localhost:8000/analyze/history?limit=10

# Delete Meal
curl -X DELETE http://localhost:8000/analyze/1

# Health Check
curl http://localhost:8000/health
```

### Example Usage with Python
```python
import requests

# Analyze Image
with open('meal.jpg', 'rb') as f:
    r = requests.post('http://localhost:8000/analyze/image', files={'file': f})
    print(r.json())

# Get Stats
stats = requests.get('http://localhost:8000/analyze/stats').json()
print(f"Average Calories: {stats['data']['avg_calories']}")
```

---

## Configuration

### Backend (.env)
| Variable | Default | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | - | Your Google AI Studio API Key. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | The specific model version to use. |
| `DATABASE_URL` | `sqlite:///./veonix.db` | SQLAlchemy database connection string. |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS configuration for frontend. |

### Frontend (.env.local)
| Variable | Default | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | The backend API root URL. |

---

## UI Features

### Design System
- **Palette**: Deep slate background (`#020617`), Emerald brand primary (`#10b981`), Cyan accents (`#22d3ee`).
- **Typography**: Interface utilizes system sans-serif stacks with variable weights for high readability.
- **Glassmorphism**: Cards and overlays use semi-transparent blurs to create depth.

### Components
- **UploadBox**: Multipath upload handler with drag & drop support and type validation.
- **LoadingScreen**: Stepper component synchronized with backend processing phases.
- **ResultsDisplay**: Modular cards for macronutrients, ingredients, and confidence scores.

### Animations
- **Spring Physics**: Hover effects use natural spring curves for a "premium" tactile feel.
- **Staggered Entry**: Macro bars and history items use staggered delays to prevent layout jarring.
- **Shimmer Effects**: Interactive buttons feature subtle light sweeps on hover.

---

## Tech Stack

### Backend
| Technology | Role |
| :--- | :--- |
| **FastAPI** | High-performance API framework. |
| **Pydantic v2** | Data modeling and validation. |
| **SQLAlchemy** | SQL Toolkit and Object Relational Mapper. |
| **Pillow** | Image processing and optimization. |
| **Google GenAI** | Gemini 2.5 Flash / Pro model integration. |

### Frontend
| Technology | Role |
| :--- | :--- |
| **Next.js 15** | Application framework & SSR. |
| **TypeScript** | Type-safe development environment. |
| **Tailwind CSS** | Utility-first styling engine. |
| **Framer Motion** | UI animation and orchestration. |
| **Lucide React** | Premium icon system. |

### DevOps
| Technology | Role |
| :--- | :--- |
| **Docker** | Containerization of services. |
| **Docker Compose** | Multi-container orchestration. |
| **GitHub Actions** | CI/CD automation. |

---

## API Models

### VisionResult
| Field | Type | Description |
| :--- | :--- | :--- |
| `food_name` | `str` | The identified dish name (e.g., "Greek Yogurt Bowl"). |
| `confidence` | `float` | AI confidence score (0.0 to 1.0). |
| `estimated_weight` | `int` | Total meal weight in grams. |
| `nutrients` | `dict` | Breakdown of fat, carbs, protein, fiber, and sodium. |

### NutritionResult
| Field | Type | Description |
| :--- | :--- | :--- |
| `calories` | `float` | Total energy content in kCal. |
| `per_100g` | `dict` | Standardized values for nutritional comparison. |
| `source` | `str` | Always "Gemini" for current implementation. |

---

## Deployment

### Deploy on Render
1. Create a `Web Service` for the **Backend**.
   - Input your `GEMINI_API_KEY` in environment variables.
2. Create a `Static Site` (or Web Service) for the **Frontend**.
   - Set `NEXT_PUBLIC_API_URL` to your backend's URL.

### Deploy with Docker
```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run in detached mode
docker-compose up -d
```

---

## Contributing
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## Author
**Mariam Maysara**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mariam-maysara/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/mariiammaysara)

---

## License
Distributed under the MIT License. See `LICENSE` for more information.