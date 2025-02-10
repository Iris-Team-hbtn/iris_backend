from flask_restx import Namespace, Resource, fields
from app.services.gemini_service import IrisAI
from typing import Dict, Tuple, Optional, Union

api = Namespace('iris', description='iris endpoints')

model = api.model('Iris', {
    'query': fields.String(required=True, description='Question for Iris')
})

chatbot = IrisAI()

@api.route('/message')
class Query(Resource):
    @api.expect(model)
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'There is no information about this')
    def post(self) -> Tuple[Dict[str, str], int]:
        """A question is received"""
        data: Optional[Dict[str, str]] = api.payload
        if not data or "query" not in data:
            return {"error": "Invalid input data."}, 400

        response: Optional[str] = chatbot.call_iris(data["query"])

        if not response:
            return {"error": "There is no information about this."}, 404
        return {"response": response}, 200
