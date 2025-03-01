from flask_restx import Namespace, Resource, fields
from flask import make_response, jsonify, request
import json
from app.services.calendar_service import CalendarService
from app.services.toolkits import get_or_create_user_id
from app.services.mail_service import MailService
from app.services.main_service import MainCaller

api = Namespace('iris', description='Iris endpoints')

model = api.model('Iris', {
    'query': fields.String(required=True, description='Pregunta para Iris'),
})

calendar_model = api.model('Calendar', {
    'fullname': fields.String(required=True, description='Fullname of client'),
    'month': fields.Integer(required=True, description='Month of the appointment'),
    'day': fields.Integer(required=True, description='Day of the appointment'),
    'starttime': fields.Integer(required=True, description='Start Time of the appointment'),
    'email': fields.String(required=True, description='Email to invite to Google Calendar event'),
    'year': fields.Integer(required=False, description='Year of the appointment')
})

calendar = CalendarService()
main_caller = MainCaller()

@api.route("/chat")
class Query(Resource):
    @api.expect(model)
    @api.response(200, "Respuesta obtenida correctamente")
    @api.response(400, "Datos de entrada inválidos")
    @api.response(404, "No hay información disponible")
    def post(self):
        """Procesa una pregunta y devuelve la respuesta de Iris en Markdown"""
        data = api.payload
        if not data or "query" not in data:
            return {"error": "Datos de entrada inválidos."}, 400

        # Obtener user_id y respuesta con cookie si es un nuevo usuario
        user_id, user_response = get_or_create_user_id()
        user_question = data["query"]

        # Llamar a Iris para procesar la consulta
        response = main_caller.call(user_question, user_id=user_id)
        if not response:
            return {"error": "No hay información disponible."}, 404

#<------------Descomentar aqui si queremos devolver este formato-------------->
        # # Configurar la respuesta en formato Markdown
        # resp = {
        #     "iris": [
        #         {
        #             "content": response["text"],  # Aquí la respuesta ya está formateada en Markdown
        #             "role": "model"
        #         }
        #     ]
        # }

        resp = {"response": response["text"]}

        # Si se creó un nuevo user_id, devolvemos la respuesta con la cookie ya establecida
        if user_response:
            user_response.set_data(json.dumps(resp))  # Adjuntar los datos a la respuesta
            user_response.status_code = 200
            return user_response

        # Si ya existía el user_id, devolvemos solo la respuesta JSON
        return make_response(jsonify(resp), 200)

@api.route('/appointments')
class Calendar(Resource):
    @api.response(200, 'Citas obtenidas correctamente')
    @api.response(400, 'Datos de entrada inválidos')
    @api.response(404, 'No hay citas agendadas')
    def get(self):
        """Obtiene todas las citas de las próximas dos semanas"""
        event_list = calendar.listEvents()

        if not event_list:
            return {"message": 'No hay citas agendadas'}, 404
        return {"events": event_list}, 200

    @api.expect(calendar_model)
    @api.response(200, 'Cita creada correctamente')
    @api.response(400, 'Hubo un problema con Google Calendar')
    def post(self):
        """Agenda una cita en la clínica"""
        data = api.payload

        if not data:
            return {"error": "Datos de entrada inválidos"}, 400
        
        fullname = data.get('fullname')
        month = data.get('month')
        day = data.get('day')
        email = data.get('email')
        starttime = data.get('starttime')
        year = data.get('year')

        event_create = calendar.createEvent(month=month, day=day, email=email, startTime=starttime, year=year)

        if event_create:
            # Enviar email al usuario
            mail_service = MailService()

            user_mail_body = mail_service.build_body('user_appointment', {"fullname": fullname, "date": f"{day}/{month}/{year} - {starttime}hs"})
            mail_service.send_email('user_appointment', user_mail_body, email)

            # Enviar email a la clínica
            clinic_mail_body = mail_service.build_body('clinic_appointment', {"fullname": fullname, "user_email": email, "date": f"{day}/{month}/{year} - {starttime}hs"})
            mail_service.send_email('clinic_appointment', clinic_mail_body, "yuntxwillover@gmail.com")

            return {"message": "Evento creado con éxito"}, 200
        
        return {"error": "Hubo un problema con Google Calendar"}, 400
