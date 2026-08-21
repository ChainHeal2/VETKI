from datetime import date
class MedicalRecordModel:
    """
    Este objeto toma los datos y lo transofrma en un diccionario
    """
    def __init__(self, data):
        """
        'data' es el diccionario que viene de la base de datos 
        gracias al RealDictCursor que configuraste en db.py
        """
        self.medical_id = data.get('medical_record_id')
        self.reason = data.get('medical_record_reason')
        self.weight = data.get('medical_record_weight')
        self.signals = data.get('medical_record_signs')
        self.diagnosis = data.get('medical_record_diagnosis')
        self.treatment = data.get('medical_record_treatment')
        self.date = data.get('medical_record_date')
        self.pet_id = data.get('medical_record_pet_id')
        self.user_id = data.get('medical_record_user_id')
        self.appointment_id = data.get('medical_record_appointment_id')
        #datos de mascota
        self.names = data.get('pet_names')
        self.species= data.get('pet_species_name')
        self.race = data.get('pet_race')
        self.datebirth = data.get('pet_datebirth')
        self.gender = data.get('pet_gender')
        self.reproductive_status = data.get('pet_reproductive_status')
        self.tutor = data.get('pet_tutor_name')
    @property
    def age(self):
        """Esta es tu Lógica de Negocio"""
        if not self.datebirth:
            return "Edad desconocida"
        
        today = date.today()
        # Calculamos la diferencia de años
        years = today.year - self.datebirth.year
        # Ajustamos si aún no ha pasado su cumpleaños este año
        if (today.month, today.day) < (self.datebirth.month, self.datebirth.day):
            years -= 1
            
        if years < 1:
            return "menos de 1 año"
        return f"{years}"