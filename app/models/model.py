import pyrebase
from app.models.vectorstore import VectorStore as vectorstore
import os
from dotenv import load_dotenv

load_dotenv()
firebaseConfig = {
  'apiKey': os.getenv("FIREBASE_API_KEY"),
  'authDomain': "htbn-final-project.firebaseapp.com",
  'projectId': "htbn-final-project",
  'storageBucket': "htbn-final-project.firebasestorage.app",
  'messagingSenderId': "85744476044",
  'appId': "1:85744476044:web:c622fa9a21d442880b40a9",
  'databaseURL': ""
}

def createVS():
  firebase = pyrebase.initialize_app(firebaseConfig)
  storage = firebase.storage()
  # Download PDF from Firebase
  storage.child("protocoloIris.pdf").download(filename="protocoloIris.pdf", path="./")

  return vectorstore('./protocoloIris.pdf')
