# ui_components/doctor_module.py

# CAMBIO: Añadido QTableWidgetItem a la importación
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QFormLayout, QComboBox, QTimeEdit, QCheckBox, QGroupBox, QGridLayout, QDialogButtonBox, QHeaderView
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTime

import data_manager
from config import ESPECIALIDADES, DIAS_SEMANA

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
            check = QCheckBox(dia); inicio = QTimeEdit(QTime(9, 0)); fin = QTimeEdit(QTime(17, 0))
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
        medico = data_manager.get_doctor_by_id(self.medico_id)
        horarios = data_manager.get_doctor_schedules(self.medico_id)
        if medico:
            self.nombre.setText(medico['nombre_completo']); self.especialidad.setCurrentText(medico['especialidad']); self.telefono.setText(medico['telefono'])
        for dia_idx, data in horarios.items():
            widgets = self.horarios_widgets[dia_idx]
            widgets['check'].setChecked(True); widgets['inicio'].setTime(QTime.fromString(data['inicio'], "HH:mm")); widgets['fin'].setTime(QTime.fromString(data['fin'], "HH:mm"))
            
    def get_data(self):
        horarios = {}
        for dia_idx, widgets in self.horarios_widgets.items():
            if widgets['check'].isChecked(): horarios[dia_idx] = {'inicio': widgets['inicio'].time().toString("HH:mm"),'fin': widgets['fin'].time().toString("HH:mm")}
        return self.nombre.text(), self.especialidad.currentText(), self.telefono.text(), horarios

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
        medicos = data_manager.get_all_doctors(self.filtro_medico.text())
        self.tabla_medicos.setRowCount(len(medicos))
        for r, med in enumerate(medicos):
            for c, val in enumerate(med): self.tabla_medicos.setItem(r, c, QTableWidgetItem(str(val)))
            
    def abrir_dialogo_medico(self):
        dialogo = DialogoMedico(parent=self)
        if dialogo.exec():
            data_manager.add_doctor(dialogo.get_data())
            QMessageBox.information(self, "Éxito", "Médico agregado.")
            self.cargar_medicos()
            
    def editar_medico_seleccionado(self):
        row = self.tabla_medicos.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione un médico.")
        medico_id = int(self.tabla_medicos.item(row, 0).text())
        dialogo = DialogoMedico(medico_id, self)
        if dialogo.exec():
            data_manager.update_doctor(medico_id, dialogo.get_data())
            QMessageBox.information(self, "Éxito", "Médico actualizado.")
            self.cargar_medicos()