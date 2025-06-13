# main.py
import sys
from PySide6.QtWidgets import QApplication

import database
from styles import GLOBAL_STYLESHEET
from ui_components.login_window import VentanaLogin

if __name__ == "__main__":
    # 1. Asegurarse de que las tablas de la base de datos existan
    database.crear_tablas()

    # 2. Crear la aplicación
    app = QApplication(sys.argv)
    
    # 3. Aplicar los estilos globales
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    # 4. Iniciar la ventana de login
    login_window = VentanaLogin()
    login_window.show()
    
    # 5. Ejecutar el bucle de eventos de la aplicación
    sys.exit(app.exec())