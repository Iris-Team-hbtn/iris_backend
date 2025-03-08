import os
import re
from email.message import EmailMessage
from dotenv import load_dotenv
import ssl
import smtplib

load_dotenv()

class MailService:
    def __init__(self):
        """Loads credentials into OS."""
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        
        self.email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    def validate_email(self, email):
        """
        Validate email format using regex pattern
        Args:
            email (str): Email address to validate
        Returns:
            bool: True if email is valid, False otherwise
        """
        return bool(self.email_pattern.match(email))

    @staticmethod
    def build_body(subject, obj={}):
        body = ''
        if subject == 'user_question':
            body = f"""
            Hola,

            Un usuario ha solicitado asistencia humana. Aquí están los detalles:

            Correo del usuario: {obj.get('user_email')}
            Pregunta del usuario: {obj.get('user_question')}

            Por favor, pónganse en contacto con el usuario para brindarle asistencia.

            Atentamente,
            Iris - Asistente Virtual
            """
        elif subject == 'clinic_appointment':
            body = f"""
            Hola!
            
            Un usuario ha sido agendado para una consulta médica
            Correo del usuario: {obj.get('user_email')}
            Fecha de la consulta: {obj.get('date')} 

            Atentamente,
            Iris - Asistente Virtual
            """
        elif subject == 'user_appointment':
            body = f"""
            Hola {obj.get('fullname')},
            
            Te has agendado con exito en Holberton Clinic, esperamos verte!
            Fecha de la consulta: {obj.get('date')} 

            Para cancelaciones por favor comunicarse a:
            09x xxx xxx

            Atentamente,
            Iris - Asistente Virtual
            """
        return body

    def send_email(self, subject, body, destination):
        """We send a mail with subject options"""
        if not self.username or not self.password:
            raise ValueError("Faltan configuraciones de SMTP en el entorno")

        # Configurar el correo
        self.em = EmailMessage()
        self.em["From"] = self.username
        self.em["To"] = destination

        if subject == 'user_question':
            self.em["Subject"] = "Nueva consulta de un usuario"
        elif subject == 'clinic_appointment':
            self.em["Subject"] = "Nueva consulta agendada"
        elif subject == 'user_appointment':
            self.em["Subject"] = "Consulta agendada con exito"

        self.em.set_content(body)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(self.username, self.password)
                smtp.sendmail(self.username, destination, self.em.as_string())
            print("Correo enviado exitosamente.")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")


