# ui_components/doctor_module.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QFormLayout, QComboBox, QTimeEdit, QCheckBox, QGroupBox, QGridLayout, QDialogButtonBox, QHeaderView, QTabWidget, QTextEdit
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTime

import data_manager
from config import ESPECIALIDADES, DIAS_SEMANA

# --- Diálogo para añadir/editar médicos (sin cambios) ---
class DialogoMedico(QDialog):
    # ... (Esta clase no cambia)
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
        if medico: self.nombre.setText(medico['nombre_completo']); self.especialidad.setCurrentText(medico['especialidad']); self.telefono.setText(medico['telefono'])
        for dia_idx, data in horarios.items():
            widgets = self.horarios_widgets[dia_idx]
            widgets['check'].setChecked(True); widgets['inicio'].setTime(QTime.fromString(data['inicio'], "HH:mm")); widgets['fin'].setTime(QTime.fromString(data['fin'], "HH:mm"))
    def get_data(self):
        horarios = {};
        for dia_idx, widgets in self.horarios_widgets.items():
            if widgets['check'].isChecked(): horarios[dia_idx] = {'inicio': widgets['inicio'].time().toString("HH:mm"),'fin': widgets['fin'].time().toString("HH:mm")}
        return self.nombre.text(), self.especialidad.currentText(), self.telefono.text(), horarios

# --- DIÁLOGO DE REGISTRO CLÍNICO COMPLETAMENTE REDISEÑADO ---
class DialogoRegistroClinico(QDialog):
    def __init__(self, cita_id, parent=None):
        super().__init__(parent)
        self.cita_id = cita_id
        self.setWindowTitle(f"Completar Registro Clínico para Cita N° {self.cita_id}")
        self.setMinimumSize(600, 700)
        
        main_layout = QVBoxLayout(self)

        # Motivo de la consulta
        self.motivo_consulta = QTextEdit()
        self.motivo_consulta.setFixedHeight(80)
        form_layout = QFormLayout()
        form_layout.addRow("<b>Motivo Principal de la Consulta:</b>", self.motivo_consulta)
        main_layout.addLayout(form_layout)
        
        # Grupo para Signos Vitales
        vitals_group = QGroupBox("Signos Vitales")
        vitals_layout = QGridLayout()
        self.temperatura = QLineEdit(); self.temperatura.setPlaceholderText("Ej: 37.5")
        self.presion = QLineEdit(); self.presion.setPlaceholderText("Ej: 120/80")
        self.frec_cardiaca = QLineEdit(); self.frec_cardiaca.setPlaceholderText("Ej: 75")
        self.saturacion = QLineEdit(); self.saturacion.setPlaceholderText("Ej: 98")
        vitals_layout.addWidget(QLabel("Temperatura (°C):"), 0, 0); vitals_layout.addWidget(self.temperatura, 0, 1)
        vitals_layout.addWidget(QLabel("Presión Arterial (mmHg):"), 0, 2); vitals_layout.addWidget(self.presion, 0, 3)
        vitals_layout.addWidget(QLabel("Frec. Cardíaca (lpm):"), 1, 0); vitals_layout.addWidget(self.frec_cardiaca, 1, 1)
        vitals_layout.addWidget(QLabel("Saturación O₂ (%):"), 1, 2); vitals_layout.addWidget(self.saturacion, 1, 3)
        vitals_group.setLayout(vitals_layout)
        main_layout.addWidget(vitals_group)

        # Grupo para la evaluación clínica
        eval_group = QGroupBox("Evaluación Clínica")
        eval_layout = QFormLayout()
        self.sintomas = QTextEdit(); self.diagnostico = QTextEdit(); self.tratamiento = QTextEdit(); self.notas = QTextEdit()
        eval_layout.addRow("<b>Síntomas y Examen Físico:</b>", self.sintomas)
        eval_layout.addRow("<b>Diagnóstico:</b>", self.diagnostico)
        eval_layout.addRow("<b>Tratamiento y Receta:</b>", self.tratamiento)
        eval_layout.addRow("<b>Notas Adicionales:</b>", self.notas)
        eval_group.setLayout(eval_layout)
        main_layout.addWidget(eval_group)

        self.botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)
        main_layout.addWidget(self.botones)

    def get_data(self):
        # Helper para convertir a número o devolver None
        def to_float(text):
            try: return float(text)
            except (ValueError, TypeError): return None
        def to_int(text):
            try: return int(text)
            except (ValueError, TypeError): return None

        return (
            self.motivo_consulta.toPlainText(),
            to_float(self.temperatura.text()),
            self.presion.text(),
            to_int(self.frec_cardiaca.text()),
            to_int(self.saturacion.text()),
            self.sintomas.toPlainText(),
            self.diagnostico.toPlainText(),
            self.tratamiento.toPlainText(),
            self.notas.toPlainText()
        )

# --- Ventana de Gestión de Médicos con Pestañas (sin cambios) ---
class VentanaGestionMedicos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Módulo de Médicos"); self.setGeometry(150, 150, 900, 700)
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Pestaña 1: Gestión de Médicos
        self.gestion_medicos_tab = QWidget()
        layout_gestion = QVBoxLayout(self.gestion_medicos_tab)
        controles_layout = QHBoxLayout()
        self.filtro_medico = QLineEdit(placeholderText="Buscar por nombre o especialidad..."); self.filtro_medico.textChanged.connect(self.cargar_medicos)
        btn_agregar = QPushButton(QIcon("icons/add.png"), " Añadir Médico"); btn_agregar.clicked.connect(self.abrir_dialogo_medico)
        btn_editar = QPushButton(QIcon("icons/edit.png"), " Editar Médico"); btn_editar.clicked.connect(self.editar_medico_seleccionado)
        controles_layout.addWidget(QLabel("<b>Buscar:</b>")); controles_layout.addWidget(self.filtro_medico)
        controles_layout.addWidget(btn_agregar); controles_layout.addWidget(btn_editar)
        self.tabla_medicos = QTableWidget(columnCount=4, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_medicos.setHorizontalHeaderLabels(["ID", "Nombre Completo", "Especialidad", "Teléfono"])
        self.tabla_medicos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_gestion.addLayout(controles_layout); layout_gestion.addWidget(self.tabla_medicos)

        # Pestaña 2: Consultas por Completar
        self.consultas_tab = QWidget()
        layout_consultas = QVBoxLayout(self.consultas_tab)
        controles_consultas = QHBoxLayout()
        btn_completar = QPushButton(QIcon("icons/edit.png"), " Llenar Registro Clínico"); btn_completar.clicked.connect(self.completar_registro_clinico)
        controles_consultas.addStretch(); controles_consultas.addWidget(btn_completar)
        self.tabla_consultas = QTableWidget(columnCount=4, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_consultas.setHorizontalHeaderLabels(["ID Cita", "Paciente", "Médico", "Fecha y Hora"])
        self.tabla_consultas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_consultas.addLayout(controles_consultas); layout_consultas.addWidget(self.tabla_consultas)

        self.tabs.addTab(self.gestion_medicos_tab, "Gestionar Médicos")
        self.tabs.addTab(self.consultas_tab, "Consultas Pagadas por Completar")
        
        self.tabs.currentChanged.connect(self.actualizar_pestanas)
        self.cargar_medicos()
        
    def actualizar_pestanas(self):
        if self.tabs.currentIndex() == 0: self.cargar_medicos()
        else: self.cargar_consultas_pagadas()

    def cargar_medicos(self):
        medicos = data_manager.get_all_doctors(self.filtro_medico.text())
        self.tabla_medicos.setRowCount(len(medicos))
        for r, med in enumerate(medicos):
            for c, val in enumerate(med): self.tabla_medicos.setItem(r, c, QTableWidgetItem(str(val)))

    def cargar_consultas_pagadas(self):
        consultas = data_manager.get_payment_history()
        consultas_pendientes = [c for c in consultas if not c['diagnostico']]
        self.tabla_consultas.setRowCount(len(consultas_pendientes))
        for r, consulta in enumerate(consultas_pendientes):
            self.tabla_consultas.setItem(r, 0, QTableWidgetItem(str(consulta['id'])))
            self.tabla_consultas.setItem(r, 1, QTableWidgetItem(str(consulta[1])))
            self.tabla_consultas.setItem(r, 2, QTableWidgetItem(str(consulta[2])))
            self.tabla_consultas.setItem(r, 3, QTableWidgetItem(str(consulta['fecha_hora'])))

    def abrir_dialogo_medico(self):
        dialogo = DialogoMedico(parent=self)
        if dialogo.exec(): data_manager.add_doctor(dialogo.get_data()); QMessageBox.information(self, "Éxito", "Médico agregado."); self.cargar_medicos()

    def editar_medico_seleccionado(self):
        row = self.tabla_medicos.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione un médico.")
        medico_id = int(self.tabla_medicos.item(row, 0).text())
        dialogo = DialogoMedico(medico_id, self)
        if dialogo.exec(): data_manager.update_doctor(medico_id, dialogo.get_data()); QMessageBox.information(self, "Éxito", "Médico actualizado."); self.cargar_medicos()

    def completar_registro_clinico(self):
        row = self.tabla_consultas.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione una consulta para completar.")
        cita_id = int(self.tabla_consultas.item(row, 0).text())
        dialogo = DialogoRegistroClinico(cita_id, self)
        if dialogo.exec():
            datos = dialogo.get_data()
            data_manager.save_clinical_record(cita_id, datos)
            QMessageBox.information(self, "Éxito", "Registro clínico guardado.")
            self.cargar_consultas_pagadas()