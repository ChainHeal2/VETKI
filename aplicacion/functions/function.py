"""
Docstring for aplicacion.functions.function
"""
import re

def limpiar_datos(dato):
    """Limpia los datos para la BD"""
    lista_buena= []
    for fila in dato:
        tabla_limpia = {}
        for llave,valor in fila.items():
            if isinstance(valor, str):
                if len(valor) >= 1 and len(valor) <= 45:
                    valor_limpio = re.sub(r'\d+', '', valor.lower())
                    tabla_limpia[llave] = valor_limpio.strip().title()
                else:
                    print("una de las llaves es menor a la condicion")
            else:
                tabla_limpia[llave] = valor
        lista_buena.append(tabla_limpia)
    #print("datos salientes",type(lista_buena),lista_buena)
    return lista_buena
def limpiar_formulario(datos_dict):
    """Limpia un solo diccionario proveniente de un formulario"""
    print(datos_dict)
    fila_limpia = {}
    for llave, valor in datos_dict.items():
        if isinstance(valor, str):
            print(len(valor))
            if len(valor) > 3:
                valor_limpio = re.sub(r'\d+', '', valor.lower())
                fila_limpia[llave] = valor_limpio.strip().title()
            else:
                print("ok no es mayor pasa aca")
                print(fila_limpia)
                return fila_limpia
        else:
            fila_limpia[llave] = valor
    return fila_limpia