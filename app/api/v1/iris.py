from flask_restx import Namespace, Resource, fields
from flask import request, Response
from app.services.gemini_service import IrisAI
from app.services.calendar_service import CalendarService
from app.services.toolkits import get_or_create_user_id
from app.services.mail_service import MailService


api = Namespace('iris', description='iris endpoints')

model = api.model('Iris', {
    'query': fields.String(required=True, description='Pregunta para Iris'),
},)

email_model = api.model(
    'EmailRequest',
    {
        'email': fields.String(required=True, description='Correo del usuario'),
        'question': fields.String(required=True, description='Pregunta del usuario'),
    },
)

calendar_model = api.model('Calendar', {
    'fullname': fields.String(required=True, description='Fullname of client'),
    'month': fields.Integer(required=True, description='Month of the appointment'),
    'day': fields.Integer(required=True, description='Day of the appointment'),
    'startime': fields.Integer(required=True, description='Start Time of the appointment'),
    'email': fields.String(required=True, description='Email to invite to Google Calendar event'),
    'year': fields.Integer(required=False, description='Year of the appointment')
})

chatbot = IrisAI()
calendar = CalendarService()
mail_service = MailService()

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

        user_id = get_or_create_user_id()
        user_question = data["query"]

        if not response:
            return {"error": "There is no information about this."}, 404
    
        #Configuramos la respuesta en cookie
        resp = {"response": response}
        response = make_response(jsonify(resp), 200)
        response.set_cookie('user_id', user_id, max_age=24*60*60)  # cookie solo por 1 dia
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

        print(event_list)
        if not event_list:
            return {"message": 'No appointments scheduled'}, 404
        return {"events": event_list}, 200

    @api.expect(model)
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'There is a problem with Google Calendar')
    def post(self):
        """Schedule an appointment to the clinic"""
        data = api.payload

        if not data:
            return {"error": "Invalid input data"}, 400
        
        month = data.get('month')
        day = data.get('day')
        email = data.get('email')
        starttime = data.get('starttime')
        year = data.get('year')
        event_create = calendar.createEvent(month=month, day=day, email=email, startTime=starttime, year=year)

        if event_create:
            return {"message": "Event successfully created"}, 200
        
        return {"error": "There is a problem with Google Calendar"}, 400
