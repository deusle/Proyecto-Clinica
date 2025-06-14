# ventana_recetas.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QDateEdit
)
from PySide6.QtCore import QDate
import data_manager

class VentanaRecetas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Recetas Médicas")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Título
        layout.addWidget(QLabel("<h2>Agregar Nueva Receta Médica</h2>"))

        # Combo de pacientes
        self.paciente_combo = QComboBox()
        self.pacientes = data_manager.get_all_pacientes()
        for p in self.pacientes:
            self.paciente_combo.addItem(f"{p['nombre']} {p['apellidos']} - {p['dni']}", p['id'])
        layout.addWidget(QLabel("Paciente:"))
        layout.addWidget(self.paciente_combo)

        # Combo de médicos
        self.medico_combo = QComboBox()
        self.medicos = data_manager.get_all_medicos()
        for m in self.medicos:
            self.medico_combo.addItem(m['nombre_completo'], m['id'])
        layout.addWidget(QLabel("Médico:"))
        layout.addWidget(self.medico_combo)

        # Fecha
        self.fecha_edit = QDateEdit(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        layout.addWidget(QLabel("Fecha:"))
        layout.addWidget(self.fecha_edit)

        # Contenido
        self.texto_receta = QTextEdit()
        layout.addWidget(QLabel("Contenido de la receta:"))
        layout.addWidget(self.texto_receta)

        # Botón para guardar
        self.btn_guardar = QPushButton("Guardar Receta")
        self.btn_guardar.clicked.connect(self.guardar_receta)
        layout.addWidget(self.btn_guardar)

        layout.addWidget(QLabel("<h2>Historial de Recetas</h2>"))

        # Tabla para mostrar recetas
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Paciente", "Médico", "Contenido"])
        layout.addWidget(self.tabla)

        self.cargar_recetas()

    def guardar_receta(self):
        paciente_id = self.paciente_combo.currentData()
        medico_id = self.medico_combo.currentData()
        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        contenido = self.texto_receta.toPlainText()

        if not contenido.strip():
            QMessageBox.warning(self, "Error", "El contenido de la receta no puede estar vacío.")
            return

        data_manager.create_prescription(paciente_id, medico_id, fecha, contenido)
        QMessageBox.information(self, "Éxito", "Receta guardada correctamente.")
        self.texto_receta.clear()
        self.cargar_recetas()

    def cargar_recetas(self):
        recetas = data_manager.get_all_prescriptions()
        self.tabla.setRowCount(len(recetas))
        for row, r in enumerate(recetas):
            self.tabla.setItem(row, 0, QTableWidgetItem(r["fecha"]))
            self.tabla.setItem(row, 1, QTableWidgetItem(r["paciente"]))
            self.tabla.setItem(row, 2, QTableWidgetItem(r["medico"]))
            self.tabla.setItem(row, 3, QTableWidgetItem(r["contenido"]))
        self.tabla.resizeColumnsToContents()
