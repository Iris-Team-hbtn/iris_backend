import uuid

class ConsultationScheduler:
    def __init__(self):
        self.appointments = {}

    def schedule_appointment(self, data):
        appointment_id = str(uuid.uuid4())
        self.appointments[appointment_id] = {
            "client_id": data["client_id"],
            "date": data["date"],
            "status": "Confirmed"
        }
        return appointment_id
