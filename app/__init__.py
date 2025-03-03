from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from app.models.model import createVS
from app.api.v1.iris import api as iris_ns

# Initialize CORS with support for credentials and allow all origins
cors = CORS(resources={r"/*": {"origins": "*"}}, supports_credentials=True)

def create_app():
    # Create a Flask application instance
    app = Flask(__name__)
    
    # Create an API instance with version, title, and description
    api = Api(app, version='1.0', title='Iris API', description='Iris Application API')
    
    # Initialize CORS for the Flask app
    cors.init_app(app)

    try:
        # Attempt to create and configure the VectorStore
        app.config["vs"] = createVS()
    except Exception as e:
        # Print an error message if VectorStore creation fails and set it to None
        print(f"Error al cargar VectorStore: {e}")
        app.config["vs"] = None  # Prevent the app from crashing

    # Add the iris namespace to the API with the specified path
    api.add_namespace(iris_ns, path='/iris')

    # Return the configured Flask app instance
    return app
