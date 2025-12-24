import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

print("Available models that support generateContent:\n")

for model in genai.list_models():
    methods = model.supported_generation_methods or []
    if "generateContent" in methods:
        print(model.name, methods)
