from flask_restx import Namespace, Resource, fields


api = Namespace('iris', description='iris endpoints')

# Define the review model for input validation and documentation
review_model = api.model('Iris', {
    'query': fields.String(required=True, description='Question for Iris')
})

@api.route('/')
class Query(Resource):
    @api.expect(review_model)
    @api.response(200, 'Answer retrieved correctly')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'There is no information about this')
    def post(self):

        """A question is received"""
        data = api.payload
        print(data)
        print(data.get('query'))
        search = vs.search(data.get('query'))

        return {'answer': search}, 200

