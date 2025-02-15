import pyrebase
from app.models.vectorstore import VectorStore as vectorstore
import os
from dotenv import load_dotenv

load_dotenv()
firebaseConfig = {
  'apiKey': os.getenv("FIREBASE_API_KEY"),
  'authDomain': "htbn-final-project.firebaseapp.com",
  'projectId': "htbn-final-project",
  'storageBucket': "htbn-final-project.appspot.com",
  'messagingSenderId': "85744476044",
  'appId': "1:85744476044:web:c622fa9a21d442880b40a9",
  'databaseURL': ""
}

def createVS():
    firebase = pyrebase.initialize_app(firebaseConfig)
    storage = firebase.storage()

    pdf_path = "./protocolo2.pdf"
    
    # Verificar si el archivo ya existe antes de descargarlo
    if not os.path.exists(pdf_path):
        storage.child("protocolo2.pdf").download(filename=pdf_path, path="./")

    return vectorstore(pdf_path)
