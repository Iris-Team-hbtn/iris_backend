import pyrebase
import vectorstore

firebaseConfig = {
  'apiKey': "AIzaSyANGIbB4Ckqv8QxPcEa2shZrr3nJ-uo4LY",
  'authDomain': "htbn-final-project.firebaseapp.com",
  'projectId': "htbn-final-project",
  'storageBucket': "htbn-final-project.firebasestorage.app",
  'messagingSenderId': "85744476044",
  'appId': "1:85744476044:web:c622fa9a21d442880b40a9",
  'databaseURL': ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

storage.child("protocolo.pdf").download(filename="protocol.pdf", path="./")

vs = vectorstore.VectorStore('./protocol.pdf')

result = vs.search('Tratamiento capilar')
print(result)