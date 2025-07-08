# config.py
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env al inicio
load_dotenv()

# --- CONFIGURACIONES GENERALES DE LA APLICACIÓN ---
ESPECIALIDADES = ["Medicina General", "Cardiología", "Pediatría", "Ginecología", "Dermatología", "Traumatología", "Oftalmología", "Otorrinolaringología", "Endocrinología", "Gastroenterología", "Neurología"]
SEGUROS = ["Ninguno", "Rimac", "Pacífico", "La Positiva", "Mapfre", "Sanitas", "Interseguro"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

# Información de la Clínica para la Boleta
CLINICA_INFO = {
    "nombre": "GesClínica S.A.C.",
    "ruc": "20123456789",
    "direccion": "Av. Principal 123, San Isidro, Lima, Perú",
    "telefono": "(01) 555-1234",
    "email": "contacto@gesclinica.com",
    "logo_path": "icons/logo.png"
}

# --- MÓDULO DE RECORDATORIOS POR VOZ ---
ENABLE_VOICE_REMINDERS = True

# --- LECTURA DE SECRETOS DESDE EL ENTORNO (.env) ---
# Clave de API para Google AI (Gemini)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Credenciales para Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_FLOW_SID = os.getenv("TWILIO_FLOW_SID")

# Verificación opcional para ayudar a depurar si faltan claves
if ENABLE_VOICE_REMINDERS and not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_FLOW_SID]):
    print("⚠️ ADVERTENCIA: Faltan una o más credenciales de Twilio en el archivo .env. El servicio de recordatorios podría fallar.")