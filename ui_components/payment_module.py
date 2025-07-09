# ui_components/payment_module.py
import random
import os
import webbrowser
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QFormLayout, QComboBox, QDialogButtonBox, QHeaderView, QTabWidget
from PySide6.QtGui import QIcon

import data_manager
import pdf_generator # NUEVA IMPORTACIÓN
from config import SEGUROS

class DialogoPago(QDialog):
    # ... (Esta clase no cambia)
    def __init__(self, cita_id, parent=None):
        super().__init__(parent); self.cita_id = cita_id; self.setWindowTitle(f"Registrar Pago para Cita N° {self.cita_id}"); self.layout = QFormLayout(self)
        self.monto = QLineEdit(); self.monto.setPlaceholderText("Ej: 150.00")
        self.metodo_pago = QComboBox(); self.metodo_pago.addItems(["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", "Transferencia"])
        self.aseguradora = QComboBox(); self.aseguradora.addItems(SEGUROS)
        self.layout.addRow("<b>Monto (S/):</b>", self.monto); self.layout.addRow("<b>Método de Pago:</b>", self.metodo_pago); self.layout.addRow("<b>Aseguradora (si aplica):</b>", self.aseguradora)
        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); self.botones.accepted.connect(self.accept); self.botones.rejected.connect(self.reject); self.layout.addWidget(self.botones)
    def get_data(self):
        try: monto = float(self.monto.text())
        except ValueError: QMessageBox.critical(self, "Error de Datos", "El monto debe ser un número válido."); return None
        return monto, self.metodo_pago.currentText(), self.aseguradora.currentText()

class VentanaGestionPagos(QWidget):
    # --- FUNCIÓN registrar_pago_seleccionado MODIFICADA ---
    def registrar_pago_seleccionado(self):
        row = self.tabla_pendientes.currentRow()
        if row < 0: return QMessageBox.warning(self, "Atención", "Seleccione una cita para registrar su pago.")
        cita_id = int(self.tabla_pendientes.item(row, 0).text())
        dialogo = DialogoPago(cita_id, self)
        if dialogo.exec():
            datos = dialogo.get_data()
            if datos:
                # 1. Registrar en la BD
                data_manager.register_payment(cita_id, datos)
                
                # 2. Recopilar datos para la boleta
                invoice_details = data_manager.get_invoice_details(cita_id)
                
                # 3. Generar el PDF
                pdf_path = pdf_generator.generate_invoice_pdf(invoice_details)
                
                # 4. Mostrar mensaje de éxito con opción de abrir el PDF
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setText("¡Pago registrado y boleta generada con éxito!")
                msg_box.setInformativeText(f"La boleta ha sido guardada en:\n{os.path.abspath(pdf_path)}")
                abrir_btn = msg_box.addButton("Abrir Boleta (PDF)", QMessageBox.ActionRole)
                msg_box.addButton(QMessageBox.Ok)
                
                msg_box.exec()
                
                if msg_box.clickedButton() == abrir_btn:
                    webbrowser.open(os.path.abspath(pdf_path))

                self.cargar_citas_programadas()
                if self.tabs.currentIndex() == 1: self.cargar_historial_pagos()

    # --- El resto de la clase no cambia ---
    def __init__(self):
        super().__init__(); self.setWindowTitle("Módulo de Pagos"); self.setGeometry(150, 150, 900, 600)
        main_layout = QVBoxLayout(self); self.tabs = QTabWidget(); main_layout.addWidget(self.tabs)
        self.pagos_pendientes_tab = QWidget(); layout_pendientes = QVBoxLayout(self.pagos_pendientes_tab)
        controles = QHBoxLayout(); self.filtro = QLineEdit(placeholderText="Buscar por paciente o médico..."); self.filtro.textChanged.connect(self.cargar_citas_programadas)
        btn_pagar = QPushButton(QIcon("icons/payment.png"), " Registrar Pago"); btn_pagar.clicked.connect(self.registrar_pago_seleccionado)
        controles.addWidget(QLabel("<b>Buscar Cita:</b>")); controles.addWidget(self.filtro); controles.addStretch(); controles.addWidget(btn_pagar)
        self.tabla_pendientes = QTableWidget(columnCount=4, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_pendientes.setHorizontalHeaderLabels(["ID Cita", "Paciente", "Médico", "Fecha y Hora"]); self.tabla_pendientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_pendientes.addLayout(controles); layout_pendientes.addWidget(self.tabla_pendientes)
        self.historial_pagos_tab = QWidget(); layout_historial = QVBoxLayout(self.historial_pagos_tab)
        self.tabla_historial = QTableWidget(columnCount=7, editTriggers=QTableWidget.NoEditTriggers, selectionBehavior=QTableWidget.SelectRows, alternatingRowColors=True)
        self.tabla_historial.setHorizontalHeaderLabels(["ID Cita", "Paciente", "Médico", "Fecha", "Monto (S/)", "Método Pago", "Aseguradora"]); self.tabla_historial.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_historial.addWidget(self.tabla_historial)
        self.tabs.addTab(self.pagos_pendientes_tab, "Pagos Pendientes"); self.tabs.addTab(self.historial_pagos_tab, "Historial de Pagos")
        self.tabs.currentChanged.connect(self.actualizar_pestanas); self.cargar_citas_programadas()
    def actualizar_pestanas(self):
        if self.tabs.currentIndex() == 0: self.cargar_citas_programadas()
        else: self.cargar_historial_pagos()
    def cargar_citas_programadas(self):
        citas = data_manager.get_scheduled_appointments(self.filtro.text())
        self.tabla_pendientes.setRowCount(len(citas))
        for r, cita in enumerate(citas):
            for c, val in enumerate(cita): self.tabla_pendientes.setItem(r, c, QTableWidgetItem(str(val)))
    def cargar_historial_pagos(self):
        pagos = data_manager.get_payment_history()
        self.tabla_historial.setRowCount(len(pagos))
        for r, pago in enumerate(pagos):
            for c, val in enumerate(pago):
                if c == 4: val = f"S/ {val:.2f}"
                self.tabla_historial.setItem(r, c, QTableWidgetItem(str(val) if val else "-"))