from flask_restx import Namespace, Resource, fields
from flask import make_response, request, Response, stream_with_context
from app.services.gemini_service import IrisAI
from app.services.toolkits import get_or_create_user_id

api = Namespace('iris', description='iris endpoints')

model = api.model('Iris', {
    'query': fields.String(required=True, description='Question for Iris')
})

chatbot = IrisAI()

@api.route('/chat')
class Query(Resource):
    @api.expect(model)
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'There is no information about this')
    def post(self):
        """A question is received"""
        data = api.payload
        if not data or "query" not in data:
            return {"error": "Invalid input data."}, 400

        user_message = data["query"]
        user_id = request.cookies.get("user_id") or get_or_create_user_id()
        new_user = not request.cookies.get("user_id")  # Si no hay cookie, es un nuevo usuario

        response = chatbot.stream_response(user_message, user_id)

        # Si el usuario es nuevo, configurar la cookie
        if new_user:
            response = make_response(response)
            response.set_cookie('user_id', user_id, max_age=24*60*60)  # Cookie válida por 1 día
        
        return response
