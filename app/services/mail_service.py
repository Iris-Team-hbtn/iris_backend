import os
import re
from email.message import EmailMessage
from dotenv import load_dotenv
import ssl
import smtplib

# Load environment variables from .env file
load_dotenv()

class MailService:
    """Class to handle email operations including validation and sending"""
    
    def __init__(self):
        # Initialize with SMTP credentials from environment variables
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        # Regular expression pattern for email validation
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
        """
        Build email body based on subject type and provided object data
        Args:
            subject (str): Type of email to send ('user_question', 'clinic_appointment', 'user_appointment')
            obj (dict): Dictionary containing data to include in email body
        Returns:
            str: Formatted email body
        """
        body = ''
        # Template for user questions/support requests
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
        # Template for clinic notifications about new appointments
        elif subject == 'clinic_appointment':
            body = f"""
            Hola!
            
            Un usuario ha sido agendado para una consulta médica.
            Correo del usuario: {obj.get('user_email')}
            Fecha de la consulta: {obj.get('date')} 

            Atentamente,
            Iris - Asistente Virtual
            """
        # Template for user appointment confirmations
        elif subject == 'user_appointment':
            body = f"""
            Hola {obj.get('fullname')},
            
            Te has agendado con éxito en Holberton Clinic, esperamos verte!
            Fecha de la consulta: {obj.get('date')} 

            Para cancelaciones por favor comunicarse a:
            09x xxx xxx

            Atentamente,
            Iris - Asistente Virtual
            """
        else:
            body = "Mensaje sin cuerpo definido."
        return body

    def send_email(self, subject, body, destination):
        """
        Send email using Gmail SMTP server
        Args:
            subject (str): Email subject type
            body (str): Email content
            destination (str): Recipient email address
        Raises:
            ValueError: If SMTP credentials are missing
            Exception: If email sending fails
        """
        # Check if SMTP credentials are available
        if not self.username or not self.password:
            raise ValueError("Faltan configuraciones de SMTP en el entorno")
            
        # Create email message
        em = EmailMessage()
        em["From"] = self.username
        em["To"] = destination

        # Set subject based on email type
        if subject == 'user_question':
            em["Subject"] = "Nueva consulta de un usuario"
        elif subject == 'clinic_appointment':
            em["Subject"] = "Nueva consulta agendada"
        elif subject == 'user_appointment':
            em["Subject"] = "Consulta agendada con éxito"
        else:
            em["Subject"] = subject

        em.set_content(body)
        # Create SSL context for secure connection
        context = ssl.create_default_context()

        try:
            # Connect to Gmail SMTP server and send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(self.username, self.password)
                smtp.sendmail(self.username, destination, em.as_string())
            print("Correo enviado exitosamente.")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            raise e
