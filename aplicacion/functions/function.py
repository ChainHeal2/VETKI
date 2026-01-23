"""
Docstring for aplicacion.functions.function
"""
import re

def limpiar_datos(dato):
    """Limpia los datos para la BD"""
    print("lo que envia FLASK--------FLASK--------\n",dato)
    if dato:
        for dicc in dato:
            nombre_malo = dicc['name_species']
            if len(nombre_malo) > 5:
                nombre_bueno = nombre_malo.lower().strip()
                return nombre_bueno.title()
