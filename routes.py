from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource
from googleapiclient.discovery import build
from google.oauth2 import service_account
from models.chatbot import Chatbot
import datetime
import uuid

# Configuración de Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'path/to/your/service-account.json'  
CALENDAR_ID = 'alexisoblivion@gmail.com'  

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

# Crear un Blueprint para la API
api_bp = Blueprint("api", __name__)
api = Api(api_bp, title="Chatbot API", description="Endpoints para el chatbot de salud estética")

# Instancia del chatbot
chatbot = Chatbot()

# Namespaces
ns_chatbot = api.namespace("chatbot", description="Operaciones del chatbot")
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

# ---- ENDPOINT: Agendar consulta ----
@ns_appointment.route("/")
class AppointmentResource(Resource):
    def post(self):
        """Crea una cita para un cliente"""
        data = request.get_json()
        if not data or "client_name" not in data or "date" not in data or "time" not in data:
            return {"error": "Faltan datos requeridos"}, 400

        # Convertir fecha y hora a formato ISO
        date_time_str = f"{data['date']}T{data['time']}:00"
        start_time = datetime.datetime.fromisoformat(date_time_str)
        end_time = start_time + datetime.timedelta(minutes=30)

        # Verificar si el turno tiene menos de dos pacientes
        events = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True
        ).execute()

        if len(events.get('items', [])) >= 2:
            return {"error": "El turno ya está lleno"}, 400

        # Crear evento en Google Calendar
        event = {
            'summary': f"Consulta con {data['client_name']}",
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/New_York'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/New_York'}
        }
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        return {"status": "Confirmed", "appointment_id": created_event["id"]}, 201

# Registrar los namespaces en la API
api.add_namespace(ns_chatbot)
api.add_namespace(ns_appointment)
