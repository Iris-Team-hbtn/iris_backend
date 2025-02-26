# Iris - Health Aesthetics Chatbot

Iris is a chatbot designed to help aesthetic health clinics filter potential clients, answer FAQs, and manage consultations. Built with Flask, Faiss, Gemini 1.5 Flash 8B, Firebase and Google Calendar API.

## Key Features

- FAQ Management: Handles common questions and provides relevant information
- Client Screening: Evaluates user eligibility before specialist referral
- Appointment Scheduling: Google Calendar integration for automated booking
- Chat Memory: Efficient conversation history management
- Advanced AI: Gemini 1.5 Flash 8B for enhanced responses
- Vector Storage: Faiss for efficient knowledge base searches

## Project Structure

```
/iris-backend
├── /app
│   ├── /api/v1
│   │   ├── __init__.py
│   │   ├── iris.py    # Defines the routes for Iris
│   └── /data
│   │     ├── prompts.py    # Indications/Rules for Iris
│   │     ├── chat_history.json    # The stored history from Iris
│   └── /models
│   │     ├── modelgemini_service.py    # Google API configuration
│   │     ├── vectorstore.py    # Vectorstore management
│   └── /services
│   │     ├── creator_service.py    # Define the services
│   │     ├── model.py    # Firebase connection
│   │     ├── calendar_service.py    # Google calendar configuration
│   │     ├── gemini_service.py    # Implements an AI chat system using Google's Gemini
│   │     ├── mail_Service.py    # Implements the config for mail managment
│   │     ├── scheduler_service.py    # Implements the scheduler managment
│   │     ├── toolkits.py    # Tools to be used (methods and functions)
│   │
│   └── __init__.py    # Create the app flask with Iris and a Blueprint for calendar
├── .env    # Keep yours Keys save
├── app.py    # Create the app
├── config.py    # Configuration
├── run.py    # Main API entry
└── requirements.txt # The requirements needed
```

## Setup Instructions

1. Clone repository:

```bash
git clone https://github.com/Iris-Team-hbtn/iris_backend.git
cd iris-backend
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

## 3. Install dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## 4. Configure credentials:

- Create a file called ".env" .

```bash
touch iris_backennd/.env
```

- Add firebase_config.json to iris_backend/.env
- Add google_credentials.json to iris_backend/.env

## 5. Run server:

```bash
python run.py
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /iris/chat | Send chatbot message |
| POST | /iris/schedule | Schedule appointment |
| GET | /calendar/appointments | Get appointments |     # Aun por implementar

## License

Alguna licencia para nuestro proyecto

## Contact

Questions or suggestions: nuestro email