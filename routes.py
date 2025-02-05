from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource
from models.chatbot import Chatbot

# Crear un Blueprint para la API
api_bp = Blueprint("api", __name__)
api = Api(api_bp, title="Chatbot API", description="Endpoints para el chatbot de salud estética")

# Instancia del chatbot
chatbot = Chatbot()

# Namespaces
ns_chatbot = api.namespace("chatbot", description="Operaciones del chatbot")

# ---- ENDPOINT: Procesar mensaje del chatbot ----
@ns_chatbot.route("/message")
class ChatbotMessage(Resource):
    def post(self):
        """Recibe un mensaje del usuario y devuelve la respuesta del chatbot"""
        data = request.get_json()
        if not data or "message" not in data:
            return {"error": "Mensaje no proporcionado"}, 400

        response = chatbot.process_message(data["message"])
        return {"response": response}, 200

# Registrar los namespaces en la API
api.add_namespace(ns_chatbot)
