<div align="center">
  <img src="assets/logo.svg" width="120" alt="Veonix Logo">
  <h1>Veonix</h1>
  <p><strong>AI-powered nutrition analysis. Upload a meal photo — get instant, accurate nutrition data.</strong></p>

  [![Status](https://img.shields.io/badge/Status-Beta-brightgreen)](https://github.com/mariiammaysara/Veonix)
  [![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
  [![Frontend](https://img.shields.io/badge/Frontend-Next.js_15-000000)](https://nextjs.org/)
  [![AI](https://img.shields.io/badge/AI-Gemini_2.5_Flash-4285F4)](https://deepmind.google/technologies/gemini/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

  [Live Demo](https://veonix.mariammaysara.com/) · [API Docs](https://veonix-api.onrender.com/docs) · [Report Bug](https://github.com/mariiammaysara/Veonix/issues)
</div>

---

##  Features

###  Backend
- **Gemini 2.5 Flash Integration**: Google's latest multimodal AI for food identification and nutrition estimation.
- **Clean Architecture**: Modular design (Controllers, Services, Providers, Repositories).
- **Provider Protocol Pattern**: Easily swap vision providers (Gemini, OpenAI, etc.).
- **Repository Pattern**: Centralized data access using SQLAlchemy and SQLite.
- **Image Optimization**: Automatic compression and normalization via Pillow.
- **Middleware Stack**: Request tracing, detailed logging, and performance timing.
- **Pydantic v2**: Strict schema validation for robust API contracts.
- **Supervisor Routing & Vision Retry Loop**: Orchestrates subgraphs (vision, history, knowledge) with automatic low-confidence detection and retries.
- **Persistent Memory & Alembic Migrations**: Manages user profiles (goals/allergies) and history via LangGraph Store and robust schema versioning.

###  Frontend
- **Next.js 15 App Router**: High-performance React framework for optimal UX.
- **Modern TypeScript**: End-to-end type safety for reliable development.
- **Drag & Drop Upload**: Secure, intuitive interface with real-time image preview.
- **Interactive Loading**: Multi-step real-time progress indicator during analysis.
- **Data Visualization**: Animated macro progress bars and nutrition ratio charts.
- **Premium Design System**: Dark Emerald aesthetic with deep slate and vibrant accents.
- **Micro-animations**: Seamless transitions (fade-up, float, shimmer) via CSS.

---
## ⚠️ Known Limitations

- Portion estimation from images is inherently unreliable without a reference scale.
- Current approach relies on AI estimation (Gemini Vision), which may produce inaccurate weights.
- Future improvement: user-assisted portion input or reference-based estimation.
---
##  Architecture

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

---

##  Tech Stack

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

##  Installation

### Prerequisites
- [Docker & Docker Compose](https://docs.docker.com/get-docker/) (Recommended)
- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 20+](https://nodejs.org/)
- [Gemini API Key](https://aistudio.google.com/app/apikey)

### Running with Docker
Start the entire stack with one command:
```bash
docker-compose up --build
```
The app will be available at `http://localhost:3000`.

---

### Deploy with Docker
```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run in detached mode
docker-compose up -d
```
---
## 🔌 MCP Server

Veonix exposes a Model Context Protocol (MCP) server to allow direct integration of your meal history logs and current stats with Claude Desktop or other MCP-compatible clients.

### Capabilities Exposed:
- **Tool**: `get_meal_history(limit, offset)` — Fetches the list of user meals (sorted newest first), including calories and macronutrient splits.
- **Resource**: `nutrition://stats` — Provides real-time aggregated nutrition stats (averages and meal count).

### Claude Desktop Configuration

To install and use this MCP server in Claude Desktop, add the following to your configuration file (located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "veonix": {
      "command": "python",
      "args": [
        "c:/Users/Mariam Hagag/Desktop/veonix/Veonix/backend/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "c:/Users/Mariam Hagag/Desktop/veonix/Veonix/backend",
        "DATABASE_URL": "sqlite:///c:/Users/Mariam Hagag/Desktop/veonix/Veonix/backend/veonix.db"
      }
    }
  }
}
```

*Note: Ensure `python` is in your system PATH and environment dependencies (including `mcp` and `sqlalchemy`) are fully installed.*

---
## ⚠️ Database Migrations & Deployment Notes

- **Alembic Database Migrations**: `alembic upgrade head` is now a required deployment step to synchronize the database schema before the application starts. The Docker container executes this automatically on startup. If deploying manually, run:
  ```bash
  alembic upgrade head
  ```
- Backend is deployed on Render (free tier)
- First request may take ~30–60 seconds due to cold start
---

## Contributing
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request.
---

## License
Distributed under the MIT License. See `LICENSE` for more information.

---

## Author
<p align="center">
  © Built by <b>Mariam Maysara</b>
</p>
