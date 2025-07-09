# data_manager.py
import database
import ct_scan_analyzer
import json
from datetime import datetime
from config import ADMIN_USER, ADMIN_PASS, GOOGLE_API_KEY
import google.generativeai as genai

# --- Lógica de Autenticación y General ---
def verify_credentials(username, password): 
    return username == ADMIN_USER and password == ADMIN_PASS

# --- Lógica de Pacientes ---
def get_all_patients(filter_text=""): return database.obtener_pacientes(filter_text)
def add_patient(data): database.agregar_paciente(*data)
def get_patient_by_id(patient_id): return database.obtener_paciente_por_id(patient_id)
def update_patient(patient_id, data): database.actualizar_paciente(patient_id, *data)

# --- Lógica de Médicos ---
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
def save_clinical_record(appointment_id, data):
    database.actualizar_consulta_clinica(appointment_id, *data)

def get_patient_clinical_history(patient_id):
    return database.obtener_historial_clinico_paciente(patient_id)

# --- Lógica de Pagos y Boletas ---
def get_scheduled_appointments(filter_text=""): return database.obtener_citas_programadas(filter_text)
def register_payment(appointment_id, data): database.registrar_pago(appointment_id, *data)
def get_payment_history(): return database.obtener_historial_pagos()

def get_invoice_details(cita_id):
    """Recopila todos los datos de una cita para generar la boleta."""
    cita_data = database.obtener_cita_completa_por_id(cita_id)
    if not cita_data:
        return None
    
    paciente_data = database.obtener_paciente_por_id(cita_data['paciente_id'])
    medico_data = database.obtener_medico_por_id(cita_data['medico_id'])
    
    invoice_info = {
        "id": cita_data['id'],
        "paciente_nombre": f"{paciente_data['nombre']} {paciente_data['apellidos']}",
        "paciente_dni": paciente_data['dni'],
        "medico_nombre": medico_data['nombre_completo'],
        "medico_especialidad": medico_data['especialidad'],
        "monto_pagado": cita_data['monto_pagado']
    }
    return invoice_info

# --- Lógica para el Módulo de Laboratorio ---
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

# --- Lógica de Reportes ---
def get_payment_method_distribution(start_date, end_date): return database.obtener_distribucion_metodo_pago(start_date, end_date)
def get_insurance_usage_distribution(start_date, end_date): return database.obtener_distribucion_uso_seguro(start_date, end_date)
def get_total_revenue(start_date, end_date): return database.calcular_ingresos_totales(start_date, end_date)
def get_total_attended_appointments(start_date, end_date): return database.contar_citas_atendidas(start_date, end_date)
def get_performance_by_specialty(start_date, end_date): return database.obtener_rendimiento_por_especialidad(start_date, end_date)
def get_appointments_per_day(start_date, end_date): return database.obtener_citas_por_dia(start_date, end_date)

# --- Funciones de IA ---

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
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: Ocurrió un problema al comunicarse con la IA. Detalles: {e}"

# MODIFICADO: Añadida la fecha actual al prompt de la IA
def generate_clinical_summary_with_ai(patient_id):
    """
    Genera un resumen del historial clínico de un paciente usando la IA de Google.
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "TU_CLAVE_API_AQUI":
        return "ERROR: La clave API de Google no ha sido configurada en el archivo config.py."

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        return f"ERROR: Fallo al configurar la API de Google. Verifica la clave. Detalles: {e}"

    historial = get_patient_clinical_history(patient_id)
    if not historial:
        return "El paciente no tiene un historial clínico registrado para generar un resumen."
    
    # NUEVO: Obtener la fecha actual para dar contexto a la IA
    fecha_actual = datetime.now().strftime("%d de %B de %Y")

    # Construir el prompt para la IA
    prompt_parts = [
        "**Instrucciones para la IA:**",
        "Eres un asistente médico inteligente. A partir del siguiente historial clínico de un paciente, genera un resumen conciso en formato Markdown. El resumen debe ser claro y fácil de entender para un profesional de la salud.",
        # NUEVO: Instrucción con la fecha actual
        f"La fecha actual es **{fecha_actual}**. Utiliza esta fecha como referencia para contextualizar los eventos en el tiempo (por ejemplo, 'la última consulta fue hace 3 meses', 'diagnosticado hace 2 años').",
        "El resumen debe incluir las siguientes secciones:",
        "1. **Resumen General del Paciente:** Un párrafo breve que describa las condiciones y diagnósticos más relevantes o recurrentes.",
        "2. **Línea de Tiempo de Consultas Clave:** Una lista cronológica de los eventos médicos más importantes (diagnósticos significativos, cambios de tratamiento, etc.), indicando cuánto tiempo ha pasado desde la fecha actual.",
        "3. **Alertas o Puntos de Atención:** Destaca cualquier patrón, contradicción o dato que pueda requerir atención especial en futuras consultas (ej. alergias, mediciones vitales anómalas recurrentes, etc.).",
        "\n---\n",
        "**HISTORIAL CLÍNICO DEL PACIENTE PARA ANÁLISIS:**\n",
    ]

    for consulta in historial:
        consulta_details = [
            f"**Fecha:** {consulta['fecha_hora']}",
            f"**Médico:** {consulta['nombre_completo']} ({consulta['especialidad']})",
            f"**Motivo de Consulta:** {consulta['motivo_consulta'] or 'No especificado'}",
            "**Signos Vitales:**"
            f"  - Temperatura: {str(consulta['temperatura']) + ' °C' if consulta['temperatura'] else 'N/A'}",
            f"  - Presión Arterial: {consulta['presion_arterial'] or 'N/A'}",
            f"  - Frec. Cardíaca: {str(consulta['frecuencia_cardiaca']) + ' lpm' if consulta['frecuencia_cardiaca'] else 'N/A'}",
            f"  - Saturación O2: {str(consulta['saturacion_oxigeno']) + ' %' if consulta['saturacion_oxigeno'] else 'N/A'}",
            f"**Síntomas Subjetivos:** {consulta['sintomas'] or 'No detallados'}",
            f"**Diagnóstico:** {consulta['diagnostico'] or 'No detallado'}",
            f"**Tratamiento:** {consulta['tratamiento'] or 'No detallado'}",
            "---"
        ]
        prompt_parts.append("\n".join(consulta_details))

    prompt = "\n".join(prompt_parts)

    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: Ocurrió un problema al comunicarse con la IA. Detalles: {e}"