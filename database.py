import sqlite3
import os

DB_FILE = "clinica.db"

def conectar_db():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), DB_FILE))
    conn.row_factory = sqlite3.Row 
    return conn

def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()

    # CAMBIO: Añadida columna 'telefono'
    sql_medicos = """
    CREATE TABLE IF NOT EXISTS medicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        especialidad TEXT NOT NULL,
        telefono TEXT
    );
    """
    sql_horarios = """
    CREATE TABLE IF NOT EXISTS horarios_medicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, medico_id INTEGER NOT NULL,
        dia_semana INTEGER NOT NULL, hora_inicio TEXT NOT NULL, hora_fin TEXT NOT NULL,
        FOREIGN KEY (medico_id) REFERENCES medicos (id)
    );
    """
    sql_pacientes = """
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, dni TEXT NOT NULL UNIQUE, 
        nombre TEXT NOT NULL, apellidos TEXT NOT NULL, fecha_nac TEXT, 
        genero TEXT, telefono TEXT, email TEXT, historial_basico TEXT
    );
    """
    # CAMBIO: Reestructurado el sistema de pago
    sql_citas = """
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_id INTEGER NOT NULL, medico_id INTEGER NOT NULL,
        fecha_hora TEXT NOT NULL, estado TEXT NOT NULL, metodo_pago TEXT,
        tiene_seguro TEXT, aseguradora TEXT, sintomas TEXT, diagnostico TEXT, 
        tratamiento TEXT, notas TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
        FOREIGN KEY (medico_id) REFERENCES medicos (id)
    );
    """
    
    cursor.execute(sql_pacientes); cursor.execute(sql_medicos)
    cursor.execute(sql_horarios); cursor.execute(sql_citas)
    conn.commit(); conn.close()

# --- Funciones de Médicos y Horarios (con teléfono) ---

def agregar_medico(nombre, especialidad, telefono, horarios):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medicos (nombre_completo, especialidad, telefono) VALUES (?, ?, ?)", (nombre, especialidad, telefono))
    medico_id = cursor.lastrowid
    for dia, horas in horarios.items():
        if horas: cursor.execute("INSERT INTO horarios_medicos (medico_id, dia_semana, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (medico_id, dia, horas['inicio'], horas['fin']))
    conn.commit(); conn.close()

def actualizar_medico(medico_id, nombre, especialidad, telefono, horarios):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE medicos SET nombre_completo = ?, especialidad = ?, telefono = ? WHERE id = ?", (nombre, especialidad, telefono, medico_id))
    cursor.execute("DELETE FROM horarios_medicos WHERE medico_id = ?", (medico_id,))
    for dia, horas in horarios.items():
        if horas: cursor.execute("INSERT INTO horarios_medicos (medico_id, dia_semana, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (medico_id, dia, horas['inicio'], horas['fin']))
    conn.commit(); conn.close()

def obtener_medicos(filtro=""):
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT id, nombre_completo, especialidad, telefono FROM medicos" # CAMBIO: añadido telefono
    if filtro: query += " WHERE nombre_completo LIKE ? OR especialidad LIKE ?"
    cursor.execute(query, (f'%{filtro}%', f'%{filtro}%')) if filtro else cursor.execute(query)
    medicos = cursor.fetchall(); conn.close()
    return medicos

# --- Funciones de Citas/Consultas (con nuevo sistema de pago) ---

def agregar_cita(datos):
    conn = conectar_db()
    cursor = conn.cursor()
    # CAMBIO: Actualizados los campos a insertar
    cursor.execute("""
        INSERT INTO citas (paciente_id, medico_id, fecha_hora, estado, metodo_pago, tiene_seguro, aseguradora, sintomas, diagnostico, tratamiento, notas)
        VALUES (?, ?, ?, 'Programada', ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit(); conn.close()

def actualizar_consulta(cita_id, datos):
    conn = conectar_db()
    cursor = conn.cursor()
    # CAMBIO: Actualizados los campos a modificar
    query = """
    UPDATE citas SET paciente_id = ?, medico_id = ?, fecha_hora = ?, metodo_pago = ?, 
                   tiene_seguro = ?, aseguradora = ?, sintomas = ?, diagnostico = ?, 
                   tratamiento = ?, notas = ? 
    WHERE id = ?
    """
    cursor.execute(query, datos + (cita_id,)); conn.commit(); conn.close()

def obtener_citas_detalladas():
    conn = conectar_db()
    cursor = conn.cursor()
    # CAMBIO: Seleccionamos los nuevos campos de pago
    query = """
    SELECT c.id, p.nombre || ' ' || p.apellidos, m.nombre_completo, m.especialidad,
           c.fecha_hora, c.estado, c.metodo_pago, c.tiene_seguro, c.aseguradora
    FROM citas c JOIN pacientes p ON c.paciente_id = p.id JOIN medicos m ON c.medico_id = m.id
    ORDER BY c.fecha_hora DESC
    """
    cursor.execute(query); citas = cursor.fetchall(); conn.close()
    return citas

# --- El resto de funciones no necesitan cambios ---
# (Se incluyen por completitud)
def obtener_horarios_por_medico(medico_id):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("SELECT dia_semana, hora_inicio, hora_fin FROM horarios_medicos WHERE medico_id = ?", (medico_id,))
    horarios_dict = {row['dia_semana']: {'inicio': row['hora_inicio'], 'fin': row['hora_fin']} for row in cursor.fetchall()}
    conn.close(); return horarios_dict
def obtener_citas_por_medico_y_dia(medico_id, fecha):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("SELECT fecha_hora FROM citas WHERE medico_id = ? AND date(fecha_hora) = ?", (medico_id, fecha))
    citas = [c['fecha_hora'] for c in cursor.fetchall()]; conn.close(); return citas
def agregar_paciente(dni, nombre, apellidos, fecha_nac, genero, telefono, email, historial):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("INSERT INTO pacientes (dni, nombre, apellidos, fecha_nac, genero, telefono, email, historial_basico) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (dni, nombre, apellidos, fecha_nac, genero, telefono, email, historial))
    conn.commit(); conn.close()
def obtener_pacientes(filtro=""):
    conn = conectar_db(); cursor = conn.cursor()
    query = "SELECT * FROM pacientes"; 
    if filtro: query += " WHERE nombre LIKE ? OR apellidos LIKE ? OR dni LIKE ?"
    cursor.execute(query, (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%')) if filtro else cursor.execute(query)
    pacientes = cursor.fetchall(); conn.close(); return pacientes
def obtener_paciente_por_id(paciente_id):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone(); conn.close(); return paciente
def actualizar_paciente(paciente_id, dni, nombre, apellidos, fecha_nac, genero, telefono, email, historial):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("UPDATE pacientes SET dni = ?, nombre = ?, apellidos = ?, fecha_nac = ?, genero = ?, telefono = ?, email = ?, historial_basico = ? WHERE id = ?", (dni, nombre, apellidos, fecha_nac, genero, telefono, email, historial, paciente_id))
    conn.commit(); conn.close()
def obtener_medico_por_id(medico_id):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicos WHERE id = ?", (medico_id,)); medico = cursor.fetchone(); conn.close(); return medico
def obtener_medicos_por_especialidad(especialidad):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_completo FROM medicos WHERE especialidad = ?", (especialidad,)); medicos = cursor.fetchall(); conn.close(); return medicos
def obtener_cita_completa_por_id(cita_id):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas WHERE id = ?", (cita_id,)); cita = cursor.fetchone(); conn.close(); return cita
def actualizar_estado_cita(cita_id, nuevo_estado):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute("UPDATE citas SET estado = ? WHERE id = ?", (nuevo_estado, cita_id)); conn.commit(); conn.close()