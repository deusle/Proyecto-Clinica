# data_manager.py
import database
from config import ADMIN_USER, ADMIN_PASS

# ... (todas las funciones existentes se mantienen) ...
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
def get_all_detailed_appointments(): return database.obtener_citas_detalladas()
def create_appointment(data): database.agregar_cita(*data)
def delete_appointment(appointment_id): database.eliminar_cita(appointment_id)
def get_appointments_by_doctor_and_day(doctor_id, date_str): return database.obtener_citas_por_medico_y_dia(doctor_id, date_str)
def get_appointment_by_id(appointment_id): return database.obtener_cita_completa_por_id(appointment_id)
def get_paid_appointments_for_clinical_record(filter_text=""): return database.obtener_historial_pagos()
def save_clinical_record(appointment_id, data): database.actualizar_consulta_clinica(appointment_id, *data)
def get_patient_clinical_history(patient_id): return database.obtener_historial_clinico_paciente(patient_id)
def get_scheduled_appointments(filter_text=""): return database.obtener_citas_programadas(filter_text)
def register_payment(appointment_id, data): database.registrar_pago(appointment_id, *data)
def get_payment_history(): return database.obtener_historial_pagos()

# --- FUNCIONES PARA REPORTES ---
def get_payment_method_distribution(start_date, end_date):
    """Obtiene la distribución de métodos de pago para el gráfico."""
    return database.obtener_distribucion_metodo_pago(start_date, end_date)

def get_insurance_usage_distribution(start_date, end_date):
    """Obtiene la distribución de uso de seguros para el gráfico."""
    return database.obtener_distribucion_uso_seguro(start_date, end_date)

# NUEVAS FUNCIONES PARA KPIs
def get_total_revenue(start_date, end_date):
    """Calcula los ingresos totales en un rango de fechas."""
    return database.calcular_ingresos_totales(start_date, end_date)

def get_total_attended_appointments(start_date, end_date):
    """Cuenta las citas atendidas (pagadas) en un rango de fechas."""
    return database.contar_citas_atendidas(start_date, end_date)