# VETKI
Dedicado a mi prometida con todo mi amor y a mis gatos con cariño, para convertirme en un programador.

## Migraciones de base de datos

VETKI usa PostgreSQL con las variables de conexión que ya utiliza la aplicación:
`FLASK_DATABASE_HOST`, `FLASK_DATABASE_PORT`, `FLASK_DATABASE_USER`,
`FLASK_DATABASE_PASSWORD` y `FLASK_DATABASE`.

Instala las dependencias del proyecto y usa Flask-Migrate para administrar los cambios:

```bash
pip install -r requirements.txt
```

Para una base de datos nueva, crea las tablas y vistas con:

```bash
flask --app index db upgrade
```

Si la base ya contiene el esquema `vetki`, primero verifica que corresponda al esquema
inicial del proyecto y registra esa versión sin volver a crear ni borrar tablas:

```bash
flask --app index db stamp head
```

Para modificar la estructura, actualiza los metadatos en `aplicacion/schema.py`,
genera una revisión, revisa el archivo generado y luego aplica la migración:

```bash
flask --app index db migrate -m "Describe el cambio"
flask --app index db upgrade
```

Las vistas PostgreSQL no se detectan automáticamente al generar revisiones; si una
vista cambia, agrega su actualización manualmente a la migración correspondiente.
