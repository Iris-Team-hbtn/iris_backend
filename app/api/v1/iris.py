# Import necessary modules and packages
from flask_restx import Namespace, Resource, fields
from flask import make_response, jsonify, request
import json
from app.services.calendar_service import CalendarService
from app.services.toolkits import get_or_create_user_id
from app.services.mail_service import MailService
from app.services.main_service import MainCaller

# Create a namespace for Iris API endpoints
api = Namespace('iris', description='Iris endpoints')

# Define the model for chat queries
model = api.model('Iris', {
    'query': fields.String(required=True, description='Pregunta para Iris'),
})

# Define the model for calendar appointments
calendar_model = api.model('Calendar', {
    'fullname': fields.String(required=True, description='Fullname of client'),
    'month': fields.Integer(required=True, description='Month of the appointment'),
    'day': fields.Integer(required=True, description='Day of the appointment'),
    'starttime': fields.Integer(required=True, description='Start Time of the appointment'),
    'email': fields.String(required=True, description='Email to invite to Google Calendar event'),
    'year': fields.Integer(required=False, description='Year of the appointment')
})

# Initialize services
calendar = CalendarService()
main_caller = MainCaller()

# Chat endpoint for handling queries to Iris
@api.route("/chat")
class Query(Resource):
    @api.expect(model)
    @api.response(200, "Respuesta obtenida correctamente")
    @api.response(400, "Datos de entrada inválidos")
    @api.response(404, "No hay información disponible")
    def post(self):
        # Get payload data and validate
        data = api.payload
        if not data or "query" not in data or not data["query"].strip():
            return {"error": "Datos de entrada inválidos."}, 400

        # Get or create user ID and process the question
        user_id, user_response = get_or_create_user_id()
        user_question = data["query"]

        # Get response from main service
        response = main_caller.call(user_question, user_id=user_id)
        if not response:
            return {"error": "No hay información disponible."}, 404

        # Format response based on type (dict or string)
        if isinstance(response, dict):
            resp = {"response": response.get("text")}
        else:
            resp = {"response": response}

        # Return response with user session if available
        if user_response:
            user_response.set_data(json.dumps(resp))
            user_response.status_code = 200
            return user_response

        return make_response(jsonify(resp), 200)

# Calendar endpoints for handling appointments
@api.route('/appointments')
class Calendar(Resource):
    @api.response(200, 'Citas obtenidas correctamente')
    @api.response(400, 'Datos de entrada inválidos')
    @api.response(404, 'No hay citas agendadas')
    def get(self):
        # Get list of calendar events
        event_list = calendar.listEvents()
        if not event_list:
            return {"message": 'No hay citas agendadas'}, 404
        return {"events": event_list}, 200

    @api.expect(calendar_model)
    @api.response(200, 'Cita creada correctamente')
    @api.response(400, 'Hubo un problema con Google Calendar')
    def post(self):
        # Get and validate appointment data
        data = api.payload
        if not data:
            return {"error": "Datos de entrada inválidos"}, 400
        
        # Extract appointment details
        fullname = data.get('fullname')
        month = data.get('month')
        day = data.get('day')
        email = data.get('email')
        starttime = data.get('starttime')
        year = data.get('year', 2025)

        # Validate email
        mail_service = MailService()
        if not mail_service.validate_email(email):
            return {"error": "El correo electrónico proporcionado no es válido."}, 400

        # Create calendar event
        event_create = calendar.createEvent(month=month, day=day, email=email, startTime=starttime, year=year)
        if event_create:
            try:
                # Send confirmation email to user
                user_mail_body = mail_service.build_body('user_appointment', {
                    "fullname": fullname, 
                    "date": f"{day}/{month}/{year} - {starttime}hs"
                })
                mail_service.send_email('user_appointment', user_mail_body, email)

                # Send notification email to clinic
                clinic_mail_body = mail_service.build_body('clinic_appointment', {
                    "fullname": fullname, 
                    "user_email": email, 
                    "date": f"{day}/{month}/{year} - {starttime}hs"
                })
                mail_service.send_email('clinic_appointment', clinic_mail_body, "yuntxwillover@gmail.com")
            except Exception as e:
                return {"error": f"Error al enviar el correo: {str(e)}"}, 500
            return {"message": "Evento creado con éxito"}, 200
        
        return {"error": "Hubo un problema con Google Calendar"}, 400
