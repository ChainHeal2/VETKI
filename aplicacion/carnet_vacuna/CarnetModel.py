class CarnetModel:
    def __init__(self, data):
        # Si 'data' viene vacío, evitamos que rompa
        if not data:
            return

        # 1. Los datos del paciente y tutor salen de la primera fila (se repiten en el JOIN)
        pet_data = data[0]
        self.pet_id = pet_data.get('pet_id')
        self.pet_name = pet_data.get('pet_name')
        self.species = pet_data.get('species')
        self.breed = pet_data.get('breed')
        self.datebirth = pet_data.get('datebirth')
        self.gender = pet_data.get('gender')
        self.reproductive_status = pet_data.get('reproductive_status')
        self.tutor_name = pet_data.get('tutor_name')
        self.tutor_phone = pet_data.get('tutor_phone')
        self.tutor_address = pet_data.get('tutor_address')
        
        # 2. Recorremos TODAS las filas para armar la lista de vacunas de la tabla
        self.vaccines = []
        for row in data:
            # Validamos que realmente exista una vacuna en esta fila (por el LEFT JOIN si no tiene ninguna)
            if row.get('vaccine_id'):
                self.vaccines.append({
                    'name': row.get('vaccine_name'),
                    'application_date': row.get('application_date'),
                    'lot_number': row.get('lot_number'),
                    'notes': row.get('veterinarian_notes')
                })
