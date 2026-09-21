class CarnetModel:
    def __init__(self, data):
        # Mapeamos los nombres de la tabla a atributos del objeto
        self.pet_id = data['pet_id']
        self.pet_name = data['pet_name']
        self.species = data['species']
        self.breed = data['breed']
        self.datebirth = data['datebirth']
        self.gender = data['gender']
        self.reproductive_status = data['reproductive_status']
        self.tutor_name = data['tutor_name']
        self.tutor_phone = data['tutor_phone']
        self.tutor_address = data['tutor_address']
        self.vaccine_id = data['vaccine_id']
        self.vaccine_name = data['vaccine_name']
        self.application_date = data['application_date']
        self.next_due_date = data['next_due_date']