# seed_database.py
import sqlite3
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Importar configuraciones desde tu proyecto
from config import ESPECIALIDADES, DIAS_SEMANA, SEGUROS
import database

# --- CONFIGURACIÓN ---
DB_FILE = "clinica.db"
NUM_PACIENTES = 25
NUM_CITAS_RECIENTES = 40 # Citas en los últimos 2 meses para la demo
NUM_CITAS_HISTORIAL = 80 # Citas más antiguas para construir el historial

# Inicializar Faker para generar datos en español
fake = Faker('es_ES')

# --- LISTAS DE DATOS FICTICIOS PARA REALISMO ---
MOTIVOS_CONSULTA = [
    "Control anual de rutina", "Dolor de cabeza persistente", "Fiebre y malestar general", "Revisión de resultados de laboratorio",
    "Consulta por tos y congestión", "Dolor abdominal agudo", "Seguimiento de hipertensión", "Reacción alérgica en la piel",
    "Lesión deportiva en la rodilla", "Consulta pediátrica de niño sano", "Control de embarazo", "Revisión de lunar sospechoso",
    "Ardor al orinar", "Problemas de visión"
]

DIAGNOSTICOS = [
    "Hipertensión arterial esencial (primaria)", "Diabetes mellitus tipo 2", "Gripe común", "Faringitis aguda",
    "Migraña sin aura", "Trastorno de ansiedad generalizada", "Infección del tracto urinario", "Dermatitis de contacto",
    "Esguince de tobillo", "Paciente sano", "Embarazo de bajo riesgo", "Nevo displásico", "Otitis media", "Reflujo gastroesofágico"
]

TRATAMIENTOS = [
    "Se prescribe Losartán 50mg cada 24h. Control en 1 mes.", "Se indica Metformina 850mg después del desayuno. Dieta y ejercicio.",
    "Reposo, hidratación y Paracetamol 500mg cada 8h si hay fiebre.", "Amoxicilina 500mg cada 8h por 7 días.",
    "Se recomienda evitar detonantes. Ibuprofeno 400mg en caso de dolor.", "Se deriva a psicología. Se prescribe Sertralina 50mg/día.",
    "Ciprofloxacino 500mg cada 12h por 5 días.", "Crema con hidrocortisona al 1% dos veces al día.",
    "Reposo, hielo, compresión y elevación (RICE). Fisioterapia.", "Continuar con controles periódicos. No se requiere tratamiento.",
    "Ácido fólico y control prenatal mensual.", "Se recomienda extirpación y biopsia del nevo.", "Gotas óticas con antibiótico.",
    "Omeprazol 20mg en ayunas. Evitar comidas irritantes."
]


def conectar_db():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def limpiar_base_de_datos(cursor):
    print("[INFO] Limpiando la base de datos existente...")
    # El orden es importante para no violar las claves foráneas
    cursor.execute("DELETE FROM analisis_laboratorio;")
    cursor.execute("DELETE FROM citas;")
    cursor.execute("DELETE FROM horarios_medicos;")
    cursor.execute("DELETE FROM pacientes;")
    cursor.execute("DELETE FROM medicos;")
    print("[OK] Base de datos limpia.")

def crear_medicos(cursor):
    print("[INFO] Creando medicos y sus horarios...")
    medico_ids = []
    for especialidad in ESPECIALIDADES:
        for _ in range(3):  # 3 médicos por especialidad
            nombre = fake.name()
            telefono = fake.phone_number()
            cursor.execute("INSERT INTO medicos (nombre_completo, especialidad, telefono) VALUES (?, ?, ?)",
                           (nombre, especialidad, telefono))
            medico_id = cursor.lastrowid
            medico_ids.append(medico_id)

            # Generar horarios aleatorios
            for dia_idx, _ in enumerate(DIAS_SEMANA):
                if random.random() < 0.7:  # 70% de probabilidad de trabajar un día
                    hora_inicio = random.randint(8, 10)
                    hora_fin = random.randint(16, 19)
                    if hora_fin <= hora_inicio: hora_fin = hora_inicio + 4

                    cursor.execute("INSERT INTO horarios_medicos (medico_id, dia_semana, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)",
                                   (medico_id, dia_idx, f"{hora_inicio:02d}:00", f"{hora_fin:02d}:00"))
    print(f"[OK] Creados {len(medico_ids)} medicos.")
    return medico_ids

def crear_pacientes(cursor):
    print("[INFO] Creando pacientes...")
    paciente_ids = []
    for _ in range(NUM_PACIENTES):
        dni = fake.unique.numerify(text='########')
        nombre = fake.first_name()
        apellidos = fake.last_name()
        
        # Generar fecha de nacimiento para tener una edad promedio de 30
        hoy = datetime.now()
        año_nacimiento = hoy.year - random.randint(18, 55) # Edades entre 18 y 55
        fecha_nac = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d")

        genero = random.choice(["Masculino", "Femenino"])
        telefono = fake.phone_number()
        email = fake.email()
        historial = fake.sentence(nb_words=10)

        cursor.execute("INSERT INTO pacientes (dni, nombre, apellidos, fecha_nac, genero, telefono, email, historial_basico) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (dni, nombre, apellidos, fecha_nac, genero, telefono, email, historial))
        paciente_ids.append(cursor.lastrowid)
    print(f"[OK] Creados {len(paciente_ids)} pacientes.")
    return paciente_ids

def crear_citas_y_historial(cursor, medico_ids, paciente_ids):
    print("[INFO] Creando historial clinico y citas...")
    
    # 1. Crear citas antiguas para formar el historial clínico de los pacientes
    for i in range(NUM_CITAS_HISTORIAL):
        paciente_id = random.choice(paciente_ids)
        medico_id = random.choice(medico_ids)
        
        # Fechas entre 1 año y 2 meses atrás
        fecha_cita = datetime.now() - timedelta(days=random.randint(61, 365))
        fecha_hora_str = fecha_cita.strftime("%Y-%m-%d %H:%M:%S")
        
        # Todas las citas del historial están pagadas y completadas
        estado = 'Pagada'
        monto = round(random.uniform(70.0, 120.0), 2)
        metodo_pago = random.choice(["Efectivo", "Tarjeta de Crédito", "Transferencia"])
        aseguradora = random.choice(SEGUROS) if random.random() < 0.7 else "Ninguno"
        
        # Datos clínicos
        motivo = random.choice(MOTIVOS_CONSULTA)
        temperatura = round(random.uniform(36.5, 38.0), 1)
        presion = f"{random.randint(110, 140)}/{random.randint(70, 90)}"
        frec_cardiaca = random.randint(60, 100)
        saturacion = random.randint(95, 99)
        sintomas = fake.sentence(nb_words=15)
        diagnostico = random.choice(DIAGNOSTICOS)
        tratamiento = random.choice(TRATAMIENTOS)
        
        cursor.execute("""
            INSERT INTO citas (paciente_id, medico_id, fecha_hora, estado, monto_pagado, metodo_pago, aseguradora,
                               motivo_consulta, temperatura, presion_arterial, frecuencia_cardiaca, saturacion_oxigeno,
                               sintomas, diagnostico, tratamiento, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (paciente_id, medico_id, fecha_hora_str, estado, monto, metodo_pago, aseguradora,
              motivo, temperatura, presion, frec_cardiaca, saturacion, sintomas, diagnostico, tratamiento, "Notas de prueba."))

    # 2. Crear citas recientes para la demo (últimos 2 meses)
    for i in range(NUM_CITAS_RECIENTES):
        paciente_id = random.choice(paciente_ids)
        medico_id = random.choice(medico_ids)
        
        # Fechas desde hace 60 días hasta en 15 días en el futuro
        fecha_cita = datetime.now() - timedelta(days=random.randint(-15, 60))
        fecha_hora_str = fecha_cita.strftime("%Y-%m-%d %H:%M:%S")
        
        estado = random.choices(["Pagada", "Programada", "Cancelada"], weights=[0.6, 0.3, 0.1], k=1)[0]
        
        if estado == 'Pagada':
            monto = round(random.uniform(70.0, 120.0), 2)
            metodo_pago = random.choice(["Efectivo", "Tarjeta de Crédito", "Yape/Plin"])
            aseguradora = random.choice(SEGUROS) if random.random() < 0.7 else "Ninguno"
            # Dejar algunos datos clínicos en blanco para demo
            diagnostico = random.choice(DIAGNOSTICOS) if random.random() < 0.5 else None
            tratamiento = random.choice(TRATAMIENTOS) if diagnostico else None
            cursor.execute("""
                INSERT INTO citas (paciente_id, medico_id, fecha_hora, estado, monto_pagado, metodo_pago, aseguradora, diagnostico, tratamiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (paciente_id, medico_id, fecha_hora_str, estado, monto, metodo_pago, aseguradora, diagnostico, tratamiento))
        else: # Programada o Cancelada
            cursor.execute("""
                INSERT INTO citas (paciente_id, medico_id, fecha_hora, estado)
                VALUES (?, ?, ?, ?)
            """, (paciente_id, medico_id, fecha_hora_str, estado))

    print(f"[OK] Creadas {NUM_CITAS_HISTORIAL + NUM_CITAS_RECIENTES} citas en total.")


def seed_database():
    """Función principal para poblar la base de datos."""
    # Primero, asegúrate de que las tablas existan
    print("[INFO] Verificando y creando tablas si es necesario...")
    database.crear_tablas()
    print("[OK] Tablas verificadas.")

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        limpiar_base_de_datos(cursor)
        medico_ids = crear_medicos(cursor)
        paciente_ids = crear_pacientes(cursor)
        crear_citas_y_historial(cursor, medico_ids, paciente_ids)

        conn.commit()
        print("\n¡EXITO! La base de datos ha sido poblada con exito.")
        print("Ahora puedes ejecutar 'python main.py' para ver los datos de demostracion.")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Ocurrio un error: {e}")
        print("[INFO] Se ha deshecho la transaccion. La base de datos no fue modificada.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()