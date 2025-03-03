# Import required libraries
import pyrebase  # Firebase Python SDK
from app.models.vectorstore import VectorStore as vectorstore  # Custom vector store implementation
import os  # Operating system interface
from dotenv import load_dotenv  # Load environment variables from .env file

# Load environment variables
load_dotenv()

# Firebase configuration dictionary
firebaseConfig = {
  'apiKey': os.getenv("FIREBASE_API_KEY"),  # Get API key from environment variables
  'authDomain': "htbn-final-project.firebaseapp.com",
  'projectId': "htbn-final-project",
  'storageBucket': "htbn-final-project.firebasestorage.app",
  'messagingSenderId': "85744476044",
  'appId': "1:85744476044:web:c622fa9a21d442880b40a9",
  'databaseURL': ""  # Empty as database URL is not used
}

def createVS():
  """
  Creates a vector store from a PDF file stored in Firebase.
  
  Returns:
      VectorStore: An instance of the vector store containing the processed PDF
  """
  # Initialize Firebase app with config
  firebase = pyrebase.initialize_app(firebaseConfig)
  # Get storage instance
  storage = firebase.storage()

  # Download the PDF file from Firebase storage
  storage.child("protocoloIris.pdf").download(filename="protocoloIris.pdf", path="./")

  # Create and return vector store from the downloaded PDF
  return vectorstore('./protocoloIris.pdf')
