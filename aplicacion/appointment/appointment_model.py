class AppointmentModel:
    def __init__(self, data):
        # Mapeamos los nombres de la tabla a atributos del objeto
        self.id = data.get('appointment_id')
        self.appointment_id = data.get('appointment_id')
        self.date = data.get('appointment_date')
        self.pet_names = data.get('pet_names')
        self.pet_id = data.get('pet_id')

    def to_dict(self):
        """La clave para tu futura API: convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "date": str(self.date) if self.date else None,
            "pet_names": self.pet_names,
            "pet_id": self.pet_id
        }