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
def get_payment_method_distribution(start_date, end_date): return database.obtener_distribucion_metodo_pago(start_date, end_date)
def get_insurance_usage_distribution(start_date, end_date): return database.obtener_distribucion_uso_seguro(start_date, end_date)
def get_total_revenue(start_date, end_date): return database.calcular_ingresos_totales(start_date, end_date)
def get_total_attended_appointments(start_date, end_date): return database.contar_citas_atendidas(start_date, end_date)

# --- NUEVA FUNCIÓN PARA BOLETAS ---
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