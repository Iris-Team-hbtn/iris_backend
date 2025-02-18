from flask_restx import Namespace, Resource, fields
from flask import request, Response, stream_with_context
from app.services.gemini_service import IrisAI
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

chatbot = IrisAI()
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

        def generate():
            for chunk in chatbot.stream_response(user_question, user_id):
                yield f"{chunk}"  # No usamos "data: " para que el frontend lo reciba limpio

        return Response(stream_with_context(generate()), content_type="text/plain")
