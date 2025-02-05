from flask import Flask
from flask_restx import Api
from routes import api_bp  # Importamos el Blueprint con las rutas definidas

def create_app():
    app = Flask(__name__)

    # Configuración de la API
    api = Api(app, version="1.0", title="Chatbot API-Iris", description="API para el chatbot de salud estética", doc="/api/v1/")

    # Registrar el Blueprint con los endpoints del chatbot
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
