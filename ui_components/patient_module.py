# ui_components/patient_module.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QFormLayout, QDateEdit, QComboBox, QTextEdit, QDialogButtonBox, QHeaderView, QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import QDate

import data_manager

# --- Diálogo de Paciente (sin cambios) ---
class DialogoPaciente(QDialog):
    # ... (Esta clase no cambia)
    def __init__(self, paciente_id=None, parent=None):
        super().__init__(parent); self.paciente_id = paciente_id; self.setWindowTitle("Gestionar Paciente"); self.layout = QFormLayout(self)
        self.dni, self.nombre, self.apellidos = QLineEdit(), QLineEdit(), QLineEdit()
        self.fecha_nac = QDateEdit(calendarPopup=True, date=QDate.currentDate()); self.genero = QComboBox(); self.genero.addItems(["Masculino", "Femenino", "Otro"])
        self.telefono, self.email = QLineEdit(), QLineEdit(); self.historial = QTextEdit()
        self.layout.addRow("<b>DNI:</b>", self.dni); self.layout.addRow("<b>Nombre:</b>", self.nombre); self.layout.addRow("<b>Apellidos:</b>", self.apellidos)
        self.layout.addRow("<b>Fecha de Nacimiento:</b>", self.fecha_nac); self.layout.addRow("<b>Género:</b>", self.genero)
        self.layout.addRow("<b>Teléfono:</b>", self.telefono); self.layout.addRow("<b>Email:</b>", self.email)
        self.layout.addRow("<b>Historial Básico:</b>", self.historial)
        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self); self.botones.accepted.connect(self.accept); self.botones.rejected.connect(self.reject); self.layout.addWidget(self.botones)
        if self.paciente_id: self.cargar_datos_paciente()
    def cargar_datos_paciente(self):
        p = data_manager.get_patient_by_id(self.paciente_id)
        if p: self.dni.setText(p['dni']); self.nombre.setText(p['nombre']); self.apellidos.setText(p['apellidos']); self.fecha_nac.setDate(QDate.fromString(p['fecha_nac'], "yyyy-MM-dd")); self.genero.setCurrentText(p['genero']); self.telefono.setText(p['telefono']); self.email.setText(p['email']); self.historial.setText(p['historial_basico'])
    def get_data(self): return (self.dni.text(), self.nombre.text(), self.apellidos.text(), self.fecha_nac.date().toString("yyyy-MM-dd"), self.genero.currentText(), self.telefono.text(), self.email.text(), self.historial.toPlainText())

# --- Nueva Ventana para ver el Historial Clínico ---
class VentanaHistorialClinico(QDialog):
    def __init__(self, paciente_id, paciente_nombre, parent=None):
        super().__init__(parent)
        self.paciente_id = paciente_id
        self.setWindowTitle(f"Historial Clínico de: {paciente_nombre}")
        self.setMinimumSize(800, 600)
        
        self.layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Fecha", "Médico", "Especialidad"])
        self.tree.setColumnWidth(0, 180)
        self.tree.setColumnWidth(1, 250)
        
        self.layout.addWidget(self.tree)
        self.cargar_historial()

    def cargar_historial(self):
        historial = data_manager.get_patient_clinical_history(self.paciente_id)
        for consulta in historial:
            # Item principal con la info de la cita
            item_cita = QTreeWidgetItem(self.tree, [
                consulta['fecha_hora'],
                consulta['nombre_completo'],
                consulta['especialidad']
            ])
            # Hijos con los detalles clínicos
            QTreeWidgetItem(item_cita, ["Síntomas:", consulta['sintomas']])
            QTreeWidgetItem(item_cita, ["Diagnóstico:", consulta['diagnostico']])
            QTreeWidgetItem(item_cita, ["Tratamiento:", consulta['tratamiento']])
            self.tree.expandAll()

# --- Ventana de Gestión de Pacientes con el nuevo botón ---
class VentanaGestionPacientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Pacientes"); self.setGeometry(150, 150, 1100, 600)
        layout = QVBoxLayout(self)
        controles_layout = QHBoxLayout()
        self.filtro_paciente = QLineEdit(placeholderText="Buscar por nombre, DNI..."); self.filtro_paciente.textChanged.connect(self.cargar_pacientes)
        btn_agregar = QPushButton(QIcon("icons/add.png"), " Añadir Paciente"); btn_agregar.clicked.connect(self.abrir_dialogo_paciente)
        btn_editar = QPushButton(QIcon("icons/edit.png"), " Editar Paciente"); btn_editar.clicked.connect(self.editar_paciente_seleccionado)
        # NUEVO BOTÓN
        btn_historial = QPushButton(QIcon("icons/history.png"), " Ver Historial Clínico"); btn_historial.clicked.connect(self.ver_historial_clinico)
        
        controles_layout.addWidget(QLabel("<b>Buscar:</b>")); controles_layout.addWidget(self.filtro_paciente); controles_layout.addStretch()
        controles_layout.addWidget(btn_agregar); controles_layout.addWidget(btn_editar); controles_layout.addWidget(btn_historial)
        
        self.tabla_pacientes = QTableWidget(columnCount=8, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_pacientes.setHorizontalHeaderLabels(["ID", "DNI", "Nombre", "Apellidos", "Fecha Nac.", "Género", "Teléfono", "Email"])
        self.tabla_pacientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addLayout(controles_layout); layout.addWidget(self.tabla_pacientes)
        self.cargar_pacientes()

    def cargar_pacientes(self):
        pacientes = data_manager.get_all_patients(self.filtro_paciente.text())
        self.tabla_pacientes.setRowCount(len(pacientes))
        for r, pac in enumerate(pacientes):
            for c, val in enumerate(pac):
                if c < 8: self.tabla_pacientes.setItem(r, c, QTableWidgetItem(str(val)))
                
    def abrir_dialogo_paciente(self):
        dialogo = DialogoPaciente(parent=self)
        if dialogo.exec(): data_manager.add_patient(dialogo.get_data()); QMessageBox.information(self, "Éxito", "Paciente agregado."); self.cargar_pacientes()

    def editar_paciente_seleccionado(self):
        row = self.tabla_pacientes.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione un paciente.")
        paciente_id = int(self.tabla_pacientes.item(row, 0).text())
        dialogo = DialogoPaciente(paciente_id, self)
        if dialogo.exec(): data_manager.update_patient(paciente_id, dialogo.get_data()); QMessageBox.information(self, "Éxito", "Paciente actualizado."); self.cargar_pacientes()

    def ver_historial_clinico(self):
        row = self.tabla_pacientes.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione un paciente para ver su historial.")
        paciente_id = int(self.tabla_pacientes.item(row, 0).text())
        nombre = self.tabla_pacientes.item(row, 2).text()
        apellidos = self.tabla_pacientes.item(row, 3).text()
        paciente_nombre = f"{nombre} {apellidos}"
        
        self.historial_window = VentanaHistorialClinico(paciente_id, paciente_nombre, self)
        self.historial_window.exec()