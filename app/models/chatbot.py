from app.services.gemini_service import GeminiService

class Chatbot:
    def process_message(self, user_message):
        gemini = GeminiService()
        return gemini.generate_response(user_message)

