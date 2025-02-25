import pyrebase
from app.models.vectorstore import VectorStore as vectorstore
import os
from dotenv import load_dotenv

load_dotenv()
firebaseConfig = {
  'apiKey': os.getenv("FIREBASE_API_KEY"),
  'authDomain': os.getenv("FIREBASE_AUTH_DOMAIN"),
  'projectId': os.getenv("FIREBASE_PROJECT_ID"),
  'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET"),
  'messagingSenderId': os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
  'appId': "FIREBASE_APP_ID",
  'databaseURL': ""
}

def createVS():
  firebase = pyrebase.initialize_app(firebaseConfig)
  storage = firebase.storage()

  storage.child("protocoloIris.pdf").download(filename="protocoloIris.pdf", path="./")

  return vectorstore('./protocoloIris.pdf')
