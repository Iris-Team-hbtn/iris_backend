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
        """Procesa una pregunta y devuelve la respuesta de Iris en streaming"""
        data = api.payload
        if not data or "query" not in data:
            return {"error": "Datos de entrada inválidos."}, 400

        user_id, user_response = get_or_create_user_id()
        user_question = data["query"]

        response = main_caller.call(user_question, user_id=user_id)

        if not response:
            return {"error": "There is no information about this."}, 404
        
        resp = {"response": response}
    
        # Si se creó un nuevo user_id, devolvemos la respuesta con la cookie ya establecida
        if user_response:
            user_response.set_data(jsonify(resp).get_data())  # Adjuntar los datos a la respuesta
            user_response.status_code = 200
            return user_response
        
        # Si ya existía el user_id, devolvemos solo la respuesta JSON
        return make_response(jsonify(resp), 200)

@api.route('/appointments')
class Calendar(Resource):
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'No appointments scheduled')
    def get(self):
        """Get all events in the next two weeks"""
        event_list = calendar.listEvents()

        print(event_list)
        if not event_list:
            return {"message": 'No appointments scheduled'}, 404
        return {"events": event_list}, 200

    @api.expect(model)
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'There is a problem with Google Calendar')
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
