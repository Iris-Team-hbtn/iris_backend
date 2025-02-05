from flask import Flask
from flask_restx import Api
from app.models.model import createVS
from app.api.v1.iris import api as iris_ns

def create_app():
    app = Flask(__name__)
    api = Api(app, version='1.0', title='Iris API', description='Iris Application API')

    #createVS()

    api.add_namespace(iris_ns, path='/iris')

    return app
