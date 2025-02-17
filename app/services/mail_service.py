import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_to_agent(user_id):
    # Cargar configuración desde .env
    sender_email = os.getenv("SENDER_EMAIL")
    recipient_email = os.getenv("AGENT_EMAIL")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    password = os.getenv("EMAIL_PASSWORD")
    
    # Crear mensaje
    subject = "Solicitud de contacto con un agente humano"
    body = f"El usuario con ID {user_id} ha solicitado contactar con un agente humano."
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    # Enviar el correo
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print(f"[INFO] Correo enviado al agente para el usuario {user_id}.")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo: {e}")
