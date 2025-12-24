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


