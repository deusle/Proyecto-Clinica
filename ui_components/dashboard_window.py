# ui_components/dashboard_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, QSize

from .patient_module import VentanaGestionPacientes
from .doctor_module import VentanaGestionMedicos
from .appointment_module import VentanaGestionCitas
from .payment_module import VentanaGestionPagos
from styles import apply_shadow_effect

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GesClínica - Panel Principal"); self.setGeometry(100, 100, 800, 600)
        self.ventanas_abiertas = {}
        widget_central = QWidget(); self.setCentralWidget(widget_central)
        layout = QVBoxLayout(widget_central); layout.setContentsMargins(40, 40, 40, 40)
        titulo = QLabel("Panel de Control Principal"); titulo.setAlignment(Qt.AlignCenter); titulo.setStyleSheet("font-size: 32px; font-weight: 600; margin-bottom: 20px; color: #2c3e50;")
        layout.addWidget(titulo)
        menu_layout = QGridLayout(); menu_layout.setSpacing(30); layout.addLayout(menu_layout)
        
        btn_citas = self.crear_boton_menu("Agendar Citas", "icons/appointment.png", self.abrir_gestion_citas)
        btn_pacientes = self.crear_boton_menu("Pacientes", "icons/patient.png", self.abrir_gestion_pacientes)
        btn_medicos = self.crear_boton_menu("Médicos", "icons/doctor.png", self.abrir_gestion_medicos)
        # NUEVO BOTÓN
        btn_pagos = self.crear_boton_menu("Pagos y Boletas", "icons/payment.png", self.abrir_gestion_pagos)
        btn_salir = self.crear_boton_menu("Salir", "icons/exit.png", self.close, es_rojo=True)
        
        menu_layout.addWidget(btn_citas, 0, 0); menu_layout.addWidget(btn_pagos, 0, 1)
        menu_layout.addWidget(btn_pacientes, 1, 0); menu_layout.addWidget(btn_medicos, 1, 1)
        menu_layout.addWidget(btn_salir, 2, 0, 1, 2) # Span across 2 columns

    def crear_boton_menu(self, texto, icon_path, funcion_click, es_rojo=False):
        btn = QPushButton(QIcon(icon_path), f"  {texto}"); btn.setIconSize(QSize(48, 48)); btn.setMinimumHeight(120)
        style = "QPushButton {color: #34495e; font-size: 18px; border-radius: 10px; background-color: #ffffff; text-align: center; padding: 10px;} QPushButton:hover {background-color: #ecf0f1;}"
        if es_rojo: style = "QPushButton {color: #e74c3c; font-weight: bold; background-color: #f5b7b1; border: 2px solid #e74c3c;} QPushButton:hover {background-color: #f1948a;}"
        btn.setStyleSheet(style); apply_shadow_effect(btn); btn.clicked.connect(funcion_click)
        return btn
    
    def abrir_ventana(self, nombre_ventana, clase_ventana):
        if nombre_ventana not in self.ventanas_abiertas or not self.ventanas_abiertas[nombre_ventana].isVisible():
            self.ventanas_abiertas[nombre_ventana] = clase_ventana(); self.ventanas_abiertas[nombre_ventana].show()
        else: self.ventanas_abiertas[nombre_ventana].activateWindow(); self.ventanas_abiertas[nombre_ventana].raise_()

    def abrir_gestion_citas(self): self.abrir_ventana("citas", VentanaGestionCitas)
    def abrir_gestion_pacientes(self): self.abrir_ventana("pacientes", VentanaGestionPacientes)
    def abrir_gestion_medicos(self): self.abrir_ventana("medicos", VentanaGestionMedicos)
    def abrir_gestion_pagos(self): self.abrir_ventana("pagos", VentanaGestionPagos)