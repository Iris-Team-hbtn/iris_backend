from services.gemini_service import GeminiService

class Chatbot:
    def process_message(self, message):
        return GeminiService.generate_response(message)
