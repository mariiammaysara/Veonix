# ✦ V E O N I X

<div align="center">
  <img src="https://github.com/user-attachments/assets/95c08bcd-c765-4d1e-9cbf-950f3d06a3a6" alt="Veonix Header" width="100%" />
</div>

> **Unlock the data in your diet.** Veonix combines advanced computer vision with nutritional science to provide instant, detailed breakdowns of your meals.

---

## Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Design System](#design-system)
- [Installation & Setup](#installation--setup)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Introduction

**Veonix** is an intelligent, AI-powered dietary companion designed to simplify nutrition tracking. By leveraging state-of-the-art **Vision Language Models (VLMs)**, Veonix "sees" your food, identifying complex dishes, estimating portion sizes, and calculating macronutrients with remarkable accuracy.

Unlike traditional calorie trackers that require tedious manual entry, Veonix allows users to simply upload a photo of their meal. The system instantly analyzes the image, deconstructs the ingredients, and provides a comprehensive nutritional breakdown (Calories, Protein, Carbs, Fat).

Veonix features a robust **dual-model architecture**:
- **Primary Engine**: **Qwen 2.5-VL (7B Instruct)**, chosen for its superior multimodal reasoning and visual understanding capabilities.
- **Fallback Engine**: **LLaVA v1.6 (Mistral 7B)**, ensuring high availability and reliability even if the primary service encounters latency or downtime.

Designed for bio-hackers, fitness enthusiasts, and anyone seeking a frictionless health tracking experience, Veonix transforms the way we interact with our food data.

---

## Key Features

### Key Features Overview

| Category | Feature | Description |
| :--- | :--- | :--- |
| **Visual AI** | **Instant Recognition** | Identifies thousands of global dishes, from complex curries to simple salads, in milliseconds. |
| | **Dual-Model Reliability** | Implements a sophisticated failover mechanism between **Qwen 2.5-VL** and **LLaVA v1.6** to guarantee service continuity. |
| | **Ingredient Deconstruction** | Breaks down composite meals into their core ingredients for granular nutritional analysis. |
| | **Portion Estimation** | AI-driven analysis estimates quantity and volume to provide accurate caloric counts. |
| **Frontend** | **Glassmorphism Design** | A visually stunning interface featuring glassmorphism effects, floating background elements, and smooth transitions. |
| | **Fully Responsive** | Optimized for all devices—Desktop, Tablet, and Mobile. |
| | **Interactive Upload** | Drag-and-drop zone with instant image previews, validation, and visual feedback. |
| | **Local History Tracking** | Automatically saves analyzed meals to the browser's local storage, ensuring data persistence without requiring user accounts. |
| | **Privacy-First** | No extensive user data collection; the application functions as a public, anonymous tool. |
| **Analytics** | **Real-Time Macro Breakdown** | Instant calculation of key macronutrients: Protein, Carbohydrates, Fats, and Total Calories. |
| | **Health Scoring** | Auto-generated health scores and insights for every analyzed meal. |

---

## System Architecture

Veonix utilizes a modern, **decoupled architecture** designed for speed, scalability, and maintainability.

1.  **Client Layer (Frontend)**: Built with **Next.js 15 (App Router)** and **React 19**, styled with **Tailwind CSS v4**. It handles user interactions, image uploads, and state management via local storage.
2.  **API Layer (Backend)**: Powered by **FastAPI**, a high-performance Python web framework. It acts as the secure orchestrator between the client and the AI models.
3.  **Intelligence Layer (AI)**: Integrates with the **Hugging Face Inference API** to access powerful Vision Language Models.
4.  **Storage Layer**: Uses **SQLite** for structured data storage (transactional records) and browser **LocalStorage** for user-facing history.

### Workflow:
1.  User uploads an image via the Next.js frontend.
2.  The request is sent to the FastAPI backend (`/analyze/image`).
3.  The backend validates the image and routes it to the **FoodAnalyzer Service**.
4.  The service queries **Qwen 2.5-VL**. If it fails or times out, it seamlessly falls back to **LLaVA v1.6**.
5.  The AI response is parsed, normalized into a structured JSON format, and stored in the database.
6.  The result is returned to the frontend and displayed to the user.

---

## Project Structure

Below is the exhaustive file structure of the Veonix codebase, with descriptions for each significant component.

```graphql
Veonix/
├── backend/                              # Python FastAPI Backend Application
│   ├── app/                              # Main application source code
│   │   ├── core/                         # Core logical components and configuration
│   │   │   ├── middleware/               # HTTP Middleware configurations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── request_id.py         # Assigns unique IDs to requests
│   │   │   │   ├── request_logger.py     # Logs request details
│   │   │   │   └── timing.py             # Performance monitoring middleware
│   │   │   ├── routers/                  # API Route Definitions
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analyze.py            # Endpoints for image analysis & history
│   │   │   │   └── health.py             # Service health check endpoint
│   │   │   ├── schemas/                  # Pydantic Models for Data Validation
│   │   │   │   ├── __init__.py
│   │   │   │   └── analyze.py            # Request/Response schemas for analysis
│   │   │   ├── services/                 # Business Logic & External Integrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── food_analysis.py      # Core logic for nutrition calculation
│   │   │   │   └── vision.py             # Integration with Hugging Face Inference API
│   │   │   ├── utils/                    # Helper utilities
│   │   │   │   ├── __init__.py
│   │   │   │   └── image_processing.py   # Image resizing and format utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py                 # Application configuration & env loading
│   │   │   ├── database.py               # SQLAlchemy database session management
│   │   │   ├── error_handler.py          # Global exception handlers
│   │   │   └── logging_config.py         # Logger configuration
│   │   ├── models/                       # SQLAlchemy ORM Database Models
│   │   │   ├── __init__.py
│   │   │   └── meal.py                   # Model definition for 'meals' table
│   │   ├── __init__.py
│   │   └── main.py                       # FastAPI entry point & app initialization
│   ├── .env.example                      # Template for backend environment variables
│   ├── .gitignore                        # Backend-specific git exclusion rules
│   ├── Dockerfile                        # Instructions to containerize the backend
│   └── requirements.txt                  # List of Python dependencies
│
├── frontend/                             # Next.js React Frontend Application
│   ├── app/                              # Next.js App Router Directory
│   │   ├── dashboard/                    # Dashboard Section
│   │   │   ├── history/
│   │   │   │   └── page.tsx              # Page: User Meal History
│   │   │   └── upload/
│   │   │   │   └── page.tsx              # Page: Image Upload & Analysis
│   │   ├── intro/
│   │   │   └── page.tsx                  # Page: Introduction/Onboarding flow
│   │   ├── loading/
│   │   │   └── page.tsx                  # Page: Global loading state
│   │   ├── favicon.ico                   # Website favicon
│   │   ├── globals.css                   # Global CSS imports & Tailwind directives
│   │   ├── layout.tsx                    # Root layout (fonts, metadata, footer)
│   │   └── page.tsx                      # Page: Main Landing Page
│   ├── components/                       # Reusable React UI Components
│   │   ├── ui/                           # Primitive UI components (buttons, cards, etc.)
│   │   │   ├── button.tsx                # Button component
│   │   │   └── ... (shadcn/ui items)
│   │   ├── app-sidebar.tsx               # Application sidebar navigation
│   │   ├── chart-area-interactive.tsx    # Interactive charting component
│   │   ├── data-table.tsx                # Reusable data table component
│   │   ├── error-card.tsx                # Standardized error display card
│   │   ├── image-preview.tsx             # Component to preview uploaded images
│   │   ├── IntroScreen.tsx               # Initial brand intro animation
│   │   ├── LoadingScreen.tsx             # Analysis in-progress animation
│   │   ├── nav-main.tsx                  # Main navigation links
│   │   ├── nav-user.tsx                  # User profile navigation
│   │   ├── navbar.tsx                    # Top navigation bar
│   │   ├── results-display.tsx           # Visual card for nutritional results
│   │   ├── upload-box.tsx                # Drag & drop file upload zone
│   │   └── veonix-logo.tsx               # SVG Logo component
│   ├── lib/                              # Utility Functions & Libraries
│   │   ├── api.ts                        # API client wrappers for backend communication
│   │   ├── error-utils.ts                # Error formatting and handling helpers
│   │   └── utils.ts                      # General helper functions (e.g. cn for tailwind)
│   ├── public/                           # Static Public Assets
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── .env.example                      # Template for frontend environment variables
│   ├── .gitignore                        # Frontend-specific git exclusion rules
│   ├── components.json                   # shadcn/ui configuration file
│   ├── Dockerfile                        # Instructions to containerize the frontend
│   ├── next.config.ts                    # Next.js framework configuration
│   ├── package.json                      # Node.js dependencies & scripts
│   ├── postcss.config.js                 # PostCSS configuration
│   ├── tailwind.config.ts                # Tailwind CSS configuration
│   └── tsconfig.json                     # TypeScript compiler configuration
│
├── .gitignore                            # Root-level git exclusion rules
├── LICENSE                               # MIT License file
└── README.md                             # Main project documentation
```

---

## Technology Stack

### Frontend
| Technology | Description |
| :--- | :--- |
| **[Next.js 15](https://nextjs.org/)** | React Framework with App Router & Server Actions |
| **[React 19](https://react.dev/)** | Library for building user interfaces |
| **[TypeScript](https://www.typescriptlang.org/)** | Statically typed JavaScript superset |
| **[Tailwind CSS v4](https://tailwindcss.com/)** | Utility-first CSS framework for rapid UI development |
| **[Lucide React](https://lucide.dev/)** | Beautiful & consistent icon library |
| **[Geist Font](https://vercel.com/font)** | Modern sans-serif font family by Vercel |

### Backend
| Technology | Description |
| :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | Modern, high-performance web framework for building APIs with Python |
| **[Python 3.10+](https://www.python.org/)** | Core programming language |
| **[SQLAlchemy](https://www.sqlalchemy.org/)** | SQL Toolkit and Object Relational Mapper |
| **[Pydantic](https://docs.pydantic.dev/)** | Data validation and settings management using Python type hints |
| **[SQLite](https://www.sqlite.org/)** | C-language library that implements a small, fast, self-contained SQL database engine |
| **[Uvicorn](https://www.uvicorn.org/)** | Lightning-fast ASGI server implementation |

### Artificial Intelligence
| Component | Model / Service | Description |
| :--- | :--- | :--- |
| **Inference Provider** | **[Hugging Face Inference API](https://huggingface.co/inference-api)** | Serverless inference for state-of-the-art models |
| **Primary VLM** | **[Qwen 2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)** | High-performance Vision-Language Model for detailed image analysis |
| **Fallback VLM** | **[LLaVA v1.6-Mistral-7B](https://huggingface.co/llava-hf/llava-v1.6-mistral-7b-hf)** | Robust backup model ensuring reliability during outages |

---

## Design System

Veonix features a carefully curated design system built on **Tailwind CSS**.

### Color Palette

| Color Name | Hex Code | Utility Class | Usage |
| :--- | :--- | :--- | :--- |
| **Deep Slate** | `#0f172a` | `bg-slate-900` | Primary application background. |
| **Darker Slate** | `#020617` | `bg-slate-950` | Footer, sidebar, and deep background layers. |
| **Brand Emerald** | `#10b981` | `text-emerald-500` | Primary brand color, actions, success states. |
| **Highlight Green** | `#34d399` | `text-emerald-400` | Hover states, glowing effects, accents. |
| **Text Primary** | `#f8fafc` | `text-slate-50` | Main headings and high-contrast text. |
| **Text Secondary** | `#94a3b8` | `text-slate-400` | Subtitles, captions, and secondary information. |
| **Border Line** | `#334155` | `border-slate-700` | Subtle dividers and card borders. |

### Typography

Veonix uses the **Geist** font family by Vercel for a modern, tech-forward aesthetic.

| Font Family | Variable | Usage |
| :--- | :--- | :--- |
| **Geist Sans** | `--font-geist-sans` | UI text, headings, buttons, and general content. |
| **Geist Mono** | `--font-geist-mono` | Code snippets, nutritional data numbers, and technical details. |

---

## Installation & Setup

We recommend using Docker for the easiest setup experience.

### Quick Start (Docker)

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/mariiammaysara/Veonix.git
    cd Veonix
    ```

2.  **Environment Configuration**
    Create a `.env` file in the `backend/` directory and add your Hugging Face Token:
    ```bash
    # backend/.env
    HF_TOKEN=your_token_here
    DATABASE_URL=sqlite:///./veonix.db
    ```

3.  **Run with Docker Compose**
    ```bash
    docker-compose up --build
    ```

    The application will be available at:
    - **Frontend:** http://localhost:3000
    - **Backend API:** http://localhost:8000/docs

---

### Manual Installation (Development)

If you prefer to run the services locally without Docker:

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Activate: venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt

# Configure Environment
# Create backend/.env with HF_TOKEN=your_token_here

uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install

# Configure Environment
# Create frontend/.env.local with NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

---

## Deployment

Veonix is optimized for deployment on **Render**.

### Backend Deployment (Render)
1.  Create a new **Web Service** on Render.
2.  Connect your repository and select the `backend` directory as the Root Directory.
3.  **Runtime**: Python 3
4.  **Build Command**: `pip install -r requirements.txt`
5.  **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
6.  **Environment Variables**:
    - `HF_TOKEN`: Your Hugging Face Token.
    - `PYTHON_VERSION`: `3.10.0` (or your preferred version).

### Frontend Deployment (Render)
1.  Create a new **Web Service** on Render.
2.  Connect your repository and select the `frontend` directory as the Root Directory.
3.  **Runtime**: Node
4.  **Build Command**: `npm install && npm run build`
5.  **Start Command**: `npm start`
6.  **Environment Variables**:
    - `NEXT_PUBLIC_API_URL`: The URL of your deployed Backend Web Service (e.g., `https://veonix-backend.onrender.com`).

---

## API Documentation

Veonix provides a self-documenting REST API. Once the backend is running, you can access the interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

| Category | Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- | :--- |
| **Analysis** | `POST` | `/analyze/image` | Uploads an image for AI nutritional analysis. Returns simplified JSON data. | `multipart/form-data` (file) |
| **History** | `GET` | `/analyze/history` | Retrieves past analysis records (Note: Frontend uses local storage). | N/A |
| | `DELETE` | `/analyze/{id}` | Permanently deletes a specific meal entry by ID. | N/A |
| **System** | `GET` | `/health` | Returns `{ status: "ok" }` to verify backend availability. | N/A |

---

## Future Roadmap

We are committed to continuously enhancing Veonix. Planned features include:

- [ ] **Mobile Application**: Developing native iOS and Android apps using React Native.
- [ ] **Personalized Nutrition Plans**: Implementing AI algorithms to suggest meal plans based on user history and goals.
- [ ] **Barcode Scanning**: Adding barcode recognition for packaged foods to complement visual analysis.
- [ ] **Voice Logging**: Enabling voice commands (e.g., "Hey Veonix, I logged a banana").
- [ ] **Social Sharing**: Features to share meals and nutritional achievements with friends.
- [ ] **Cloud Sync**: Optional account creation to sync history across devices securely.

---

## Contributing

We welcome contributions from the community! To contribute:

1.  **Fork** the repository.
2.  Create a **Feature Branch** (`git checkout -b feature/NewFeature`).
3.  **Commit** your changes (`git commit -m 'Add NewFeature'`).
4.  **Push** to your branch (`git push origin feature/NewFeature`).
5.  Open a **Pull Request**.

---

## License

This project is open source and available under the terms of the **MIT License**. See the `LICENSE` file for more details.

---
<p align="center">
  <strong>Developed by Mariam Maysara</strong>
</p>

