# ui_components/appointment_module.py
from datetime import datetime, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QFormLayout, QComboBox, QDialogButtonBox, QCalendarWidget, QHeaderView, QGridLayout
from PySide6.QtGui import QIcon, QColor, QTextCharFormat, QBrush
from PySide6.QtCore import QDate, QTime, QDateTime

import data_manager
from config import ESPECIALIDADES

class DialogoCrearCita(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Nueva Cita"); self.setMinimumSize(450, 600)
        self.layout = QFormLayout(self)
        self.paciente_combo = QComboBox(); self.especialidad_combo = QComboBox(); self.especialidad_combo.addItems(ESPECIALIDADES)
        self.medico_combo = QComboBox(); self.calendario = QCalendarWidget(); self.hora_combo = QComboBox()
        self.layout.addRow("<b>Paciente:</b>", self.paciente_combo); self.layout.addRow("<b>Especialidad:</b>", self.especialidad_combo)
        self.layout.addRow("<b>Médico:</b>", self.medico_combo); self.layout.addRow(self.calendario)
        self.layout.addRow("<b>Hora Disponible:</b>", self.hora_combo)
        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); self.layout.addWidget(self.botones)
        
        self.especialidad_combo.currentTextChanged.connect(self.actualizar_medicos); self.medico_combo.currentIndexChanged.connect(self.pintar_mes_actual)
        self.calendario.selectionChanged.connect(self.actualizar_horas_disponibles); self.calendario.currentPageChanged.connect(self.pintar_mes_actual)
        self.botones.accepted.connect(self.accept); self.botones.rejected.connect(self.reject)
        self.cargar_pacientes(); self.actualizar_medicos()

    def cargar_pacientes(self):
        for p in data_manager.get_all_patients(): self.paciente_combo.addItem(f"{p['nombre']} {p['apellidos']} (DNI: {p['dni']})", userData=p['id'])
    
    def get_data(self):
        hora = self.hora_combo.currentText()
        if not hora: return None
        fecha_hora = f"{self.calendario.selectedDate().toString('yyyy-MM-dd')} {hora}:00"
        return (self.paciente_combo.currentData(), self.medico_combo.currentData(), fecha_hora)
    
    def actualizar_medicos(self, especialidad=None):
        self.medico_combo.blockSignals(True); self.medico_combo.clear()
        especialidad = especialidad or self.especialidad_combo.currentText()
        for m in data_manager.get_doctors_by_specialty(especialidad): self.medico_combo.addItem(m['nombre_completo'], userData=m['id'])
        self.medico_combo.blockSignals(False); self.pintar_mes_actual()
    def pintar_mes_actual(self):
        medico_id = self.medico_combo.currentData(); year = self.calendario.yearShown(); month = self.calendario.monthShown()
        formato_vacio = QTextCharFormat()
        for day in range(1, 32): self.calendario.setDateTextFormat(QDate(year, month, day), formato_vacio)
        if not medico_id: return
        horarios_medico = data_manager.get_doctor_schedules(medico_id)
        formato_verde = QTextCharFormat(); formato_verde.setBackground(QBrush(QColor("#a8e6cf"))); formato_rojo = QTextCharFormat(); formato_rojo.setBackground(QBrush(QColor("#ff8a80"))); formato_negro = QTextCharFormat(); formato_negro.setBackground(QBrush(QColor("#e0e0e0")))
        dias_en_mes = QDate(year, month, 1).daysInMonth()
        for day in range(1, dias_en_mes + 1):
            fecha = QDate(year, month, day); dia_semana = fecha.dayOfWeek() - 1 
            if dia_semana in horarios_medico:
                citas_del_dia = data_manager.get_appointments_by_doctor_and_day(medico_id, fecha.toString("yyyy-MM-dd"))
                inicio = datetime.strptime(horarios_medico[dia_semana]['inicio'], '%H:%M').time(); fin = datetime.strptime(horarios_medico[dia_semana]['fin'], '%H:%M').time()
                total_slots = (datetime.combine(datetime.min, fin) - datetime.combine(datetime.min, inicio)) // timedelta(minutes=20)
                if len(citas_del_dia) >= total_slots: self.calendario.setDateTextFormat(fecha, formato_rojo)
                else: self.calendario.setDateTextFormat(fecha, formato_verde)
            else: self.calendario.setDateTextFormat(fecha, formato_negro)
        self.actualizar_horas_disponibles()
    def actualizar_horas_disponibles(self):
        self.hora_combo.clear(); medico_id = self.medico_combo.currentData(); fecha_seleccionada = self.calendario.selectedDate()
        if not medico_id: return
        horarios_medico = data_manager.get_doctor_schedules(medico_id)
        dia_semana = fecha_seleccionada.dayOfWeek() - 1
        if dia_semana in horarios_medico:
            citas_ocupadas = [datetime.strptime(c, '%Y-%m-%d %H:%M:%S').time() for c in data_manager.get_appointments_by_doctor_and_day(medico_id, fecha_seleccionada.toString("yyyy-MM-dd"))]
            hora_actual = datetime.strptime(horarios_medico[dia_semana]['inicio'], '%H:%M'); hora_fin = datetime.strptime(horarios_medico[dia_semana]['fin'], '%H:%M')
            while hora_actual < hora_fin:
                if hora_actual.time() not in citas_ocupadas: self.hora_combo.addItem(hora_actual.strftime('%H:%M'))
                hora_actual += timedelta(minutes=20)

class VentanaGestionCitas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Citas"); self.setGeometry(150, 150, 1200, 700)
        layout = QVBoxLayout(self)
        controles = QHBoxLayout()
        btn_crear = QPushButton(QIcon("icons/add.png"), " Crear Cita"); btn_crear.clicked.connect(self.crear_cita)
        btn_eliminar = QPushButton(QIcon("icons/delete.png"), " Eliminar Cita"); btn_eliminar.clicked.connect(self.eliminar_cita)
        btn_eliminar.setStyleSheet("background-color: #e74c3c;"); # Estilo rojo
        controles.addWidget(btn_crear); controles.addStretch(); controles.addWidget(btn_eliminar)
        
        self.tabla_citas = QTableWidget(columnCount=6, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_citas.setHorizontalHeaderLabels(["ID", "Paciente", "Médico", "Especialidad", "Fecha/Hora", "Estado"])
        self.tabla_citas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_citas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # Fecha/Hora
        layout.addLayout(controles); layout.addWidget(self.tabla_citas)
        self.cargar_citas()
    
    def cargar_citas(self):
        citas = data_manager.get_all_detailed_appointments()
        self.tabla_citas.setRowCount(len(citas))
        for r, cita in enumerate(citas):
            for c, val in enumerate(cita): self.tabla_citas.setItem(r, c, QTableWidgetItem(str(val)))
            
    def crear_cita(self):
        dialogo = DialogoCrearCita(parent=self)
        if dialogo.exec():
            datos = dialogo.get_data()
            if not datos: return QMessageBox.warning(self, "Atención", "Debe seleccionar una hora disponible.")
            data_manager.create_appointment(datos); QMessageBox.information(self, "Éxito", "Cita creada."); self.cargar_citas()
            
    def eliminar_cita(self):
        row = self.tabla_citas.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione una cita para eliminar.")
        
        estado = self.tabla_citas.item(row, 5).text()
        if estado == "Pagada":
            return QMessageBox.critical(self, "Acción no permitida", "No se puede eliminar una cita que ya ha sido pagada.")

        cita_id = int(self.tabla_citas.item(row, 0).text())
        paciente = self.tabla_citas.item(row, 1).text()
        fecha = self.tabla_citas.item(row, 4).text()
        
        confirm = QMessageBox.question(self, "Confirmar Eliminación", 
            f"¿Está seguro de que desea eliminar la cita de <b>{paciente}</b> para el <b>{fecha}</b>?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No)
            
        if confirm == QMessageBox.Yes:
            data_manager.delete_appointment(cita_id)
            QMessageBox.information(self, "Éxito", "La cita ha sido eliminada.")
            self.cargar_citas()