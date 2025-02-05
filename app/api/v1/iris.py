from flask_restx import Namespace, Resource, fields
from app.models.chatbot import Chatbot

api = Namespace('iris', description='iris endpoints')

model = api.model('Iris', {
    'query': fields.String(required=True, description='Question for Iris')
})

chatbot = Chatbot()

@api.route('/message')
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

        response = chatbot.process_message(data["query"])

        if not response:
            return {"error": "There is no information about this."}, 404
        return {"response": response}, 200
