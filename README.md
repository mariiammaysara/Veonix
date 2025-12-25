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

## Usage

Once the application is running, follow these steps to analyze your meals and track your nutrition:

### 1. Analyze a Meal
1. Open the **Veonix** dashboard in your browser (`http://localhost:3000`).
2. Navigate to the **Upload** page.
3. Drag and drop an image of your food or click the upload area to select a file from your device.
4. Click the **Analyze** button.
5. Wait for the **Gemini 2.0 Flash** model to identify the food and calculate the nutritional breakdown.

### 2. View Results
* **Nutritional Summary:** View total calories and a detailed breakdown of macronutrients (Protein, Carbs, and Fats).
* **AI Insights:** The system identifies the specific name of the food items detected in the image.



### 3. Track History
1. Navigate to the **History** tab in the sidebar.
2. Browse through your previous meal analyses stored in the local database.
3. Use the history to monitor your eating habits over time.
4. (Optional) Use the delete function to remove entries you no longer wish to track.

### 4. Developer Tools (API Docs)
If you are a developer looking to integrate with the backend:
* Visit `http://localhost:8000/docs` to access the interactive **Swagger UI**.
* You can test the endpoints manually by uploading images via the `/analyze/image` route.

## Configuration

To run **Veonix** properly, you must configure the environment variables for both the backend and frontend.

### Backend Configuration
The backend requires a `.env` file located in the `/backend` directory. This file handles sensitive API keys and database connections.

| Variable | Description | Default/Example |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Your Google AI Studio API Key | `AIzaSy...` |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./food_app.db` |
| `LOG_LEVEL` | Level of logging detail | `INFO` |

### Frontend Configuration
The frontend uses an `.env.local` file located in the `/frontend` directory to communicate with the backend API.

| Variable | Description | Default/Example |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | The URL of your FastAPI backend | `http://localhost:8000` |

---

### Google Gemini API Setup
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Create a new API Key.
3. Ensure the key has permissions for the **gemini-3-flash-preview** model.
4. Paste the key into your backend `.env` file.

---

### Docker Configuration
If you are modifying the deployment, the `docker-compose.yml` file at the root handles the networking between services.
* **Backend Port:** Internal `8000` mapped to External `8000`.
* **Frontend Port:** Internal `3000` mapped to External `3000`.
* **Network:** Both services share a custom bridge network to allow the frontend to resolve the backend container by its service name.

## UI Features

Veonix features a clean, high-performance user interface designed for a seamless user experience across all devices.

###  Design & Layout
* **Modern Dashboard:** A sleek, minimal dashboard layout for easy navigation.
* **Responsive Design:** Fully optimized for Mobile, Tablet, and Desktop views using Tailwind CSS.
* **Sidebar Navigation:** Organized sidebar for quick access to Upload, History, and Settings.
* **Dynamic Logo:** Custom-branded Veonix logo integrated into the header.

###  Interaction Features
* **Smart Upload Box:** Supports drag-and-drop functionality with real-time file type validation.
* **Live Image Preview:** Displays the selected image instantly before processing to ensure accuracy.
* **Loading States:** Interactive progress indicators while the Gemini AI analyzes the meal.
* **Actionable Sidebar:** Collapsible navigation to maximize workspace during analysis.

###  Data Visualization
* **Nutritional Cards:** Clean cards displaying Calories, Protein, Carbs, and Fats.
* **History Table:** A structured data table to review past meals with delete and view capabilities.
* **Interactive Charts:** Visual representation of macronutrient ratios for better insight.
* **Error Handling:** Friendly UI notifications for invalid uploads or API timeouts.

---

### UI Components Gallery
| Component | Description |
| :--- | :--- |
| **`upload-box.tsx`** | Handles file selection and drag-drop events. |
| **`results-display.tsx`** | Renders the AI's nutritional breakdown. |
| **`data-table.tsx`** | Manages the display and filtering of meal history. |
| **`app-sidebar.tsx`** | The main navigation hub for the application. |
## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### How to Contribute

1. **Fork the Project**
   Click the 'Fork' button at the top of this repository to create your own copy.

2. **Create your Feature Branch**
   ```powershell
   git checkout -b feature/AmazingFeature
      ```
3. **Commit your Changes**
   ```powershell
   git commit -m 'Add some AmazingFeature'
      ```
4. **Push to the Branch**
```powershell
git push origin feature/AmazingFeature
 ```
5. Open a Pull Request Open a PR from your fork's branch to the original repository's main branch

## Core Technologies

Veonix is built using a modern, scalable stack designed for high performance and seamless AI integration.

### Frontend (User Interface)
* **Framework:** **Next.js 15** (App Router) for server-side rendering and optimized performance.
* **Styling:** **Tailwind CSS** for a responsive, utility-first design system.
* **Components:** **Shadcn/UI** & **Lucide React** for high-quality, accessible UI elements.
* **Language:** **TypeScript** for robust, type-safe development.

### Backend (API & Logic)
* **Framework:** **FastAPI** (Python) for building high-performance, asynchronous APIs.
* **AI Engine:** **Google gemini-3-flash-preview** for advanced image recognition and nutritional analysis.
* **Database:** **SQLite** with **SQLAlchemy ORM** for efficient data persistence and history tracking.
* **Validation:** **Pydantic** for rigorous data validation and settings management.

### Infrastructure & DevOps
* **Containerization:** **Docker & Docker Compose** for consistent environment orchestration.
* **Deployment:** **Render** for reliable cloud hosting of both frontend and backend services.
* **API Documentation:** **Swagger UI** for interactive API testing and documentation.
* **Code Quality:** **Ruff** for ultra-fast Python linting and formatting.

---

### Why this stack?
- **FastAPI + Gemini:** Provides near-instant AI responses using asynchronous processing.
- **Next.js 15:** Ensures the dashboard is fast, SEO-friendly, and provides a smooth SPA-like experience.
- **Docker:** Guarantees that the app runs exactly the same way on your local machine as it does on the Render production server.

##  License

Distributed under the MIT License. See `LICENSE` for more information.

---
<div align="center">

**Developed with by [Mariam Maysara](https://github.com/mariiammaysara)**

</div>








