from fastapi import HTTPException, UploadFile
from app.utils.image_processing import (
    load_image_bytes,
    pil_from_bytes,
    reencode_to_jpeg,
)
from app.services.gemini_client import GeminiClient
from app.services.nutrition import NUTRITION_PROMPT


class ImageAnalysisService:
    def __init__(self):
        self.client = GeminiClient()

    def analyze(self, file: UploadFile):
        image_bytes = self._load_bytes(file)
        pil_image = self._decode_pil(image_bytes)
        jpeg_bytes = self._encode_jpeg(pil_image)

        model_output = self._send_to_gemini(jpeg_bytes)
        return model_output

    def _load_bytes(self, file: UploadFile):
        try:
            return load_image_bytes(file)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file.")

    def _decode_pil(self, image_bytes: bytes):
        try:
            return pil_from_bytes(image_bytes)
        except Exception:
            raise HTTPException(status_code=400, detail="Failed to decode image.")

    def _encode_jpeg(self, image):
        try:
            return reencode_to_jpeg(image)
        except Exception:
            raise HTTPException(status_code=500, detail="JPEG encoding failed.")

    def _send_to_gemini(self, jpeg_bytes: bytes):
        try:
            return self.client.analyze_image_with_prompt(
                image_bytes=jpeg_bytes,
                prompt=NUTRITION_PROMPT
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")
