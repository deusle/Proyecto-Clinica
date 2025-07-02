# data_manager.py
import database
from config import ADMIN_USER, ADMIN_PASS, GOOGLE_API_KEY
import google.generativeai as genai

def verify_credentials(username, password): return username == ADMIN_USER and password == ADMIN_PASS
def get_all_patients(filter_text=""): return database.obtener_pacientes(filter_text)
def add_patient(data): database.agregar_paciente(*data)
def get_patient_by_id(patient_id): return database.obtener_paciente_por_id(patient_id)
def update_patient(patient_id, data): database.actualizar_paciente(patient_id, *data)
def get_all_doctors(filter_text=""): return database.obtener_medicos(filter_text)
def add_doctor(data): database.agregar_medico(*data)
def get_doctor_by_id(doctor_id): return database.obtener_medico_por_id(doctor_id)
def update_doctor(doctor_id, data): database.actualizar_medico(doctor_id, *data)
def get_doctors_by_specialty(specialty): return database.obtener_medicos_por_especialidad(specialty)
def get_doctor_schedules(doctor_id): return database.obtener_horarios_por_medico(doctor_id)

# --- Lógica de Citas ---
def get_all_detailed_appointments(): return database.obtener_citas_detalladas()
def create_appointment(data): database.agregar_cita(*data)
def delete_appointment(appointment_id): database.eliminar_cita(appointment_id)
def get_appointments_by_doctor_and_day(doctor_id, date_str): return database.obtener_citas_por_medico_y_dia(doctor_id, date_str)
def get_appointment_by_id(appointment_id): return database.obtener_cita_completa_por_id(appointment_id)

# --- Lógica de Historial Clínico ---
def get_paid_appointments_for_clinical_record(filter_text=""):
    # Esta función podría ser más compleja, por ahora reutilizamos la de pagos
    # pero buscando por estado 'Pagada'
    # En un futuro, podrías crear una función específica en database.py
    # que busque citas 'Pagada' sin registro clínico.
    all_payments = database.obtener_historial_pagos() # Usaremos esta, pero idealmente sería una nueva
    return all_payments

def save_clinical_record(appointment_id, data):
    database.actualizar_consulta_clinica(appointment_id, *data)

def get_patient_clinical_history(patient_id):
    return database.obtener_historial_clinico_paciente(patient_id)

# --- Lógica de Pagos ---
def get_scheduled_appointments(filter_text=""): return database.obtener_citas_programadas(filter_text)
def register_payment(appointment_id, data): database.registrar_pago(appointment_id, *data)
def get_payment_history(): return database.obtener_historial_pagos()

# --- NUEVA FUNCIÓN CON INTELIGENCIA ARTIFICIAL ---
def generate_clinical_summary_with_ai(patient_id):
    """
    Genera un resumen clínico y puntos clave usando la IA de Google.
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "CLAVE_API_AQUI":
        return "ERROR: La clave API de Google no ha sido configurada en el archivo config.py."

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        return f"ERROR: Fallo al configurar la API de Google. Verifica la clave. Detalles: {e}"

    paciente = get_patient_by_id(patient_id)
    historial = get_patient_clinical_history(patient_id)

    if not paciente:
        return "ERROR: No se encontró al paciente."
    if not historial:
        return "INFORME: El paciente no tiene un historial clínico registrado para analizar."

    # Construir el prompt para la IA
    prompt_parts = [
        "**Instrucciones para la IA:**",
        "Eres un asistente médico experto. Analiza el siguiente historial clínico de un paciente y genera un informe conciso para el médico tratante. El informe debe estar en formato Markdown y estructurado de la siguiente manera:",
        "1.  **Resumen General del Paciente:** Un párrafo que sintetice el estado de salud general, condiciones preexistentes y cualquier dato demográfico relevante.",
        "2.  **Puntos Clave del Historial:** Una lista de viñetas (bullet points) que resalten los diagnósticos más importantes, tratamientos recurrentes, alergias conocidas o condiciones crónicas significativas.",
        "3.  **Posibles Alertas o Seguimientos:** Una breve sección que sugiera posibles áreas de atención futura o seguimientos recomendados basados en el historial.",
        "\n---\n",
        "**DATOS DEL PACIENTE:**",
        f"- **Nombre:** {paciente['nombre']} {paciente['apellidos']}",
        f"- **Fecha de Nacimiento:** {paciente['fecha_nac']}",
        f"- **Género:** {paciente['genero']}",
        f"- **Historial Básico / Alergias:** {paciente['historial_basico'] or 'No especificado'}",
        "\n---\n",
        "**HISTORIAL DE CONSULTAS (de más reciente a más antigua):**\n"
    ]

    for consulta in historial:
        consulta_details = [
            f"**Fecha:** {consulta['fecha_hora']}",
            f"**Médico:** {consulta['nombre_completo']} ({consulta['especialidad']})",
            f"**Síntomas:** {consulta['sintomas'] or 'No detallados'}",
            f"**Diagnóstico:** {consulta['diagnostico'] or 'No detallado'}",
            f"**Tratamiento:** {consulta['tratamiento'] or 'No detallado'}",
            "---"
        ]
        prompt_parts.append("\n".join(consulta_details))

    prompt = "\n".join(prompt_parts)

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: Ocurrió un problema al comunicarse con la IA. Detalles: {e}"