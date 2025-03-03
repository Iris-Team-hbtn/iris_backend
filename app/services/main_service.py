from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
from app.services.mail_service import MailService
from app.services.calendar_service import CalendarService
from app.services.gemini_service import IrisAI
from app.services.creator_service import ObjectCreator
from app.services.scheduler_service import EventScheduler
from app.services.toolkits import ToolkitService
import json
import re

class MainCaller:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        # Initialize the Google Generative AI model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        # Initialize the toolkit service
        self.toolkit = ToolkitService()

    def call(self, user_input, user_id):
        # Initialize services
        iris = IrisAI()
        creator = ObjectCreator()
        eventscheduler = EventScheduler()
        # Load chat history for the user
        chat_history = self.toolkit._load_chat_history(user_id)

        # If no chat history, add a welcome message
        if not chat_history:
            welcome_message = {
                "user": "Hola Iris!",
                "assistant": "Hola! Soy Iris, una asistente virtual dedicada a ayudar a liberar tus consultas sobre Holberton Clinic!"
            }
            chat_history.append(welcome_message)

        # Summarize chat history if needed
        if self.toolkit.should_summarize(user_id):
            summary_prompt = "Resume brevemente el siguiente historial de conversación, guardando información clave:"
            history_text = "\n".join(
                [f"Usuario: {e['user']}\nAsistente: {e['assistant']}" for e in chat_history]
            )
            summary_response = self.llm.invoke([
                SystemMessage(content=summary_prompt),
                HumanMessage(content=history_text)
            ])
            chat_history = [{"user": "Resumen", "assistant": summary_response.content}]

        # Create system prompt for categorizing the message
        system_prompt = """
        Tu rol es clasificar los mensajes dentro de las siguientes categorías:
        1. Conversación con la IA
        2. Solicitando ayuda a soporte humano
        3. Busca agendarse en la clínica
        Debes responder solamente con el número de la categoría y nada más.

        Debes entender el contexto y dirección de la conversación a través del historial de chat:
        """
        history_text = "\n".join(
            [f"Usuario: {e['user']}\nAsistente: {e['assistant']}" for e in chat_history]
        ) or ""
        system_prompt += history_text
        # Invoke the AI model to categorize the user input
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ])
        print(f"La categoría del mensaje es: {response.content}")

        # Handle the response based on the category
        match response.content:
            case '2':
                # Handle support request
                mail_obj = creator.email_object(user_id=user_id)
                if mail_obj:
                    match_obj = re.search(r"\{.*\}", mail_obj.strip(), re.DOTALL)
                    if match_obj:
                        json_text = match_obj.group(0)
                        try:
                            email_obj = json.loads(json_text)
                            self.create_support_mail(email_obj)
                            return "Tu consulta ha sido elevada a soporte con éxito."
                        except json.JSONDecodeError:
                            print("Error al decodificar JSON, contenido inválido.")
                    else:
                        print("No se encontró un JSON válido en la respuesta.")
                return iris.call_iris(user_input=user_input, user_id=user_id)

            case '3':
                # Handle scheduling request
                schedule_date = creator.date_object(user_id=user_id)
                print(f"Este es el string que salió del creador de objetos: {schedule_date}")
                if schedule_date:
                    match_obj = re.search(r"\{.*\}", schedule_date.strip(), re.DOTALL)
                    if match_obj:
                        json_text = match_obj.group(0)
                        try:
                            date_obj = json.loads(json_text)
                            print(date_obj)
                            if date_obj:
                                availability = eventscheduler.check(
                                    day=date_obj['day'],
                                    month=date_obj['month'],
                                    starttime=date_obj['starttime']
                                )
                                print(availability)
                                if availability.strip().lower() == 'disponible':
                                    self.create_event(date_obj)
                                    return "Has sido agendado con éxito."
                                else:
                                    user_input += " Los horarios disponibles para el día consultado son: " + availability
                                    return iris.call_iris(user_input=user_input, user_id=user_id)
                        except json.JSONDecodeError:
                            print("Error al decodificar JSON, contenido inválido.")
                    else:
                        print("No se encontró un JSON válido en la respuesta.")
                return iris.call_iris(user_input=user_input, user_id=user_id)

            case _:
                # Default case: continue conversation with the AI
                return iris.call_iris(user_input=user_input, user_id=user_id)

    @staticmethod
    def create_event(date_obj):
        # Create a calendar event
        calendar = CalendarService()
        fullname = date_obj.get('fullname')
        month = date_obj.get('month')
        day = date_obj.get('day')
        email = date_obj.get('email')
        starttime = date_obj.get('starttime')
        year = date_obj.get('year', 2025)
        event_create = calendar.createEvent(month=month, day=day, email=email, startTime=starttime, year=year)

        if event_create:
            mail_service = MailService()

            # Send confirmation email to the user
            user_mail_body = mail_service.build_body('user_appointment', {
                "fullname": fullname,
                "date": f"{day}/{month}/{year} - {starttime}hs"
            })
            mail_service.send_email('user_appointment', user_mail_body, email)

            # Send notification email to the clinic
            clinic_mail_body = mail_service.build_body('clinic_appointment', {
                "fullname": fullname,
                "user_email": email,
                "date": f"{day}/{month}/{year} - {starttime}hs"
            })
            mail_service.send_email('clinic_appointment', clinic_mail_body, "yuntxwillover@gmail.com")

    @staticmethod
    def create_support_mail(email_obj):
        # Create a support email
        mail_service = MailService()
        fullname = email_obj.get('fullname')
        email = email_obj.get('email')
        question = email_obj.get('user_question')
        support_mail_body = mail_service.build_body('user_question', {
            "fullname": fullname,
            "user_email": email,
            "user_question": question
        })
        mail_service.send_email('user_question', support_mail_body, "yuntxwillover@gmail.com")
