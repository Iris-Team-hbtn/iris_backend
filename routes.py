from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource
from chatbot import Chatbot
from consultation_scheduler import ConsultationScheduler
import uuid

# Crear un Blueprint para la API
api_bp = Blueprint("api", __name__)
api = Api(api_bp, title="Chatbot API", description="Endpoints para el chatbot de salud estética")

# Instancias de las clases de negocio
chatbot = Chatbot()
scheduler = ConsultationScheduler()

# Base de datos temporal para almacenar clientes (puede ser reemplazada por Faiss u otra BD)
clients_db = {}

# Namespaces para organizar los endpoints
ns_chatbot = api.namespace("chatbot", description="Operaciones del chatbot")
# ns_client = api.namespace("client", description="Gestión de clientes")
ns_appointment = api.namespace("appointment", description="Manejo de consultas")

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

# ---- ENDPOINT: Registrar cliente ----
# @ns_client.route("/")
# class ClientResource(Resource):
#     def post(self):
#         """Registra un cliente potencial en el sistema"""
#         data = request.get_json()
#         if not data or "name" not in data or "email" not in data:
#             return {"error": "Faltan datos requeridos"}, 400

#         client_id = str(uuid.uuid4())  # Genera un ID único para el cliente
#         clients_db[client_id] = {
#             "id": client_id,
#             "name": data["name"],
#             "email": data["email"],
#             "phone": data.get("phone", ""),
#             "interested_in": data.get("interested_in", ""),
#             "status": "Pending"
#         }

#         return {"status": "Client stored", "client_id": client_id}, 201

# ---- ENDPOINT: Agendar consulta ----
@ns_appointment.route("/")
class AppointmentResource(Resource):
    def post(self):
        """Crea una cita para un cliente"""
        data = request.get_json()
        if not data or "client_id" not in data or "date" not in data:
            return {"error": "Faltan datos requeridos"}, 400

        appointment_id = scheduler.schedule_appointment(data)
        return {"status": "Confirmed", "appointment_id": appointment_id}, 201

# Registrar los namespaces en la API
api.add_namespace(ns_chatbot)
api.add_namespace(ns_client)
api.add_namespace(ns_appointment)
