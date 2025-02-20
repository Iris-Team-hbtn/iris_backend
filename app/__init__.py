from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from app.models.model import createVS
from app.api.v1.iris import api as iris_ns

cors = CORS(resources={r"/*": {"origins": "*"}}, supports_credentials=True)

def create_app():
    app = Flask(__name__)
    api = Api(app, version='1.0', title='Iris API', description='Iris Application API')
    
    cors.init_app(app)

    try:
        app.config["vs"] = createVS()
    except Exception as e:
        print(f"Error al cargar VectorStore: {e}")
        app.config["vs"] = None  # Evitar que la app se caiga

    api.add_namespace(iris_ns, path='/iris')

    return app
