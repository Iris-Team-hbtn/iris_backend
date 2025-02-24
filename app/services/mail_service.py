import os
from email.message import EmailMessage
from dotenv import load_dotenv
import ssl
import smtplib

load_dotenv()

class MailService:
    def __init__(self):
        """Carga la configuración del servidor SMTP desde variables de entorno."""
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")

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
            Hola,
            
            Un usuario ha sido agendado para una consulta médica.
            Correo del usuario: {obj.get('user_email')}
            Fecha de la consulta: {obj.get('date')} 

            Atentamente,
            Iris - Asistente Virtual
            """
        elif subject == 'user_appointment':
            body = f"""
            Hola,
            
            Te has agendado con éxito en Holberton Clinic, esperamos verte!
            Fecha de la consulta: {obj.get('date')} 

            Para cancelaciones, por favor comunícate a:
            09x xxx xxx

            Atentamente,
            Iris - Asistente Virtual
            """
        elif subject == 'contact_request':
            body = f"""
            Hola,

            El usuario ha solicitado que un profesional se ponga en contacto.
            Correo del usuario: {obj.get('user_email')}
            Consulta pendiente: {obj.get('user_question')}

            Por favor, pónganse en contacto a la brevedad.

            Atentamente,
            Iris - Asistente Virtual
            """
        return body

    def send_email(self, subject, body, destination):
        """Envía un correo utilizando la configuración SMTP."""
        if not self.username or not self.password:
            raise ValueError("Faltan configuraciones de SMTP en el entorno")

        self.em = EmailMessage()
        self.em["From"] = self.username
        self.em["To"] = destination

        if subject == 'user_question':
            self.em["Subject"] = "Nueva consulta de un usuario"
        elif subject == 'clinic_appointment':
            self.em["Subject"] = "Nueva consulta agendada"
        elif subject == 'user_appointment':
            self.em["Subject"] = "Consulta agendada con éxito"
        elif subject == 'contact_request':
            self.em["Subject"] = "Solicitud de contacto - Consulta pendiente"

        self.em.set_content(body)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(self.username, self.password)
                smtp.sendmail(self.username, destination, self.em.as_string())
            print("Correo enviado exitosamente.")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
