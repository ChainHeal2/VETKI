from datetime import date

class PetModel:
    """
    Este objeto toma los datos y lo transofrma en un diccionario
    """
    def __init__(self, data):
        """
        'data' es el diccionario que viene de la base de datos 
        gracias al RealDictCursor que configuraste en db.py
        """
        self.pet_id = data.get('pet_id')
        self.names = data.get('pet_names')
        self.species_name = data.get('pet_species_name')
        self.race = data.get('pet_race')
        self.datebirth = data.get('pet_datebirth')
        self.microchip = data.get('pet_microchip')
        self.gender = data.get('pet_gender')
        self.reproductive_status = data.get('pet_reproductive_status')
        self.tutor_name = data.get('pet_tutor_name')
        self.tutor_address = data.get('pet_tutor_address')
        self.tutor_phone = data.get('pet_tutor_phone')

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
        return f"{years} años"