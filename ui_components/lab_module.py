# ui_components/lab_module.py
import json
from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QPushButton, QLabel, QMessageBox, QFormLayout, 
                               QDateEdit, QComboBox, QTextEdit, QDialogButtonBox, QHeaderView, 
                               QLineEdit, QFileDialog, QApplication)
from PySide6.QtGui import QCursor
from PySide6.QtCore import QDate, Qt

import data_manager

class DialogoNuevoAnalisis(QDialog):
    def __init__(self, paciente_id, parent=None):
        super().__init__(parent)
        self.paciente_id = paciente_id
        self.raw_ia_prediction = None # Para almacenar el dict de la IA

        self.setWindowTitle("Añadir Nuevo Análisis de Laboratorio")
        self.setMinimumWidth(550)
        
        self.layout = QFormLayout(self)
        
        self.tipo_analisis = QComboBox()
        self.tipo_analisis.addItems(["Análisis de Sangre", "Tomografía (CT)", "Rayos-X", "Análisis de Orina", "Otro"])
        self.fecha_analisis = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.resultados_texto = QTextEdit()
        self.resultados_texto.setPlaceholderText("Ingrese aquí los resultados, resumen o notas del análisis...")
        
        # Layout para seleccionar archivo
        file_layout = QHBoxLayout()
        self.ruta_archivo = QLineEdit()
        self.ruta_archivo.setPlaceholderText("Seleccione un archivo (PDF, JPG, PNG, etc.)")
        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(40)
        btn_browse.clicked.connect(self.seleccionar_archivo)
        file_layout.addWidget(self.ruta_archivo)
        file_layout.addWidget(btn_browse)

        self.btn_analizar_ia = QPushButton("Analizar con IA")
        self.btn_analizar_ia.clicked.connect(self.analizar_con_ia)
        self.btn_analizar_ia.setVisible(False) # Oculto por defecto

        self.layout.addRow("<b>Tipo de Análisis:</b>", self.tipo_analisis)
        self.layout.addRow("<b>Fecha:</b>", self.fecha_analisis)
        self.layout.addRow("<b>Archivo Adjunto:</b>", file_layout)
        self.layout.addRow(self.btn_analizar_ia)
        self.layout.addRow("<b>Resultados / Notas:</b>", self.resultados_texto)

        self.botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)
        self.layout.addWidget(self.botones)

        self.tipo_analisis.currentTextChanged.connect(self._on_type_changed)
        self._on_type_changed(self.tipo_analisis.currentText())

    def _on_type_changed(self, text):
        """Muestra u oculta el botón de IA según el tipo de análisis."""
        is_ct_scan = (text == "Tomografía (CT)")
        self.btn_analizar_ia.setVisible(is_ct_scan)

    def seleccionar_archivo(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Todos los Archivos (*);;Imágenes (*.png *.jpg);;Documentos (*.pdf)")
        if filepath:
            self.ruta_archivo.setText(filepath)

    def analizar_con_ia(self):
        image_path = self.ruta_archivo.text()
        if not image_path:
            QMessageBox.warning(self, "Archivo no encontrado", "Por favor, seleccione un archivo de imagen para analizar.")
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.resultados_texto.setText("Analizando imagen con el modelo de IA, por favor espere...")
        
        raw_prediction, formatted_text = data_manager.analyze_ct_scan_image(image_path)
        
        QApplication.restoreOverrideCursor()

        if "error" in raw_prediction:
            QMessageBox.critical(self, "Error de Análisis", raw_prediction["error"])
            self.resultados_texto.setText(f"Error al analizar: {raw_prediction['error']}")
            self.raw_ia_prediction = None
        else:
            self.resultados_texto.setText(formatted_text)
            self.raw_ia_prediction = raw_prediction # Guardar el resultado crudo

    def get_data(self):
        return (
            self.paciente_id,
            self.tipo_analisis.currentText(),
            self.fecha_analisis.date().toString("yyyy-MM-dd"),
            self.resultados_texto.toPlainText(),
            self.ruta_archivo.text(),
            self.raw_ia_prediction
        )

class VentanaGestionAnalisis(QDialog):
    def __init__(self, paciente_id, paciente_nombre, parent=None):
        super().__init__(parent)
        self.paciente_id = paciente_id
        
        self.setWindowTitle(f"Análisis de Laboratorio de: {paciente_nombre}")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        
        controles_layout = QHBoxLayout()
        btn_agregar = QPushButton("Añadir Análisis")
        btn_agregar.clicked.connect(self.agregar_analisis)
        btn_eliminar = QPushButton("Eliminar Análisis")
        btn_eliminar.clicked.connect(self.eliminar_analisis)
        btn_eliminar.setStyleSheet("background-color: #e74c3c;")
        
        controles_layout.addStretch()
        controles_layout.addWidget(btn_agregar)
        controles_layout.addWidget(btn_eliminar)

        self.tabla_analisis = QTableWidget(columnCount=4, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows)
        self.tabla_analisis.setHorizontalHeaderLabels(["ID", "Fecha", "Tipo de Análisis", "Resultados/Resumen"])
        header = self.tabla_analisis.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.tabla_analisis.doubleClicked.connect(self.ver_detalle_analisis)

        layout.addLayout(controles_layout)
        layout.addWidget(self.tabla_analisis)
        
        self.cargar_analisis()

    def cargar_analisis(self):
        analisis = data_manager.get_lab_tests_for_patient(self.paciente_id)
        self.tabla_analisis.setRowCount(len(analisis))
        for r, item in enumerate(analisis):
            self.tabla_analisis.setItem(r, 0, QTableWidgetItem(str(item['id'])))
            self.tabla_analisis.setItem(r, 1, QTableWidgetItem(item['fecha_analisis']))
            self.tabla_analisis.setItem(r, 2, QTableWidgetItem(item['tipo_analisis']))
            
            resumen = item['resultados_texto']
            if resumen and len(resumen) > 100:
                resumen = resumen[:100] + "..."
            self.tabla_analisis.setItem(r, 3, QTableWidgetItem(resumen))

    def agregar_analisis(self):
        dialogo = DialogoNuevoAnalisis(self.paciente_id, self)
        if dialogo.exec():
            datos = dialogo.get_data()
            data_manager.add_lab_test(*datos)
            QMessageBox.information(self, "Éxito", "Análisis guardado correctamente.")
            self.cargar_analisis()

    def eliminar_analisis(self):
        row = self.tabla_analisis.currentRow()
        if row < 0:
            return QMessageBox.warning(self, "Atención", "Seleccione un análisis para eliminar.")
        
        analisis_id = int(self.tabla_analisis.item(row, 0).text())
        confirm = QMessageBox.question(self, "Confirmar", "¿Está seguro de que desea eliminar este análisis?", QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            data_manager.delete_lab_test(analisis_id)
            QMessageBox.information(self, "Éxito", "Análisis eliminado.")
            self.cargar_analisis()
            
    def ver_detalle_analisis(self, index):
        row = index.row()
        analisis_id = int(self.tabla_analisis.item(row, 0).text())
        
        # Recuperamos el registro completo para tener todos los detalles
        todos_los_analisis = data_manager.get_lab_tests_for_patient(self.paciente_id)
        detalle_completo = next((item for item in todos_los_analisis if item['id'] == analisis_id), None)
        
        if not detalle_completo:
            return

        tipo = detalle_completo['tipo_analisis']
        resultados = detalle_completo['resultados_texto']
        archivo = detalle_completo['ruta_archivo']

        info_text = f"""
        <b>Tipo de Análisis:</b> {tipo}<br>
        <b>Fecha:</b> {detalle_completo['fecha_analisis']}<br>
        <b>Archivo Adjunto:</b> {archivo or 'Ninguno'}<br><br>
        <hr>
        <b>Resultados:</b><br>
        <pre>{resultados or 'No hay resultados detallados.'}</pre>
        """
        QMessageBox.information(self, f"Detalle del Análisis #{analisis_id}", info_text)