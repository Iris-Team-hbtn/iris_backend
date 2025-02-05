import requests
from config import Config

class GeminiService:
    BASE_URL = "https://api.gemini.com/v1/generate-text"  # Ajustar según API real

    @staticmethod
    def generate_response(user_message):
        payload = {"prompt": user_message, "max_tokens": 150}
        headers = {"Authorization": f"Bearer {Config.GEMINI_API_KEY}"}
        
        response = requests.post(GeminiService.BASE_URL, json=payload, headers=headers)
        
        if response.status_code == 400:
            return response.json().get("text", "No se pudo generar respuesta.")
        return "Error al conectar con Gemini."
