import sys
from datetime import datetime, time, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QDialog, QFormLayout, QDateEdit, QComboBox, QTextEdit,
    QTabWidget, QHeaderView, QDialogButtonBox, QDateTimeEdit, QRadioButton,
    QCheckBox, QTimeEdit, QCalendarWidget, QGroupBox, QGridLayout, QFrame
)
from PySide6.QtCore import QDate, QTime, Qt, QSize, QDateTime
from PySide6.QtGui import QColor, QTextCharFormat, QBrush, QIcon, QPixmap, QFont
import database

# --- ESTILOS GLOBALES (QSS) ---
GLOBAL_STYLESHEET = """
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #333;
}
QMainWindow, QDialog {
    background-color: #f0f8ff; /* AliceBlue, un fondo suave */
}
/* Estilo para los botones principales */
QPushButton {
    background-color: #007acc;
    color: white;
    font-weight: bold;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #005c99;
}
QPushButton:pressed {
    background-color: #004c80;
}
/* Botones de Aceptar/Cancelar en diálogos */
QDialogButtonBox QPushButton {
    padding: 8px 20px;
}
/* Estilo para campos de entrada */
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit, QDateTimeEdit {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: white;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1px solid #007acc;
}
/* Estilo para las tablas */
QTableWidget {
    border: 1px solid #ddd;
    gridline-color: #e0e0e0;
    background-color: white;
    alternate-background-color: #f7fbff;
    selection-background-color: #b3d9ff;
    selection-color: #333;
}
QHeaderView::section {
    background-color: #e0eaf1;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #007acc;
    font-weight: bold;
}
/* Estilo para los GroupBox */
QGroupBox {
    font-weight: bold;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    background-color: #f0f8ff;
}
/* Estilo para el Calendario */
QCalendarWidget QToolButton {
    color: white;
    background-color: #007acc;
    font-size: 14px;
}
QCalendarWidget QAbstractItemView {
    selection-background-color: #007acc;
}
"""

# --- Listas Fijas y Credenciales ---
ESPECIALIDADES = ["Medicina General", "Cardiología", "Pediatría", "Ginecología", "Dermatología", "Traumatología", "Oftalmología", "Otorrinolaringología", "Endocrinología", "Gastroenterología", "Neurología"]
SEGUROS = ["Ninguno", "Rimac", "Pacífico", "La Positiva", "Mapfre", "Sanitas", "Interseguro"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
ADMIN_USER = "admin"; ADMIN_PASS = "admin"

# --- Módulos de Gestión ---
class VentanaGestionPacientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Pacientes"); self.setGeometry(150, 150, 1000, 600)
        layout = QVBoxLayout(self)
        controles_layout = QHBoxLayout()
        self.filtro_paciente = QLineEdit(placeholderText="Buscar por nombre, DNI..."); self.filtro_paciente.textChanged.connect(self.cargar_pacientes)
        btn_agregar = QPushButton(QIcon("icons/add.png"), " Añadir Paciente"); btn_agregar.clicked.connect(self.abrir_dialogo_paciente)
        btn_editar = QPushButton(QIcon("icons/edit.png"), " Editar Paciente"); btn_editar.clicked.connect(self.editar_paciente_seleccionado)
        controles_layout.addWidget(QLabel("<b>Buscar:</b>")); controles_layout.addWidget(self.filtro_paciente)
        controles_layout.addWidget(btn_agregar); controles_layout.addWidget(btn_editar)
        self.tabla_pacientes = QTableWidget(columnCount=8, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_pacientes.setHorizontalHeaderLabels(["ID", "DNI", "Nombre", "Apellidos", "Fecha Nac.", "Género", "Teléfono", "Email"])
        self.tabla_pacientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addLayout(controles_layout); layout.addWidget(self.tabla_pacientes)
        self.cargar_pacientes()
    def cargar_pacientes(self):
        pacientes = database.obtener_pacientes(self.filtro_paciente.text())
        self.tabla_pacientes.setRowCount(len(pacientes))
        for r, pac in enumerate(pacientes):
            for c, val in enumerate(pac):
                if c < 8: self.tabla_pacientes.setItem(r, c, QTableWidgetItem(str(val)))
    def abrir_dialogo_paciente(self):
        dialogo = DialogoPaciente(parent=self)
        if dialogo.exec(): database.agregar_paciente(*dialogo.get_data()); QMessageBox.information(self, "Éxito", "Paciente agregado."); self.cargar_pacientes()
    def editar_paciente_seleccionado(self):
        row = self.tabla_pacientes.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione un paciente.")
        paciente_id = int(self.tabla_pacientes.item(row, 0).text())
        dialogo = DialogoPaciente(paciente_id, self)
        if dialogo.exec(): database.actualizar_paciente(paciente_id, *dialogo.get_data()); QMessageBox.information(self, "Éxito", "Paciente actualizado."); self.cargar_pacientes()

class VentanaGestionMedicos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Médicos"); self.setGeometry(150, 150, 900, 600)
        layout = QVBoxLayout(self)
        controles_layout = QHBoxLayout()
        self.filtro_medico = QLineEdit(placeholderText="Buscar por nombre o especialidad..."); self.filtro_medico.textChanged.connect(self.cargar_medicos)
        btn_agregar = QPushButton(QIcon("icons/add.png"), " Añadir Médico"); btn_agregar.clicked.connect(self.abrir_dialogo_medico)
        btn_editar = QPushButton(QIcon("icons/edit.png"), " Editar Médico"); btn_editar.clicked.connect(self.editar_medico_seleccionado)
        controles_layout.addWidget(QLabel("<b>Buscar:</b>")); controles_layout.addWidget(self.filtro_medico)
        controles_layout.addWidget(btn_agregar); controles_layout.addWidget(btn_editar)
        self.tabla_medicos = QTableWidget(columnCount=4, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_medicos.setHorizontalHeaderLabels(["ID", "Nombre Completo", "Especialidad", "Teléfono"])
        self.tabla_medicos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addLayout(controles_layout); layout.addWidget(self.tabla_medicos)
        self.cargar_medicos()
    def cargar_medicos(self):
        medicos = database.obtener_medicos(self.filtro_medico.text())
        self.tabla_medicos.setRowCount(len(medicos))
        for r, med in enumerate(medicos):
            for c, val in enumerate(med): self.tabla_medicos.setItem(r, c, QTableWidgetItem(str(val)))
    def abrir_dialogo_medico(self):
        dialogo = DialogoMedico(parent=self)
        if dialogo.exec(): database.agregar_medico(*dialogo.get_data()); QMessageBox.information(self, "Éxito", "Médico agregado."); self.cargar_medicos()
    def editar_medico_seleccionado(self):
        row = self.tabla_medicos.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione un médico.")
        medico_id = int(self.tabla_medicos.item(row, 0).text())
        dialogo = DialogoMedico(medico_id, self)
        if dialogo.exec(): database.actualizar_medico(medico_id, *dialogo.get_data()); QMessageBox.information(self, "Éxito", "Médico actualizado."); self.cargar_medicos()

class VentanaGestionCitas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Citas y Consultas"); self.setGeometry(150, 150, 1200, 700)
        layout = QVBoxLayout(self)
        controles = QHBoxLayout()
        btn_crear = QPushButton(QIcon("icons/add.png"), " Crear Cita"); btn_crear.clicked.connect(self.crear_cita)
        btn_editar = QPushButton(QIcon("icons/edit.png"), " Editar / Ver Consulta"); btn_editar.clicked.connect(self.editar_cita_consulta)
        controles.addWidget(btn_crear); controles.addWidget(btn_editar); controles.addStretch()
        self.tabla_citas = QTableWidget(columnCount=9, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_citas.setHorizontalHeaderLabels(["ID", "Paciente", "Médico", "Especialidad", "Fecha/Hora", "Estado", "Método Pago", "Tiene Seguro", "Aseguradora"])
        self.tabla_citas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents); self.tabla_citas.horizontalHeader().setStretchLastSection(True)
        layout.addLayout(controles); layout.addWidget(self.tabla_citas)
        self.cargar_citas()
    def cargar_citas(self):
        citas = database.obtener_citas_detalladas()
        self.tabla_citas.setRowCount(len(citas))
        for r, cita in enumerate(citas):
            cita_id = cita[0]
            for c, val in enumerate(cita):
                if c == 5: continue
                self.tabla_citas.setItem(r, c, QTableWidgetItem(str(val) if val else ""))
            combo = QComboBox(); combo.addItems(["Programada", "Completada", "Cancelada"]); combo.setCurrentText(cita['estado'])
            combo.currentTextChanged.connect(lambda text, cid=cita_id: database.actualizar_estado_cita(cid, text))
            self.tabla_citas.setCellWidget(r, 5, combo)
    def crear_cita(self):
        dialogo = DialogoCitaConsulta(parent=self)
        if dialogo.exec():
            datos = dialogo.get_data()
            if not datos: return QMessageBox.warning(self, "Atención", "Debe seleccionar una hora disponible.")
            database.agregar_cita(datos); QMessageBox.information(self, "Éxito", "Cita creada."); self.cargar_citas()
    def editar_cita_consulta(self):
        row = self.tabla_citas.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione una cita.")
        cita_id = int(self.tabla_citas.item(row, 0).text())
        dialogo = DialogoCitaConsulta(cita_id=cita_id, parent=self)
        if dialogo.exec():
            datos = dialogo.get_data()
            if not datos: return QMessageBox.warning(self, "Atención", "Debe seleccionar una hora disponible.")
            database.actualizar_consulta(cita_id, datos); QMessageBox.information(self, "Éxito", "Cita actualizada."); self.cargar_citas()

# --- DIÁLOGOS ---
class DialogoPaciente(QDialog):
    def __init__(self, paciente_id=None, parent=None):
        super().__init__(parent)
        self.paciente_id = paciente_id
        self.setWindowTitle("Gestionar Paciente"); self.layout = QFormLayout(self)
        self.dni, self.nombre, self.apellidos = QLineEdit(), QLineEdit(), QLineEdit()
        self.fecha_nac = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.genero = QComboBox(); self.genero.addItems(["Masculino", "Femenino", "Otro"])
        self.telefono, self.email = QLineEdit(), QLineEdit(); self.historial = QTextEdit()
        self.layout.addRow("<b>DNI:</b>", self.dni); self.layout.addRow("<b>Nombre:</b>", self.nombre); self.layout.addRow("<b>Apellidos:</b>", self.apellidos)
        self.layout.addRow("<b>Fecha de Nacimiento:</b>", self.fecha_nac); self.layout.addRow("<b>Género:</b>", self.genero)
        self.layout.addRow("<b>Teléfono:</b>", self.telefono); self.layout.addRow("<b>Email:</b>", self.email)
        self.layout.addRow("<b>Historial Básico:</b>", self.historial)
        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.botones.accepted.connect(self.accept); self.botones.rejected.connect(self.reject)
        self.layout.addWidget(self.botones)
        if self.paciente_id: self.cargar_datos_paciente()
    def cargar_datos_paciente(self):
        p = database.obtener_paciente_por_id(self.paciente_id)
        if p: self.dni.setText(p['dni']); self.nombre.setText(p['nombre']); self.apellidos.setText(p['apellidos']); self.fecha_nac.setDate(QDate.fromString(p['fecha_nac'], "yyyy-MM-dd")); self.genero.setCurrentText(p['genero']); self.telefono.setText(p['telefono']); self.email.setText(p['email']); self.historial.setText(p['historial_basico'])
    def get_data(self): return (self.dni.text(), self.nombre.text(), self.apellidos.text(), self.fecha_nac.date().toString("yyyy-MM-dd"), self.genero.currentText(), self.telefono.text(), self.email.text(), self.historial.toPlainText())

class DialogoMedico(QDialog):
    def __init__(self, medico_id=None, parent=None):
        super().__init__(parent)
        self.medico_id = medico_id
        self.setWindowTitle("Gestionar Médico y Horarios"); self.setMinimumWidth(400)
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.nombre = QLineEdit(); self.especialidad = QComboBox(); self.especialidad.addItems(ESPECIALIDADES)
        self.telefono = QLineEdit()
        form_layout.addRow("<b>Nombre Completo:</b>", self.nombre)
        form_layout.addRow("<b>Especialidad:</b>", self.especialidad)
        form_layout.addRow("<b>Teléfono:</b>", self.telefono)
        horarios_group = QGroupBox("Horarios de Atención"); horarios_layout = QGridLayout()
        self.horarios_widgets = {}
        for i, dia in enumerate(DIAS_SEMANA):
            check = QCheckBox(dia); inicio = QTimeEdit(time(9, 0)); fin = QTimeEdit(time(17, 0))
            inicio.setEnabled(False); fin.setEnabled(False)
            check.toggled.connect(inicio.setEnabled); check.toggled.connect(fin.setEnabled)
            horarios_layout.addWidget(check, i, 0); horarios_layout.addWidget(QLabel("de"), i, 1); horarios_layout.addWidget(inicio, i, 2); horarios_layout.addWidget(QLabel("a"), i, 3); horarios_layout.addWidget(fin, i, 4)
            self.horarios_widgets[i] = {'check': check, 'inicio': inicio, 'fin': fin}
        horarios_group.setLayout(horarios_layout)
        main_layout.addLayout(form_layout); main_layout.addWidget(horarios_group)
        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.botones.accepted.connect(self.accept); self.botones.rejected.connect(self.reject)
        main_layout.addWidget(self.botones)
        if self.medico_id: self.cargar_datos_medico()
    def cargar_datos_medico(self):
        medico = database.obtener_medico_por_id(self.medico_id)
        horarios = database.obtener_horarios_por_medico(self.medico_id)
        if medico: self.nombre.setText(medico['nombre_completo']); self.especialidad.setCurrentText(medico['especialidad']); self.telefono.setText(medico['telefono'])
        for dia_idx, data in horarios.items():
            widgets = self.horarios_widgets[dia_idx]
            widgets['check'].setChecked(True); widgets['inicio'].setTime(QTime.fromString(data['inicio'], "HH:mm")); widgets['fin'].setTime(QTime.fromString(data['fin'], "HH:mm"))
    def get_data(self):
        horarios = {}
        for dia_idx, widgets in self.horarios_widgets.items():
            if widgets['check'].isChecked(): horarios[dia_idx] = {'inicio': widgets['inicio'].time().toString("HH:mm"),'fin': widgets['fin'].time().toString("HH:mm")}
        return self.nombre.text(), self.especialidad.currentText(), self.telefono.text(), horarios

class DialogoCitaConsulta(QDialog):
    def __init__(self, cita_id=None, parent=None):
        super().__init__(parent)
        self.cita_id = cita_id; self.setMinimumSize(800, 800)
        self.layout = QGridLayout(self)
        left_widget = QWidget(); left_layout = QFormLayout(left_widget)
        self.paciente_combo = QComboBox(); self.especialidad_combo = QComboBox(); self.especialidad_combo.addItems(ESPECIALIDADES)
        self.medico_combo = QComboBox(); self.calendario = QCalendarWidget(); self.hora_combo = QComboBox()
        left_layout.addRow("<b>Paciente:</b>", self.paciente_combo); left_layout.addRow("<b>Especialidad:</b>", self.especialidad_combo); left_layout.addRow("<b>Médico:</b>", self.medico_combo)
        left_layout.addRow(self.calendario); left_layout.addRow("<b>Hora Disponible:</b>", self.hora_combo)
        right_widget = QWidget(); right_layout = QFormLayout(right_widget)
        pago_group = QGroupBox("Pago y Seguro"); pago_layout = QFormLayout(); pago_group.setLayout(pago_layout)
        self.metodo_pago_combo = QComboBox(); self.metodo_pago_combo.addItems(["Efectivo", "Crédito"])
        self.usa_seguro_check = QCheckBox("Usa Seguro")
        self.aseguradora_combo = QComboBox(); self.aseguradora_combo.addItems(SEGUROS)
        pago_layout.addRow("<b>Método de Pago:</b>", self.metodo_pago_combo)
        pago_layout.addRow(self.usa_seguro_check); pago_layout.addRow("<b>Aseguradora:</b>", self.aseguradora_combo)
        self.consulta_group = QGroupBox("Registro Clínico"); consulta_layout = QFormLayout(); self.consulta_group.setLayout(consulta_layout)
        self.sintomas = QTextEdit(); self.diagnostico = QTextEdit(); self.tratamiento = QTextEdit(); self.notas = QTextEdit()
        consulta_layout.addRow("<b>Síntomas:</b>", self.sintomas); consulta_layout.addRow("<b>Diagnóstico:</b>", self.diagnostico); consulta_layout.addRow("<b>Tratamiento:</b>", self.tratamiento); consulta_layout.addRow("<b>Notas Adicionales:</b>", self.notas)
        right_layout.addWidget(pago_group); right_layout.addWidget(self.consulta_group)
        self.layout.addWidget(left_widget, 0, 0); self.layout.addWidget(right_widget, 0, 1)
        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.botones, 1, 0, 1, 2)
        self.especialidad_combo.currentTextChanged.connect(self.actualizar_medicos); self.medico_combo.currentIndexChanged.connect(self.pintar_mes_actual)
        self.calendario.selectionChanged.connect(self.actualizar_horas_disponibles); self.calendario.currentPageChanged.connect(self.pintar_mes_actual)
        self.usa_seguro_check.toggled.connect(self.aseguradora_combo.setVisible)
        self.botones.accepted.connect(self.accept); self.botones.rejected.connect(self.reject)
        self.cargar_pacientes(); self.actualizar_medicos(); self.aseguradora_combo.setVisible(False)
        if self.cita_id: self.setWindowTitle("Editar Cita y Consulta"); self.consulta_group.setVisible(True); self.cargar_datos_cita()
        else: self.setWindowTitle("Crear Nueva Cita"); self.consulta_group.setVisible(False)
    def cargar_pacientes(self):
        for p in database.obtener_pacientes(): self.paciente_combo.addItem(f"{p['nombre']} {p['apellidos']} (DNI: {p['dni']})", userData=p['id'])
    def actualizar_medicos(self, especialidad=None):
        self.medico_combo.blockSignals(True); self.medico_combo.clear()
        especialidad = especialidad or self.especialidad_combo.currentText()
        for m in database.obtener_medicos_por_especialidad(especialidad): self.medico_combo.addItem(m['nombre_completo'], userData=m['id'])
        self.medico_combo.blockSignals(False); self.pintar_mes_actual()
    def pintar_mes_actual(self):
        medico_id = self.medico_combo.currentData(); year = self.calendario.yearShown(); month = self.calendario.monthShown()
        formato_vacio = QTextCharFormat()
        for day in range(1, 32): self.calendario.setDateTextFormat(QDate(year, month, day), formato_vacio)
        if not medico_id: return
        horarios_medico = database.obtener_horarios_por_medico(medico_id)
        formato_verde = QTextCharFormat(); formato_verde.setBackground(QBrush(QColor("#a8e6cf"))); formato_rojo = QTextCharFormat(); formato_rojo.setBackground(QBrush(QColor("#ff8a80"))); formato_negro = QTextCharFormat(); formato_negro.setBackground(QBrush(QColor("#e0e0e0")))
        dias_en_mes = QDate(year, month, 1).daysInMonth()
        for day in range(1, dias_en_mes + 1):
            fecha = QDate(year, month, day); dia_semana = fecha.dayOfWeek() - 1 
            if dia_semana in horarios_medico:
                citas_del_dia = database.obtener_citas_por_medico_y_dia(medico_id, fecha.toString("yyyy-MM-dd"))
                inicio = datetime.strptime(horarios_medico[dia_semana]['inicio'], '%H:%M').time(); fin = datetime.strptime(horarios_medico[dia_semana]['fin'], '%H:%M').time()
                total_slots = (datetime.combine(datetime.min, fin) - datetime.combine(datetime.min, inicio)) // timedelta(minutes=20)
                if len(citas_del_dia) >= total_slots: self.calendario.setDateTextFormat(fecha, formato_rojo)
                else: self.calendario.setDateTextFormat(fecha, formato_verde)
            else: self.calendario.setDateTextFormat(fecha, formato_negro)
        self.actualizar_horas_disponibles()
    def actualizar_horas_disponibles(self):
        self.hora_combo.clear(); medico_id = self.medico_combo.currentData(); fecha_seleccionada = self.calendario.selectedDate()
        if not medico_id: return
        horarios_medico = database.obtener_horarios_por_medico(medico_id)
        dia_semana = fecha_seleccionada.dayOfWeek() - 1
        if dia_semana in horarios_medico:
            citas_ocupadas = [datetime.strptime(c, '%Y-%m-%d %H:%M:%S').time() for c in database.obtener_citas_por_medico_y_dia(medico_id, fecha_seleccionada.toString("yyyy-MM-dd"))]
            hora_actual = datetime.strptime(horarios_medico[dia_semana]['inicio'], '%H:%M'); hora_fin = datetime.strptime(horarios_medico[dia_semana]['fin'], '%H:%M')
            while hora_actual < hora_fin:
                if hora_actual.time() not in citas_ocupadas: self.hora_combo.addItem(hora_actual.strftime('%H:%M'))
                hora_actual += timedelta(minutes=20)
    def cargar_datos_cita(self):
        cita = database.obtener_cita_completa_por_id(self.cita_id)
        if not cita: return
        self.paciente_combo.setCurrentIndex(self.paciente_combo.findData(cita['paciente_id']))
        medico = database.obtener_medico_por_id(cita['medico_id'])
        if medico: self.especialidad_combo.setCurrentText(medico['especialidad']); self.actualizar_medicos(medico['especialidad']); self.medico_combo.setCurrentIndex(self.medico_combo.findData(medico['id']))
        dt_cita = QDateTime.fromString(cita['fecha_hora'], "yyyy-MM-dd HH:mm:ss")
        self.calendario.setSelectedDate(dt_cita.date()); self.pintar_mes_actual()
        hora_str = dt_cita.time().toString("HH:mm")
        if self.hora_combo.findText(hora_str) == -1: self.hora_combo.addItem(hora_str)
        self.hora_combo.setCurrentText(hora_str)
        self.metodo_pago_combo.setCurrentText(cita['metodo_pago'])
        if cita['tiene_seguro'] == 'Sí': self.usa_seguro_check.setChecked(True); self.aseguradora_combo.setCurrentText(cita['aseguradora'])
        self.sintomas.setText(cita['sintomas']); self.diagnostico.setText(cita['diagnostico']); self.tratamiento.setText(cita['tratamiento']); self.notas.setText(cita['notas'])
    def get_data(self):
        hora = self.hora_combo.currentText()
        if not hora: return None
        fecha_hora = f"{self.calendario.selectedDate().toString('yyyy-MM-dd')} {hora}:00"
        metodo_pago = self.metodo_pago_combo.currentText()
        tiene_seguro = 'Sí' if self.usa_seguro_check.isChecked() else 'No'
        aseguradora = self.aseguradora_combo.currentText() if self.usa_seguro_check.isChecked() else None
        sintomas = self.sintomas.toPlainText() if self.cita_id else ""
        diagnostico = self.diagnostico.toPlainText() if self.cita_id else ""
        tratamiento = self.tratamiento.toPlainText() if self.cita_id else ""
        notas = self.notas.toPlainText() if self.cita_id else ""
        return (self.paciente_combo.currentData(), self.medico_combo.currentData(), fecha_hora, metodo_pago, tiene_seguro, aseguradora, sintomas, diagnostico, tratamiento, notas)

# --- LOGIN Y DASHBOARD ---
class VentanaLogin(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Bienvenido a GesClínica"); self.setFixedSize(400, 500)
        widget_central = QWidget(); self.setCentralWidget(widget_central)
        main_layout = QVBoxLayout(widget_central); main_layout.setAlignment(Qt.AlignCenter)
        logo_label = QLabel("GesClínica"); logo_label.setFont(QFont("Arial", 40, QFont.Bold)); logo_label.setStyleSheet("color: #007acc;"); logo_label.setAlignment(Qt.AlignCenter)
        frame = QFrame(); frame.setFrameShape(QFrame.StyledPanel); frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
        form_layout = QFormLayout(frame); form_layout.setContentsMargins(20, 20, 20, 20); form_layout.setVerticalSpacing(15)
        self.usuario = QLineEdit(); self.usuario.setPlaceholderText("admin")
        self.clave = QLineEdit(); self.clave.setPlaceholderText("••••••••"); self.clave.setEchoMode(QLineEdit.Password)
        form_layout.addRow(QLabel("<b>Usuario:</b>"), self.usuario)
        form_layout.addRow(QLabel("<b>Contraseña:</b>"), self.clave)
        btn_ingresar = QPushButton("Ingresar"); btn_ingresar.clicked.connect(self.verificar_login)
        main_layout.addWidget(logo_label); main_layout.addSpacing(20); main_layout.addWidget(frame); main_layout.addSpacing(20); main_layout.addWidget(btn_ingresar)
    def verificar_login(self):
        if self.usuario.text() == ADMIN_USER and self.clave.text() == ADMIN_PASS:
            self.dashboard = Dashboard(); self.dashboard.show(); self.close()
        else: QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos."); self.clave.clear()

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GesClínica - Panel Principal"); self.setGeometry(100, 100, 800, 600)
        self.ventanas_abiertas = {}
        widget_central = QWidget(); self.setCentralWidget(widget_central)
        layout = QVBoxLayout(widget_central)
        titulo = QLabel("Panel de Control Principal"); titulo.setAlignment(Qt.AlignCenter); titulo.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: #005c99;")
        layout.addWidget(titulo)
        menu_layout = QGridLayout(); layout.addLayout(menu_layout)
        btn_citas = self.crear_boton_menu("Citas y Consultas", "icons/appointment.png", self.abrir_gestion_citas)
        btn_pacientes = self.crear_boton_menu("Pacientes", "icons/patient.png", self.abrir_gestion_pacientes)
        btn_medicos = self.crear_boton_menu("Médicos", "icons/doctor.png", self.abrir_gestion_medicos)
        btn_salir = self.crear_boton_menu("Salir", "icons/exit.png", self.close, es_rojo=True)
        menu_layout.addWidget(btn_citas, 0, 0); menu_layout.addWidget(btn_pacientes, 0, 1)
        menu_layout.addWidget(btn_medicos, 1, 0); menu_layout.addWidget(btn_salir, 1, 1)

    def crear_boton_menu(self, texto, icon_path, funcion_click, es_rojo=False):
        btn = QPushButton(QIcon(icon_path), f"  {texto}"); btn.setIconSize(QSize(48, 48)); btn.setMinimumSize(250, 120)
        # --- LÍNEA CORREGIDA ---
        style = "QPushButton {color: #005c99; font-size: 18px; font-weight: bold; border-radius: 10px; background-color: #ffffff; border: 2px solid #007acc; text-align: center; padding: 10px;} QPushButton:hover {background-color: #eaf5ff; border-color: #005c99;}"
        if es_rojo: style = "QPushButton {color: #c0392b; font-size: 18px; font-weight: bold; border-radius: 10px; background-color: #fce4e4; border: 2px solid #e74c3c;} QPushButton:hover {background-color: #f8c0c0;}"
        btn.setStyleSheet(style)
        btn.clicked.connect(funcion_click)
        return btn
    def abrir_ventana(self, nombre_ventana, clase_ventana):
        if nombre_ventana not in self.ventanas_abiertas or not self.ventanas_abiertas[nombre_ventana].isVisible():
            self.ventanas_abiertas[nombre_ventana] = clase_ventana(); self.ventanas_abiertas[nombre_ventana].show()
        else: self.ventanas_abiertas[nombre_ventana].activateWindow(); self.ventanas_abiertas[nombre_ventana].raise_()
    def abrir_gestion_citas(self): self.abrir_ventana("citas", VentanaGestionCitas)
    def abrir_gestion_pacientes(self): self.abrir_ventana("pacientes", VentanaGestionPacientes)
    def abrir_gestion_medicos(self): self.abrir_ventana("medicos", VentanaGestionMedicos)

if __name__ == "__main__":
    database.crear_tablas()
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)
    login_window = VentanaLogin()
    login_window.show()
    sys.exit(app.exec())