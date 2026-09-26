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
    def etapa_vida(self):
        """Regresa cachorro, adulto o senior según la edad de la mascota"""
        if not self.datebirth:
            return "Edad desconocida"
        today = date.today()
        # Calculamos la diferencia de años
        years = today.year - self.datebirth.year
        # Ajustamos si aún no ha pasado su cumpleaños este año
        if (today.month, today.day) < (self.datebirth.month, self.datebirth.day):
            years -= 1
        if years < 1:
            return "cachorro"
        elif years >= 1 and years < 7:
            return "adulto"
        else:
            return "senior"
        
    @property
    def telefono_limpio(self):
        """Limpia espacios y guiones para que el sistema de llamadas no falle"""
        if not self.tutor_phone:
            return ""
        # Reemplaza espacios, guiones o paréntesis que la gente suele poner al escribir números
        return (self.tutor_phone
                .replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", ""))

    @property
    def tiene_telefono(self):
        """Retorna True si hay un teléfono válido para mostrar el botón de llamada"""
        return bool(self.tutor_phone and len(self.tutor_phone.strip()) >= 7)
    @property
    def age(self):
        """Calcula y devuelve la edad en formato de texto"""
        if not self.datebirth:
            return "Edad desconocida"
        
        today = date.today()
        years = today.year - self.datebirth.year
        if (today.month, today.day) < (self.datebirth.month, self.datebirth.day):
            years -= 1
            
        if years < 1:
            return "Menos de 1 año"
        elif years == 1:
            return "1 año"
        else:
            return f"{years} años"
        
    @property
    def alerta_microchip(self):
        """Indica el estado del microchip de forma amigable para terreno"""
        if not self.microchip or not self.microchip.strip():
            return "⚠️ Sin Microchip (Requiere implante)"
        return f"✅ Registrado ({self.microchip.strip()})"
    
    @property
    def tiene_microchip(self):
        """Retorna True si tiene microchip válido, False si no"""
        return bool(self.microchip and len(self.microchip.strip()) > 3)

    @property
    def clase_microchip_css(self):
        # El modelo decide si es verde o rojo según si tiene microchip
        if self.tiene_microchip:
            return "text-success"
        return "text-danger"
    
    @property
    def tiene_raza(self):
        if not self.race or not self.race.strip():
            return "⚠️ Sin Raza (Requiere registro)"
        return f"✅ Registrada ({self.race.strip()})"
    
    @property
    def clase_raza_css(self):
        # El modelo decide si es verde o rojo según si tiene raza
        if self.race and len(self.race.strip()) > 3:
            return "text-success"
        return "text-danger"