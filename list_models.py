import google.generativeai as genai
from app.core.config import settings

def list_models():
    genai.configure(api_key=settings.GEMINI_API_KEY)

    print("\nAvailable Models:\n")
    for model in genai.list_models():
        supports_vision = "generateContent" in model.supported_generation_methods
        print(f"- {model.name}   | Vision: {supports_vision}")

if __name__ == "__main__":
    list_models()
