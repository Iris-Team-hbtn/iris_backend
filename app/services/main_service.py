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
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.toolkit = ToolkitService()

    def call(self, user_input, user_id):
        # Instanciating services
        iris = IrisAI()
        creator = ObjectCreator()
        eventscheduler = EventScheduler()
        chat_history = self.toolkit._load_chat_history(user_id)

        if not chat_history:
            welcome_message = {
                "user": "Hola Iris!",
                "assistant": "Hola! Soy Iris, una asistente virtual dedicada a ayudar a liberar tus consultas sobre Holberton Clinic!"
            }
            chat_history.append(welcome_message)

        if self.toolkit.should_summarize(user_id):
            summary_prompt = "Resume brevemente el siguiente historial de conversación, guardando información clave:"
            history_text = "\n".join(
                [f"Usuario: {e['user']}\nAsistente: {e['assistant']}" for e in chat_history]
            )
            print(f"history text es: {history_text}")
            summary_response = self.llm.invoke([SystemMessage(content=summary_prompt), HumanMessage(content=history_text)])
            print(summary_response)
            chat_history = [{"user": "Resumen", "assistant": summary_response.content}]

        # We categorize the chat history direction and take actions with that context
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
        # We ask the clasification
        response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_input)])
        print(f"La categoría del mensaje es: {response.content}")

        match response.content:
            case '2':
                mail_obj = creator.email_object( user_input, user_id=user_id)
                if mail_obj:
                    match = re.search(r"\{.*\}", mail_obj.strip(), re.DOTALL)
                    if match:
                        json_text = match.group(0)
                        try:
                            email_obj = json.loads(json_text)
                            self.create_support_mail(email_obj)
                            return "Hemos enviado tu consulta al equipo de la clínica y pronto recibirás una respuesta. ¡Gracias por tu paciencia!"
                        except json.JSONDecodeError:
                            print("Error al decodificar JSON, contenido inválido.")
                    else:
                        print("No se encontró un JSON válido en la respuesta.")

                return iris.call_iris(user_input=user_input, user_id=user_id)

            case '3':
                calendar = CalendarService()
                schedule_date = creator.date_object(user_input, user_id=user_id)
                print(f"Este es el string que salio del creador de objetos {schedule_date}")
                if schedule_date:
                    match = re.search(r"\{.*\}", schedule_date.strip(), re.DOTALL)
                    if match:
                        json_text = match.group(0)
                        try:
                            date_obj = json.loads(json_text)
                            print(date_obj)
                            if date_obj:
                                emails = calendar.getUniqueAttendees()
                                print(emails)
                                if date_obj["email"].lower() not in emails:
                                    availability = eventscheduler.check(day=date_obj['day'], month=date_obj['month'], starttime=date_obj['starttime'])
                                    print(availability)
                                    if availability == 'Disponible':
                                        self.create_event(date_obj)
                                        return "Tu consulta ha sido agendada con éxito. Recuerda que nuestro horario de atención es de lunes a sábado, de 11:00 a 19:00. Te atenderemos en la fecha y hora seleccionadas. ¡Gracias por confiar en nosotros!"
                                    else:
                                        user_input += ". Los horarios disponibles para el dia que consulta el usuario son: " + availability
                                        return iris.call_iris(user_input=user_input, user_id=user_id)
                                else:
                                    return "Veo que ya te has agendado en nuestra clínica, si hay un error por favor comunícate con nosotros para ayudarte."
                        except json.JSONDecodeError:
                            print("Error al decodificar JSON, contenido inválido.")
                    else:
                            print("No se encontró un JSON válido en la respuesta.")
                        
                return iris.call_iris(user_input=user_input, user_id=user_id)

            case _: 
                # Situation '1' or anything else
                return iris.call_iris(user_input=user_input, user_id=user_id)

    @staticmethod
    def create_event(date_obj):
        calendar = CalendarService()
        fullname = date_obj.get('fullname')
        month = date_obj.get('month')
        day = date_obj.get('day')
        email = date_obj.get('email')
        starttime = date_obj.get('starttime')
        year = date_obj.get('year')

        # Validating email
        mail_service = MailService()
        if not mail_service.validate_email(email):
            print("El correo electrónico proporcionado no es válido.")
            return

        event_create = calendar.createEvent(month=month, day=day, email=email, startTime=starttime, year=year)

        if event_create:
            # Sending email to user
            mail_service = MailService()

            user_mail_body = mail_service.build_body('user_appointment', {"fullname": fullname, "date": f"{day}/{month}/{year} - {starttime}hs"})
            mail_service.send_email('user_appointment', user_mail_body, email)

            # Sending email to clinic
            clinic_mail_body = mail_service.build_body('clinic_appointment', {"fullname": fullname, "user_email": email ,"date": f"{day}/{month}/{year} - {starttime}hs"})
            mail_service.send_email('clinic_appointment', clinic_mail_body, "yuntxwillover@gmail.com")

    @staticmethod
    def create_support_mail(email_obj):
        mail_service = MailService()

        fullname = email_obj.get('fullname')
        email = email_obj.get('email')
        question = email_obj.get('user_question')

        # Validating email
        if not mail_service.validate_email(email):
            print("El correo electrónico para soporte no es válido.")
            return

        support_mail_body = mail_service.build_body('user_question', {"fullname": fullname ,"user_email": email, "user_question": question})
        mail_service.send_email('user_question', support_mail_body, "yuntxwillover@gmail.com")