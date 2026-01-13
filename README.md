# ✦ V E O N I X

<div align="center">
  <img src="https://github.com/user-attachments/assets/95c08bcd-c765-4d1e-9cbf-950f3d06a3a6" alt="Veonix Header" width="100%" />
</div>

> **Unlock the data in your diet.** Veonix combines advanced computer vision with nutritional science to provide instant, detailed breakdowns of your meals.

## Introduction

**Veonix** is not just a calorie tracker; it is an intelligent dietary companion. By leveraging **Google Gemini 1.5**, Veonix "sees" your food, identifying complex dishes, estimating portion sizes, and calculating macronutrients with remarkable accuracy. 

Designed for bio-hackers, fitness enthusiasts, and anyone who wants frictionless health tracking, Veonix replaces tedious manual logging with a single photo.

## Key Features

### Visual Analysis Engine
- **Instant Recognition**: Identify thousands of worldwide dishes in milliseconds.
- **Ingredient Deconstruction**: Breaks down complex meals into their core components.
- **Portion Estimation**: AI-driven analysis of quantity and volume.

### Data-Driven Insights
- **Macro Breakdown**: Real-time calculation of Protein, Carbs, Fats, and Calories.
- **Historical Trends**: Visual graphs of your nutritional intake over time.
- **Health Scoring**: Auto-generated health scores for every meal.

### Modern User Experience
- **Responsive Design**: Built with a "mobile-first" approach using Tailwind CSS v4.
- **Interactive UI**: Fluid animations and real-time feedback with Radix UI.
- **Dark Mode Native**: Optimized for visual comfort in all lighting conditions.

### Design System

A carefully curated palette designed to evoke precision and health.

| Color | Hex | Usage |
| :--- | :--- | :--- |
| ![#0f172a](https://placehold.co/15x15/0f172a/0f172a.png) **Deep Slate** | `#0f172a` | Primary Background / Canvas |
| ![#10b981](https://placehold.co/15x15/10b981/10b981.png) **Emerald** | `#10b981` | Brand Identity / Success States |
| ![#e2e8f0](https://placehold.co/15x15/e2e8f0/e2e8f0.png) **Slate Mist** | `#e2e8f0` | Typography / Primary Text |
| ![#1e293b](https://placehold.co/15x15/1e293b/1e293b.png) **Dark Lvl 2** | `#1e293b` | Cards / Elevated Surfaces |

## System Architecture

Veonix utilizes a modern, decoupled architecture designed for speed and scalability. The workflow begins when a user uploads an image through the Next.js Client. This request is handled by the FastAPI Backend, which acts as the secure orchestrator. The backend pre-processes the image and sends it to the Google Gemini Vision API for high-level nutritional analysis. The raw AI response is then normalized into structured JSON data and stored in the SQLite database before being returned to the frontend for visualization.

### Project Structure

```graphql
veonix/
├── backend/
│   ├── app/
│   │   ├── core/                 # Core Business Logic
│   │   │   ├── middleware/
│   │   │   │   ├── request_id.py
│   │   │   │   ├── request_logger.py
│   │   │   │   └── timing.py
│   │   │   ├── routers/          # API Endpoints
│   │   │   │   ├── analyze.py
│   │   │   │   └── health.py
│   │   │   ├── schemas/          # Data Models
│   │   │   │   └── analyze.py
│   │   │   ├── services/         # Integrations (Gemini, Nutrition)
│   │   │   │   ├── food_classifier.py
│   │   │   │   ├── gemini_client.py
│   │   │   │   ├── nutrition.py
│   │   │   │   ├── nutrition_normalizer.py
│   │   │   │   └── prompts.py
│   │   │   ├── utils/
│   │   │   │   └── image_processing.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── error_handler.py
│   │   │   └── logging_config.py
│   │   ├── models/               # DB Models
│   │   │   └── meal.py
│   │   └── main.py               # Entry Point
│   ├── Dockerfile
│   ├── food_app.db
│   ├── list_gemini_models.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/                      # Next.js App Router
│   │   ├── dashboard/
│   │   │   ├── history/
│   │   │   │   └── page.tsx
│   │   │   ├── upload/
│   │   │   │   └── page.tsx
│   │   │   └── page.tsx
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/               # UI Components
│   │   ├── ui/                   # Shadcn UI
│   │   │   └── ...
│   │   ├── charts/               # Recharts
│   │   │   └── ...
│   │   ├── app-sidebar.tsx
│   │   ├── chart-area-interactive.tsx
│   │   ├── data-table.tsx
│   │   ├── image-preview.tsx
│   │   ├── nav-documents.tsx
│   │   ├── nav-main.tsx
│   │   ├── nav-secondary.tsx
│   │   ├── nav-user.tsx
│   │   ├── navbar.tsx
│   │   ├── results-card.tsx
│   │   ├── upload-box.tsx
│   │   └── veonix-logo.tsx
│   ├── hooks/
│   │   └── use-mobile.ts
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── public/
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   └── vercel.svg
│   ├── Dockerfile
│   ├── components.json
│   ├── next.config.ts
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── docker-compose.yml
├── LICENSE
└── README.md
```

## Technology Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | [Next.js 16](https://nextjs.org/) | React 19, App Router, Server Actions |
| **Styling** | [Tailwind CSS v4](https://tailwindcss.com/) | Utility-first CSS, Animations |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance Python API |
| **AI Model** | [Google Gemini 1.5](https://deepmind.google/technologies/gemini/) | Multimodal Vision Model |
| **Database** | SQLite | Lightweight, serverless storage |
| **Infrastructure** | Docker | Containerization & Orchestration |

## Quick Start

### 1. Installation

Clone the repository and enter the directory:

```bash
git clone https://github.com/mariiammaysara/Veonix.git
cd Veonix
```

### 2. Configuration

Set up your environment variables. You will need a standard Google Gemini API key.

```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
```

### 3. Run Application

We recommend using Docker Compose for a seamless start:

```bash
docker-compose up --build
```

Access the application:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## Contribution

We welcome contributions to Veonix! The open-source community is a fantastic place to learn, inspire, and create, and your contributions are greatly appreciated.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

This project is open source and available under the terms of the **MIT License**. See the `LICENSE` file for more details.

---

<p align="center">
  <strong>Developed by Mariam Maysara.</strong>
</p>
