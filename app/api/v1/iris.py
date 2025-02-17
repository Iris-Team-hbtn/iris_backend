from flask_restx import Namespace, Resource, fields
from flask import make_response, request
from app.services.gemini_service import IrisAI
from app.services.toolkits import get_or_create_user_id

api = Namespace('iris', description='iris endpoints')

model = api.model('Iris', {
    'query': fields.String(required=True, description='Question for Iris')
})

chatbot = IrisAI()  # Aquí está la instancia correcta

@api.route('/chat')
class Query(Resource):
    @api.expect(model)
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'There is no information about this')
    def post(self):
        """A question is received"""
        data = request.get_json()
        user_message = data.get("query", "")

        user_id = request.cookies.get("user_id")
        if not user_id:
            user_id = get_or_create_user_id()
            new_user = True
        else:
            new_user = False

        response = chatbot.call_iris(user_message, user_id)  # Cambiado `model` por `chatbot`

        # Agregar cookie si es un nuevo usuario
        if new_user:
            response = make_response(response)
            response.set_cookie("user_id", user_id, max_age=24*60*60)

        return response
