# ui_components/login_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

import data_manager
from .dashboard_window import Dashboard
from styles import apply_shadow_effect

class VentanaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenido a GesClínica"); self.setFixedSize(450, 550)
        widget_central = QWidget(); self.setCentralWidget(widget_central)
        main_layout = QVBoxLayout(widget_central); main_layout.setAlignment(Qt.AlignCenter); main_layout.setContentsMargins(40, 20, 40, 40)
        
        logo_label = QLabel("GesClínica"); logo_label.setFont(QFont("Roboto", 48, QFont.Weight.Bold)); logo_label.setStyleSheet("color: #2980b9;"); logo_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel("Software de Gestión Médica"); subtitle_label.setFont(QFont("Roboto", 12)); subtitle_label.setStyleSheet("color: #7f8c8d;"); subtitle_label.setAlignment(Qt.AlignCenter)
        
        frame = QFrame(); frame.setStyleSheet("background-color: white; border-radius: 12px;"); apply_shadow_effect(frame)
        form_layout = QFormLayout(frame); form_layout.setContentsMargins(30, 30, 30, 30); form_layout.setVerticalSpacing(20)
        
        self.usuario = QLineEdit("admin"); self.clave = QLineEdit("admin"); self.clave.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow(QLabel("<b>USUARIO</b>"), self.usuario)
        form_layout.addRow(QLabel("<b>CONTRASEÑA</b>"), self.clave)
        
        btn_ingresar = QPushButton("Ingresar"); btn_ingresar.clicked.connect(self.verificar_login)

        main_layout.addWidget(logo_label); main_layout.addWidget(subtitle_label); main_layout.addSpacing(30)
        main_layout.addWidget(frame); main_layout.addSpacing(30); main_layout.addWidget(btn_ingresar)
        
    def verificar_login(self):
        if data_manager.verify_credentials(self.usuario.text(), self.clave.text()):
            self.dashboard = Dashboard(); self.dashboard.show(); self.close()
        else: QMessageBox.warning(self, "Acceso Denegado", "El usuario o la contraseña son incorrectos."); self.clave.clear()