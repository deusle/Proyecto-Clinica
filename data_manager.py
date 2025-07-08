# data_manager.py
import database
import ct_scan_analyzer # <-- NUEVA IMPORTACIÓN
import json # <-- NUEVA IMPORTACIÓN
from config import ADMIN_USER, ADMIN_PASS, GOOGLE_API_KEY
import google.generativeai as genai

# ... (Funciones existentes sin cambios) ...
def verify_credentials(username, password): return username == ADMIN_USER and password == ADMIN_PASS
def get_all_patients(filter_text=""): return database.obtener_pacientes(filter_text)
# ... etc ...

# --- NUEVAS FUNCIONES PARA EL MÓDULO DE LABORATORIO ---
def add_lab_test(paciente_id, tipo, fecha, resultados, archivo, ia_results_dict):
    ia_json = json.dumps(ia_results_dict) if ia_results_dict else None
    database.agregar_analisis_laboratorio(paciente_id, tipo, fecha, resultados, archivo, ia_json)

def get_lab_tests_for_patient(paciente_id):
    return database.obtener_analisis_por_paciente(paciente_id)

def delete_lab_test(analisis_id):
    database.eliminar_analisis(analisis_id)

def analyze_ct_scan_image(image_path):
    """Llama al módulo analizador y devuelve los resultados."""
    return ct_scan_analyzer.analyze_ct_scan(image_path)


# ... (El resto de funciones de data_manager.py se mantienen sin cambios) ...
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
    return database.obtener_historial_pagos()

def save_clinical_record(appointment_id, data):
    database.actualizar_consulta_clinica(appointment_id, *data)

def get_patient_clinical_history(patient_id):
    return database.obtener_historial_clinico_paciente(patient_id)

# --- Lógica de Pagos ---
def get_scheduled_appointments(filter_text=""): return database.obtener_citas_programadas(filter_text)
def register_payment(appointment_id, data): database.registrar_pago(appointment_id, *data)
def get_payment_history(): return database.obtener_historial_pagos()

# --- FUNCIONES PARA REPORTES BÁSICOS Y KPIS ---
def get_payment_method_distribution(start_date, end_date):
    return database.obtener_distribucion_metodo_pago(start_date, end_date)

def get_insurance_usage_distribution(start_date, end_date):
    return database.obtener_distribucion_uso_seguro(start_date, end_date)

def get_total_revenue(start_date, end_date):
    return database.calcular_ingresos_totales(start_date, end_date)

def get_total_attended_appointments(start_date, end_date):
    return database.contar_citas_atendidas(start_date, end_date)

# --- FUNCIONES PARA REPORTES AVANZADOS ---
def get_performance_by_specialty(start_date, end_date):
    return database.obtener_rendimiento_por_especialidad(start_date, end_date)

def get_appointments_per_day(start_date, end_date):
    return database.obtener_citas_por_dia(start_date, end_date)

def generate_report_summary_with_ai(start_date, end_date, kpis, specialty_data):
    """
    Genera un análisis de negocio sobre el reporte usando la IA de Google.
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "TU_CLAVE_API_AQUI":
        return "ERROR: La clave API de Google no ha sido configurada en el archivo config.py."

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        return f"ERROR: Fallo al configurar la API de Google. Verifica la clave. Detalles: {e}"

    # Construir el prompt para la IA
    prompt_parts = [
        "**Instrucciones para la IA:**",
        "Eres un analista de datos de negocio especializado en el sector salud. Analiza los siguientes KPIs y datos de un reporte de la clínica GesClínica y genera un informe en formato Markdown.",
        f"El período de análisis es del **{start_date}** al **{end_date}**.",
        "El informe debe contener las siguientes secciones:",
        "1.  **Resumen Ejecutivo:** Un párrafo de alto nivel que sintetice los resultados clave.",
        "2.  **Análisis de Desempeño:** Una evaluación más detallada de los KPIs y el rendimiento de las especialidades, destacando los puntos fuertes y las áreas de oportunidad.",
        "3.  **Recomendaciones Clave:** Una lista con 2-3 recomendaciones accionables basadas en los datos para mejorar la gestión de la clínica (ej. marketing, gestión de personal, optimización de precios, etc.).",
        "\n---\n",
        "**DATOS PARA EL ANÁLISIS:**\n",
        "**Indicadores Clave de Rendimiento (KPIs):**",
        f"- **Ingresos Totales:** S/ {kpis.get('revenue', 0):.2f}",
        f"- **Total de Citas Atendidas:** {kpis.get('appointments', 0)}\n",
        "**Rendimiento por Especialidad:**",
    ]

    if specialty_data:
        for item in specialty_data:
            prompt_parts.append(f"- **{item['especialidad']}:** {item['numero_citas']} citas generaron S/ {item['ingresos_totales']:.2f}")
    else:
        prompt_parts.append("- No hay datos de rendimiento por especialidad en este período.")

    prompt = "\n".join(prompt_parts)

    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: Ocurrió un problema al comunicarse con la IA. Detalles: {e}"