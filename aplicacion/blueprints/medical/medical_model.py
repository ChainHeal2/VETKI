
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
        self.temperature = data.get('medical_record_temperature')
        self.heart = data.get('medical_record_heart')
        self.respiratory = data.get('medical_record_respiratory')
        self.water = data.get('medical_record_water')
        self.capillary = data.get('medical_record_capillary')
        self.arterial = data.get('medical_record_arterial')
        self.date = data.get('medical_record_date')
        self.history = data.get('medical_record_medical_history')
        self.signals = data.get('medical_record_signals')
        self.diagnosis = data.get('medical_record_diagnosis')
        self.treatment = data.get('medical_record_treatment')
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
    def if_history(self):
        """
        Indica si la historia clínica es muy corta para mostrar un mensaje en la vista
        """
        if len(self.history) <= 15:
            return '⚠️ Historia muy corta'