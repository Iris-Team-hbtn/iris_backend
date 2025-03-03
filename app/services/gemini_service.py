# Importing necessary libraries and modules
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
import markdown
from dotenv import load_dotenv
from collections import deque
from app.data.prompts import system_prompt
from app.services.toolkits import ToolkitService
from app.services.mail_service import MailService

class IrisAI:
    """
    A class that implements an AI assistant using Google's Generative AI (Gemini model).
    Handles chat interactions and email functionality.
    """
    def __init__(self):
        # Initialize environment variables and API key
        load_dotenv()
        self._google_api_key = os.getenv("GOOGLE_API_KEY", "")
        
        # Configure the Gemini LLM model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b",
            temperature=0.7,  # Controls randomness in responses
            max_tokens=None,  # No token limit
            timeout=None,     # No timeout limit
            max_retries=2,    # Number of retry attempts
        )
        # Initialize service components
        self.toolkit = ToolkitService()
        self.mail_service = MailService()

    def _handle_email_request(self, user_input, user_id):
        """
        Handles email-related requests from users.
        Args:
            user_input (str): User's email address
            user_id: Unique identifier for the user
        Returns:
            str: Status message about email operation
        """
        if not self.mail_service.validate_email(user_input):
            return "Formato de correo inválido. Por favor, ingresa uno válido."
        
        subject = "Correo de confirmación"
        body = f"Se ha recibido tu solicitud: {user_input}"
        self.mail_service.send_email(subject, body, user_input)
        return "Correo enviado con éxito."

    def format_response(self, text):
        """
        Converts AI response text to Markdown format.
        Args:
            text (str): Raw text to be formatted
        Returns:
            str: Markdown formatted text
        """
        return markdown.markdown(text)

    def call_iris(self, user_input, user_id):
        """
        Main method to process user queries and generate AI responses.
        Args:
            user_input (str): User's query or message
            user_id: Unique identifier for the user
        Returns:
            dict: Contains formatted AI response
        """
        # Check if query has been processed before
        if self.toolkit._has_query_been_sent(user_id, user_input):
            return "Ya hemos procesado esta consulta anteriormente. ¿Necesitas más información?"

        # Mark query as processed and load chat history
        self.toolkit._mark_query_as_sent(user_id, user_input)
        chat_history = self.toolkit._load_chat_history(user_id)
        if isinstance(chat_history, deque):
            chat_history = list(chat_history)

        # Search for relevant information in vector store
        vs = self.toolkit.get_vs()
        text = vs.search(user_input) or "No encontré información relevante en la base de datos."
        system_message_content = system_prompt() + "\nFuente: protocoloIris.pdf\n" + "\n" + text

        # Prepare conversation messages
        messages = [SystemMessage(content=system_message_content)]
        for entry in chat_history:
            messages.append(HumanMessage(content=entry["user"]))
            messages.append(AIMessage(content=entry["assistant"]))
        messages.append(HumanMessage(content=user_input))

        # Generate and format response
        response = self.llm.invoke(messages)
        formatted_response = self.format_response(response.content)
        
        # Update chat history
        chat_history.append({"user": user_input, "assistant": formatted_response})
        self.toolkit._save_chat_history(user_id, list(chat_history))

        return {"text": formatted_response}
