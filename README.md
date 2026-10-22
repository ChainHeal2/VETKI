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

## Dictado por voz local

La grabación se captura en el navegador con `MediaRecorder`. Flask transcribe el audio
localmente con Vosk; no se necesita `OPENAI_API_KEY` ni se envía audio a una API externa.
En Debian instala FFmpeg y las dependencias de Python:

```bash
sudo apt install ffmpeg
pip install -r requirements.txt
```

Descarga una vez el modelo pequeño de español de Vosk desde su sitio oficial y extrae
la carpeta `vosk-model-small-es-0.42` dentro de `models/` en la raíz del proyecto:

```bash
mkdir -p models
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip -O /tmp/vosk-model-small-es-0.42.zip
unzip -q /tmp/vosk-model-small-es-0.42.zip -d models
```

La aplicación carga el modelo la primera vez que se solicita una transcripción. El
directorio `models/` está excluido de Git porque contiene archivos grandes.
