# data_manager.py
import database
from config import ADMIN_USER, ADMIN_PASS

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

# --- Lógica de Citas Simplificada ---
def get_all_detailed_appointments(): return database.obtener_citas_detalladas()
def create_appointment(data): database.agregar_cita(*data)
def delete_appointment(appointment_id): database.eliminar_cita(appointment_id) # NUEVO
def get_appointments_by_doctor_and_day(doctor_id, date_str): return database.obtener_citas_por_medico_y_dia(doctor_id, date_str)

# --- Lógica de Pagos ---
def get_scheduled_appointments(filter_text=""): return database.obtener_citas_programadas(filter_text)
def register_payment(appointment_id, data): database.registrar_pago(appointment_id, *data)
def get_payment_history(): return database.obtener_historial_pagos() # NUEVO

# --- Lógica de Recetas ---
def create_prescription(paciente_id, medico_id, fecha, contenido):
    database.agregar_receta(paciente_id, medico_id, fecha, contenido)

def get_prescriptions_by_patient(paciente_id):
    return database.obtener_recetas_por_paciente(paciente_id)

def get_all_prescriptions():
    return database.obtener_todas_las_recetas()

def get_all_pacientes():
    return database.obtener_pacientes()

def get_all_medicos():
    return database.obtener_medicos()
