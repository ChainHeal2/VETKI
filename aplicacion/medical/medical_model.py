
class MedicalRecordModel:
    """
    Este objeto toma los datos y lo transofrma en un diccionario
    """
    def __init__(self, data):
        """
        'data' es el diccionario que viene de la base de datos 
        gracias al RealDictCursor que configuraste en db.py
        """
        self.id = data.get('medical_record_id')
        self.reason = data.get('medical_record_reason')
        self.weight = data.get('medical_record_weight')
        self.diagnosis = data.get('medical_record_diagnosis')
        self.treatment = data.get('medical_record_treatment')
        self.date = data.get('medical_record_date')
        self.pet_id = data.get('medical_record_pet_id')
        self.user_id = data.get('medical_record_user_id')
        self.appointment_id = data.get('medical_record_appointment_id')
        #datos de mascota
        self.names = data.get('pet_names')
        self.species_name = data.get('pet_species_name')
        self.race = data.get('pet_race')
        self.datebirth = data.get('pet_datebirth')
        self.gender = data.get('pet_gender')
        self.reproductive_status = data.get('pet_reproductive_status')