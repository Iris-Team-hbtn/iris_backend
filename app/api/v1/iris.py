from flask_restx import Namespace, Resource, fields
from flask import make_response, jsonify
from app.services.calendar_service import CalendarService
from app.services.toolkits import get_or_create_user_id
from app.services.mail_service import MailService
from app.services.main_service import MainCaller

api = Namespace('iris', description='iris endpoints')

model = api.model('Iris', {
    'query': fields.String(required=True, description='Pregunta para Iris'),
},)

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
        """Sends user input to Iris so she can generate an answer"""
        data = api.payload
        if not data or "query" not in data:
            return {"error": "Datos de entrada inválidos."}, 400

        user_id = get_or_create_user_id()
        user_question = data["query"]

        response = main_caller.call(user_question, user_id=user_id)
        if not response:
            return {"error": "There is no information about this."}, 404
    
        # Setting up Cookie
        resp = {"response": response}
        response = make_response(jsonify(resp), 200)
        response.set_cookie('user_id', user_id, max_age=24*60*60, path='/', domain="34.44.177.109.nip.io", httponly=True, secure=True, sameSite=None)
        print(response)
        return response

@api.route('/appointments')
class Calendar(Resource):
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'No appointments scheduled')
    def get(self):
        """Get all events in the next two weeks"""
        event_list = calendar.listEvents()

        # Filtrar y mantener solo la clave 'date' en cada evento
        filtered_event_list = [
            {"date": event["date"]} for event in event_list if "date" in event
        ]

        if not filtered_event_list:
            return {"message": 'No appointments scheduled'}, 404

        return {"events": filtered_event_list}, 200
    @api.expect(model)
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'There is a problem with Google Calendar or Email invalid')
    def post(self):
        """Schedule an appointment to the clinic"""
        data = api.payload

        if not data:
            return {"error": "Invalid input data"}, 400
        
        fullname = data.get('fullname')
        month = data.get('month')
        day = data.get('day')
        email = data.get('email')
        starttime = data.get('starttime')
        year = data.get('year')
        
        # Instanciating mail service
        mail_service = MailService()
        # Validating email
        if not mail_service.validate_email(email):
            return {"error": "El formato del correo electrónico es inválido."}, 400
        
        event_create = calendar.createEvent(month=month, day=day, email=email, startTime=starttime, year=year)

        if event_create:
            # Sending email to user
            mail_service = MailService()

            user_mail_body = mail_service.build_body('user_appointment', {"fullname": fullname, "date": f"{day}/{month}/{year} - {starttime}hs"})
            mail_service.send_email('user_appointment', user_mail_body, email)

            # Sending email to clinic
            clinic_mail_body = mail_service.build_body('clinic_appointment', {"fullname": fullname, "user_email": email ,"date": f"{day}/{month}/{year} - {starttime}hs"})
            mail_service.send_email('clinic_appointment', clinic_mail_body, "yuntxwillover@gmail.com")

            return {"message": "Event successfully created"}, 200
        
        return {"error": "There is a problem with Google Calendar"}, 400
