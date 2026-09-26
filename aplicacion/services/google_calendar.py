import os
import glob
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

class CalendarService:
    def __init__(self):
        self.creds = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        api_dir = os.path.abspath(os.path.join(current_dir, '..', '..','secrets'))
        self.token_path = os.path.join(api_dir,'token.json')
        
        # Auto-detectar la llave secreta que descargaste
        client_secrets = glob.glob(os.path.join(api_dir, 'client_secret_*.json'))
        self.credentials_path = client_secrets[0] if client_secrets else None

    def _authenticate(self):
        """Maneja la lógica de validación de OAuth localmente en el Servidor"""
        if not self.credentials_path:
            raise Exception("No se encontró ningún archivo de credenciales de Google OAuth (client_secret_*.json) en venv/api.")

        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # Si no hay credenciales válidas guardadas, o están vencidas, abrirá el flujo del navegador
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Token revocado o caducado detectado ({e}). Solicitando nuevo acceso...")
                    if os.path.exists(self.token_path):
                        os.remove(self.token_path)
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                    self.creds = flow.run_local_server(port=8080)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=8080)
            
            # Guardamos las credenciales para no tener que iniciar sesión todos los días
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

    def create_event(self, patient_name, appointment_date_str):
        """
        Crea un evento médico en tu Google Calendar y retorna confirmación.
        appointment_date_str: formato general YYYY-MM-DD
        """
        self._authenticate()
        service = build('calendar', 'v3', credentials=self.creds)

        # Parsear fecha de WTForm y establecer un horario base (10:00 AM) por ahora para el ejemplo
        if isinstance(appointment_date_str, datetime) or isinstance(appointment_date_str, type(datetime.today().date())):
            date_obj = appointment_date_str
        else:
            date_obj = datetime.strptime(str(appointment_date_str), '%Y-%m-%d')
            
        start_datetime = datetime(year=date_obj.year, month=date_obj.month, day=date_obj.day, hour=date_obj.hour, minute=date_obj.minute)
        end_datetime = start_datetime + timedelta(hours=1)

        event = {
          'summary': f'🐾 Cita Veterinaria: {patient_name.title()}',
          'location': 'VETKI Clínica Virtual',
          'description': f'Expediente clínico reservado desde la aplicación VETKI para el paciente {patient_name.title()}.',
          'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/Santiago', # Ajustado a un huso horario común latino (modifica a placer)
          },
          'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/Santiago',
          },
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'popup', 'minutes': 60}, # Alertar 1 hora antes en el móvil
            ],
          },
        }

        try:
            event_result = service.events().insert(calendarId='primary', body=event).execute()
            return event_result.get('id')
        except Exception as e:
            return None

    def update_event(self, event_id, patient_name, appointment_date_str):
            """
            Actualiza la fecha y hora de un evento existente en Google Calendar.
            event_id: El ID retornado por Google Calendar al momento de crearlo.
            appointment_date_str: Objeto datetime o string con la nueva fecha/hora.
            """
            if not event_id:
                return None

            self._authenticate()
            service = build('calendar', 'v3', credentials=self.creds)

            # Parsear la fecha recibida
            if isinstance(appointment_date_str, datetime):
                start_datetime = appointment_date_str
            elif isinstance(appointment_date_str, type(datetime.today().date())):
                date_obj = appointment_date_str
                start_datetime = datetime(year=date_obj.year, month=date_obj.month, day=date_obj.day, hour=10, minute=0, second=0)
            else:
                # Si viene como string 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM'
                try:
                    start_datetime = datetime.strptime(str(appointment_date_str), '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    date_obj = datetime.strptime(str(appointment_date_str), '%Y-%m-%d')
                    start_datetime = datetime(year=date_obj.year, month=date_obj.month, day=date_obj.day, hour=10, minute=0, second=0)

            end_datetime = start_datetime + timedelta(hours=1)

            event = {
            'summary': f'🐾 Cita Veterinaria: {patient_name.title()}',
            'location': 'VETKI Clínica Virtual',
            'description': f'Expediente clínico REPROGRAMADO desde la aplicación VETKI para el paciente {patient_name.title()}.',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'popup', 'minutes': 60},
                ],
            },
            }

            try:
                # Usamos patch() para actualizar el evento existente mediante su event_id
                event_result = service.events().patch(calendarId='primary', eventId=event_id, body=event).execute()
                return event_result.get('id')
            except Exception as e:
                return None