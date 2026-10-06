class AppointmentModel:
    def __init__(self, data):
        # Mapeamos los nombres de la tabla a atributos del objeto
        self.id = data.get('appointment_id')
        self.pet_id = data.get('pet_id')
        self.date = data.get('appointment_date')
        self.reason = data.get('appointment_reason')
        self.end_date = data.get('appointment_end_date')
        self.pet_id = data.get('pet_id')