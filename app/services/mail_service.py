import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class MailService:
    def __init__(self):
        """Carga la configuración del servidor SMTP desde variables de entorno."""
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")  # Correo de la clínica
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.clinic_email = os.getenv("CLINIC_EMAIL")  # Destinatario

    def send_email(self, user_email, user_question):
        """Envía un correo con la pregunta del usuario a la clínica."""
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            raise ValueError("Faltan configuraciones de SMTP en el entorno")

        # Configurar el correo
        msg = MIMEMultipart()
        msg["From"] = self.smtp_username
        msg["To"] = self.clinic_email
        msg["Subject"] = "Nueva consulta de un usuario"

        # Contenido del correo
        body = f"""
        Hola,

        Un usuario ha solicitado asistencia humana. Aquí están los detalles:

        Correo del usuario: {user_email}
        Pregunta del usuario: {user_question}

        Por favor, pónganse en contacto con el usuario para brindarle asistencia.

        Atentamente,
        Iris - Asistente Virtual
        """
        msg.attach(MIMEText(body, "plain"))

        # Enviar el correo
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Asegura la conexión
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.smtp_username, self.clinic_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Error enviando correo: {e}")
            return False
