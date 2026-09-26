"""
Docstring for aplicacion.functions.function
"""
def prepara_datos(tabla):
    """Prepara los datos para la BD
    si los datos son vacios
    se rellenan de None para lograr un ingreso
    exitoso.
        ej: '' = None
    """
    tabla_limpia = {}
    for llave,valor in tabla.items():
        if valor.strip() == '':
            tabla_limpia[llave] = None
        else:
            tabla_limpia[llave] = valor
    return tabla_limpia
def limpiar_dato(valor):
    """
    Recibe un valor, quita espacios si es texto y lo devuelve.
    Si es None, devuelve None sin dar error.
    """
    if isinstance(valor, str):
        return valor.strip().title()
    return valor
