# ui_components/reports_module.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDateEdit, QGroupBox, QGridLayout
from PySide6.QtCharts import QChartView, QChart, QPieSeries
from PySide6.QtGui import QPainter, QFont
from PySide6.QtCore import QDate, Qt

import data_manager
from styles import apply_shadow_effect

# NUEVO: Un widget reutilizable para mostrar un KPI
class KPIWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setMinimumHeight(120)
        self.setStyleSheet("background-color: white; border-radius: 8px;")
        apply_shadow_effect(self)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #7f8c8d;") # Asbestos
        
        self.value_label = QLabel("0")
        self.value_label.setFont(QFont("Roboto", 36, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #2c3e50;") # Midnight Blue
        
        layout.addWidget(self.title_label, 0, Qt.AlignCenter)
        layout.addWidget(self.value_label, 0, Qt.AlignCenter)
        
    def set_value(self, value):
        self.value_label.setText(value)


class VentanaGestionReportes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Módulo de Reportes y Analíticas"); self.setGeometry(150, 150, 1100, 800)
        
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(20)

        filter_group = QGroupBox("Seleccionar Rango de Fechas")
        filter_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(calendarPopup=True, date=QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        btn_generate = QPushButton("Generar Reporte")
        btn_generate.clicked.connect(self.actualizar_reporte)
        filter_layout.addWidget(QLabel("Desde:")); filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("Hasta:")); filter_layout.addWidget(self.end_date_edit)
        filter_layout.addStretch(); filter_layout.addWidget(btn_generate)
        filter_group.setLayout(filter_layout)

        # --- NUEVO: Layout para los KPIs ---
        kpi_layout = QHBoxLayout(); kpi_layout.setSpacing(20)
        self.kpi_ingresos = KPIWidget("INGRESOS TOTALES")
        self.kpi_citas = KPIWidget("CITAS ATENDIDAS")
        kpi_layout.addWidget(self.kpi_ingresos)
        kpi_layout.addWidget(self.kpi_citas)

        charts_layout = QGridLayout()
        self.chart_view_pagos = self.crear_chart_view("Distribución de Métodos de Pago")
        self.chart_view_seguros = self.crear_chart_view("Uso de Seguros")
        charts_layout.addWidget(self.chart_view_pagos, 0, 0)
        charts_layout.addWidget(self.chart_view_seguros, 0, 1)

        main_layout.addWidget(filter_group)
        main_layout.addLayout(kpi_layout) # Añadido el layout de KPIs
        main_layout.addLayout(charts_layout)
        
        self.actualizar_reporte()

    def crear_chart_view(self, title):
        chart = QChart()
        chart.setTitle(title)
        chart.setTitleFont(QFont("Roboto", 16, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AllAnimations)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        apply_shadow_effect(chart_view)
        chart_view.setStyleSheet("background-color: white; border-radius: 8px;")
        return chart_view

    def actualizar_reporte(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Actualizar KPIs
        total_ingresos = data_manager.get_total_revenue(start_date, end_date)
        total_citas = data_manager.get_total_attended_appointments(start_date, end_date)
        self.kpi_ingresos.set_value(f"S/ {total_ingresos:.2f}")
        self.kpi_citas.set_value(str(total_citas))

        # Actualizar Gráficos
        self.actualizar_grafico_pagos(start_date, end_date)
        self.actualizar_grafico_seguros(start_date, end_date)

    def actualizar_grafico_pagos(self, start_date, end_date):
        data = data_manager.get_payment_method_distribution(start_date, end_date)
        series = QPieSeries()
        for row in data:
            if row['count'] > 0: series.append(str(row['metodo_pago']), row['count'])
        
        for slice in series.slices():
            slice.setLabel(f"{slice.label()} ({slice.percentage()*100:.1f}%)")
            slice.setLabelVisible(True)
            slice.setLabelFont(QFont("Roboto", 10, QFont.Weight.Bold))

        self.chart_view_pagos.chart().removeAllSeries()
        self.chart_view_pagos.chart().addSeries(series)
    
    def actualizar_grafico_seguros(self, start_date, end_date):
        data = data_manager.get_insurance_usage_distribution(start_date, end_date)
        series = QPieSeries()
        for row in data:
            if row['count'] > 0: series.append(str(row['uso_seguro']), row['count'])

        for slice in series.slices():
            slice.setLabel(f"{slice.label()} ({slice.percentage()*100:.1f}%)")
            slice.setLabelVisible(True)
            slice.setLabelFont(QFont("Roboto", 10, QFont.Weight.Bold))

        self.chart_view_seguros.chart().removeAllSeries()
        self.chart_view_seguros.chart().addSeries(series)