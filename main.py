# main.py
import sys
from PySide6.QtWidgets import QApplication

import database
from styles import GLOBAL_STYLESHEET
from ui_components.login_window import VentanaLogin

if __name__ == "__main__":
    print("Iniciando GesClinica...")

    # Asegurar que las tablas estén creadas
    database.crear_tablas()

    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)

    login_window = VentanaLogin()
    login_window.show()

    sys.exit(app.exec())
