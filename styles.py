# styles.py
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

def apply_shadow_effect(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(5)
    shadow.setColor(QColor(0, 0, 0, 60))
    widget.setGraphicsEffect(shadow)

GLOBAL_STYLESHEET = """
/* Fuentes y Colores Base */
QWidget {
    font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #2c3e50; /* Midnight Blue */
}
QMainWindow, QDialog {
    background-color: #ecf0f1; /* Clouds */
}

/* Campos de Entrada */
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit {
    padding: 10px;
    border: 1px solid #bdc3c7; /* Silver */
    border-radius: 8px;
    background-color: #ffffff;
    font-size: 15px;
    selection-background-color: #3498db; /* Peter River */
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus {
    border: 2px solid #3498db; /* Peter River */
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 1px;
    border-left-color: #bdc3c7;
    border-left-style: solid;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}
QComboBox::down-arrow {
    image: url(icons/down_arrow.png); /* Necesitarás este icono */
}

/* Botones */
QPushButton {
    background-color: #3498db; /* Peter River */
    color: white;
    font-weight: bold;
    font-size: 15px;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    min-width: 120px;
}
QPushButton:hover {
    background-color: #2980b9; /* Belize Hole */
}
QPushButton:pressed {
    background-color: #1f618d;
}

/* Tablas */
QTableWidget {
    border: none;
    gridline-color: #e0e0e0;
    background-color: white;
    border-radius: 8px;
    font-size: 14px;
}
QHeaderView::section {
    background-color: #34495e; /* Wet Asphalt */
    color: white;
    padding: 12px;
    border: none;
    font-size: 15px;
    font-weight: bold;
}
QTableWidget::item {
    padding: 10px;
}
QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}
QTableWidget QComboBox {
    padding: 2px;
    border-radius: 4px;
}

/* Contenedores y Etiquetas */
QGroupBox {
    font-weight: bold;
    font-size: 16px;
    border: 1px solid #bdc3c7;
    border-radius: 8px;
    margin-top: 10px;
    background-color: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    left: 10px;
}
QLabel {
    font-size: 14px;
}
"""