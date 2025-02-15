from flask_restx import Namespace, Resource, fields
from flask import make_response, jsonify
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

        user_id = get_or_create_user_id()
        response = chatbot.call_iris(data["query"], user_id)

        if not response:
            return {"error": "There is no information about this."}, 404
    
        #Configuramos la respuesta en cookie
        resp = {"response": response}
        response = make_response(jsonify(resp), 200)
        response.set_cookie('user_id', user_id, max_age=24*60*60)  # cookie solo por 1 dia
        print(response)
        return response
