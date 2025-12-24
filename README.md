<h1 align="center">Veonix - AI Nutrition Analyzer</h1>
<img width="1213" height="320" alt="veonix-header png" src="https://github.com/user-attachments/assets/95c08bcd-c765-4d1e-9cbf-950f3d06a3a6" />

<p align="center">
    Experience Veonix in action —  
  <a href="https://veonix-u8yw.onrender.com" target="_blank">
    View Live Demo
  </a>
</p>

## Features


### Backend

- **Asynchronous API Architecture**  
  Built with FastAPI to efficiently handle multiple concurrent requests using Python `async/await`.

- **Advanced AI Vision Integration**  
  Utilizes the `gemini-3-flash-preview` multimodal model for fast and accurate food image analysis.

- **Structured Data Extraction**  
  Enforces strict JSON-based prompting to guarantee validated and consistent nutritional outputs.

- **Optimized Image Processing**  
  Leverages the Pillow library to resize, optimize, and convert images to JPEG, reducing latency and bandwidth usage.

- **Automated History Management**  
  Uses SQLAlchemy with SQLite to persist analyzed meals for future retrieval.

- **Environment-Based Configuration**  
  Secures sensitive configuration (e.g. `GEMINI_API_KEY`) via Pydantic Settings and `.env` files.

- **RESTful API Endpoints**
  - `POST /analyze/image` — Analyze uploaded food images (multipart/form-data)
  - `GET /analyze/history` — Retrieve paginated meal analysis history
  - `DELETE /analyze/{id}` — Delete specific analysis records

- **CORS Security Configuration**  
  Restricts cross-origin requests to the production frontend domain only.

- **Containerized Deployment**  
  Fully containerized with Docker to ensure consistency across local development and production on Render.


### Frontend

- **Modern Architecture**  
  Built with Next.js 15 using the App Router for efficient client-side navigation and high performance.

- **Responsive UI Design**  
  Fully adaptive interface designed with Tailwind CSS to deliver a seamless experience across mobile, tablet, and desktop.

- **Real-Time Analysis Interface**  
  Interactive dashboard enabling users to upload, preview, and analyze meals instantly without page reloads.

- **Dynamic Data Visualization**  
  Clean and modern results display highlighting calories and macronutrients (Protein, Carbs, Fats) with high visual clarity.

- **Meal History Dashboard**  
  Dedicated interface for browsing and managing past analyses, powered by direct integration with the backend API.

- **Client-Side Image Handling**  
  Implements local image previews using `URL.createObjectURL` to provide immediate visual feedback before upload.

- **Robust Error Handling**  
  Comprehensive UI feedback for network issues, file validation errors, and analysis failures to ensure a smooth user experience.

- **Optimized Assets & Performance**  
  Uses Lucide React for lightweight, scalable icons and optimized font loading to improve initial render times.

- **Environment-Based Integration**  
  Securely communicates with the FastAPI backend via environment variables configured for both local and production environments.

##  Project Structure
```text
Veonix/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── middleware/        # Performance and logging handlers
│   │   │   │   ├── request_id.py
│   │   │   │   ├── request_logger.py
│   │   │   │   └── timing.py
│   │   │   ├── routers/           # API Endpoints
│   │   │   │   ├── analyze.py
│   │   │   │   └── health.py
│   │   │   └── schemas/           # Pydantic data validation
│   │   │       └── analyze.py
│   │   ├── models/                # Database models
│   │   │   └── meal.py
│   │   ├── services/              # Logic and AI integrations
│   │   │   ├── food_classifier.py
│   │   │   ├── gemini_client.py
│   │   │   ├── nutrition_normalizer.py
│   │   │   ├── nutrition.py
│   │   │   └── prompts.py
│   │   ├── utils/                 # Helpers and Configurations
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── error_handler.py
│   │   │   └── logging_config.py
│   │   └── main.py                # FastAPI entry point
│   ├── Dockerfile                 # Backend container config
│   ├── requirements.txt           # Python dependencies
│   ├── food_app.db                # SQLite Database
│   └── list_gemini_models.py      # Utility script
│
├── frontend/
│   ├── app/                       # Next.js App Router
│   │   ├── dashboard/
│   │   │   ├── history/
│   │   │   │   └── page.tsx       # Past meals view
│   │   │   └── upload/
│   │   │       └── page.tsx       # Analysis & upload view
│   │   ├── globals.css            # Global styling
│   │   ├── layout.tsx             # Root layout
│   │   └── page.tsx               # Landing page
│   ├── components/                # UI Components
│   │   ├── ui/                    # Base UI elements (Shadcn/Custom)
│   │   ├── app-sidebar.tsx
│   │   ├── data-table.tsx
│   │   ├── image-preview.tsx
│   │   ├── navbar.tsx
│   │   ├── results-display.tsx
│   │   ├── upload-box.tsx
│   │   └── veonix-logo.tsx
│   ├── lib/                       # API client and utilities
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── public/                    # Static assets
│   ├── Dockerfile                 # Frontend container config
│   ├── next.config.ts             # Next.js configuration
│   ├── tailwind.config.js         # Styling configuration
│   └── package.json               # Node.js dependencies
│
├── docker-compose.yml             # Full-stack orchestration
├── LICENSE                        # Project license
└── README.md                      # Project documentation
```
### Prerequisites

Before you begin, ensure you have the following installed on your local machine:

- **Docker & Docker Compose**  
  Required to run the containerized services (frontend, backend, and database).

- **Git**  
  Used to clone the repository.

- **Google Gemini API Key**  
  Obtain your API key from  
    **[Google AI Studio – API Keys](https://aistudio.google.com/api-keys)**  
  then click **“Create API Key”** to generate one.

## Installation & Setup 

## Backend Setup 

If you prefer to run the backend service without Docker for debugging or development purposes, follow these steps:

### 1. Create a Virtual Environment
Navigate to the backend directory and create a clean environment to isolate dependencies:
```bash
cd backend
python -m venv venv
```
### 2. Activate the Environment
Windows:
```bash
venv\Scripts\activate
```
Mac/Linux:
```bash
source venv/bin/activate
```
### 3. Install Dependencies
Install the required Python packages listed in requirements.txt:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Environment Variables
Ensure your .env file is present in the backend/ root folder with the following content:
```bash
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./food_app.db
```
### 5. Launch the Server
Run the FastAPI application using Uvicorn with hot-reload enabled:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
## Frontend Setup 
If you wish to run the frontend application independently without Docker (e.g., for UI development), follow these steps:

### 1. Prerequisites
Ensure you have **Node.js** (v18 or higher) and **npm** installed on your system.

### 2. Navigate and Install
Go to the frontend directory and install the required dependencies:
```bash
cd frontend
npm install
```
### 3. Environment Variables
Create a file named .env.local in the frontend/ directory to point to your backend API:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
### 4. Development Server
Start the Next.js development server:
```bash
npm run dev
```
The application will be accessible at http://localhost:3000.
### 5. Production Build
To test the production-optimized version of the site:
```bash
npm run build
npm run start
```
## Running the Application

The easiest way to run the entire **Veonix** stack (Frontend, Backend, and Database) is using **Docker Compose**. This ensures that all services are configured correctly and can communicate with each other.

### 1. Fast Track (Docker Compose)
From the root directory of the project, run:

```bash
docker-compose up --build
```
This command will:

- Build the FastAPI backend image.

- Build the Next.js frontend image.

- Initialize the SQLite database.

- Start both services and link them via a shared network
  
### 2. Service Endpoints
Once the containers are healthy, you can access the application at:

| Service            | URL                           | Description               |
|--------------------|-------------------------------|---------------------------|
| Frontend           | http://localhost:3000         | Main user interface       |
| Backend API        | http://localhost:8000         | API base URL              |
| API Documentation  | http://localhost:8000/docs    | Interactive Swagger UI    |

## Data Flow Overview

1. **Upload**  
   The user selects a meal image from the Next.js frontend.

2. **Request Processing**  
   The frontend sends a `POST` request to the FastAPI backend.

3. **AI Analysis**  
   The backend processes the image and forwards it to the Gemini Vision model for analysis.

4. **Data Storage**  
   The analysis results (calories and macronutrients) are persisted in the SQLite database.

5. **Results Display**  
   The frontend renders the nutritional breakdown and updates the meal history in real time.










