"""Función para limpiar datos de formulario"""
def sanitizar(datos_dict):
    """
    Limpia strings (lower + strip) y convierte vacíos a None.
    Mantiene intactos objetos tipo fecha, enteros, etc.
    """
    resultado = {}
    for clave, valor in datos_dict.items(): #Pedimos que nos devuelva (llave,valor:si pertenece a ser un tipo STR aplicamos strip y lower, si no es str lo dejamos intacto)
        if isinstance(valor, str):
            valor_limpio = valor.strip().lower()
            resultado[clave] = valor_limpio if valor_limpio != "" else None
        else:
            resultado[clave] = valor
    return resultado


#datos ={'pet_species_name': 'canina', 'pet_names': 'fdasfds', 'pet_race': 'RAZA', 'pet_datebirth': None, 'pet_microchip': None, 'pet_gender': None, 'pet_color': '1312af', 'pet_rstatus': None, 'pet_tutor_name': '12312', 'pet_tutor_address': None, 'pet_tutor_phone': None, 'submit': True, 'csrf_token': 'ImJiYzk0ZWRjNzU3ZDE2MThlNTVmYjAwY2ZjMGU4ODNjNzk5MWJkOGQi.aphlvw.XkpN414bY-0Rb8GSRZPB4goMhvM'}
#print(sanitizar(datos))

