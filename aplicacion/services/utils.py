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
