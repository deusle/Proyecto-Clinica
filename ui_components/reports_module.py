# ui_components/reports_module.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDateEdit, 
                               QGroupBox, QGridLayout, QTextEdit, QMessageBox, QApplication)
from PySide6.QtCharts import (QChartView, QChart, QPieSeries, QBarSeries, QBarSet, 
                              QLineSeries, QValueAxis, QBarCategoryAxis, QDateTimeAxis)
from PySide6.QtGui import QPainter, QFont, QIcon
from PySide6.QtCore import QDate, Qt, QPointF, QDateTime

import data_manager
from styles import apply_shadow_effect
from datetime import datetime

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
        self.title_label.setStyleSheet("color: #7f8c8d;")
        self.value_label = QLabel("0")
        self.value_label.setFont(QFont("Roboto", 36, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.title_label, 0, Qt.AlignCenter)
        layout.addWidget(self.value_label, 0, Qt.AlignCenter)
    def set_value(self, value):
        self.value_label.setText(value)

class VentanaGestionReportes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Módulo de Reportes y Analíticas Avanzadas"); self.setGeometry(100, 100, 1400, 900)
        
        # Almacenamiento de datos para la IA
        self.current_report_data = {}

        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(20)

        # -- Panel de Filtros y Acciones --
        filter_group = QGroupBox("Filtros y Acciones")
        filter_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(calendarPopup=True, date=QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        btn_generate = QPushButton(QIcon("icons/reports.png"), " Generar Reporte")
        btn_generate.clicked.connect(self.actualizar_reporte)
        self.btn_generate_ai = QPushButton(QIcon("icons/ai.png"), " Generar Análisis con IA")
        self.btn_generate_ai.clicked.connect(self.generar_analisis_ia)
        self.btn_generate_ai.setEnabled(False) # Deshabilitado hasta que se genere un reporte

        filter_layout.addWidget(QLabel("Desde:")); filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("Hasta:")); filter_layout.addWidget(self.end_date_edit)
        filter_layout.addStretch(); filter_layout.addWidget(btn_generate); filter_layout.addWidget(self.btn_generate_ai)
        filter_group.setLayout(filter_layout)
        
        main_layout.addWidget(filter_group)

        # -- Layout Principal para KPIs, Gráficos y Análisis IA --
        content_layout = QGridLayout()
        content_layout.setColumnStretch(0, 2) # Columna de gráficos más ancha
        content_layout.setColumnStretch(1, 1) # Columna de IA más estrecha

        # -- Panel de KPIs --
        kpi_layout = QHBoxLayout(); kpi_layout.setSpacing(20)
        self.kpi_ingresos = KPIWidget("INGRESOS TOTALES")
        self.kpi_citas = KPIWidget("CITAS ATENDIDAS")
        kpi_layout.addWidget(self.kpi_ingresos)
        kpi_layout.addWidget(self.kpi_citas)
        
        # -- Panel de Gráficos (a la izquierda) --
        charts_group = QGroupBox("Visualización de Datos")
        charts_layout = QGridLayout()
        self.chart_view_specialty = self.crear_chart_view("Rendimiento por Especialidad")
        self.chart_view_trend = self.crear_chart_view("Tendencia de Citas Diarias")
        charts_layout.addWidget(self.chart_view_specialty, 0, 0)
        charts_layout.addWidget(self.chart_view_trend, 1, 0)
        charts_group.setLayout(charts_layout)

        # -- Panel de Análisis IA (a la derecha) --
        ai_group = QGroupBox("Análisis y Recomendaciones (IA)")
        ai_layout = QVBoxLayout()
        self.ai_summary_text = QTextEdit()
        self.ai_summary_text.setReadOnly(True)
        self.ai_summary_text.setPlaceholderText("Haga clic en 'Generar Análisis con IA' después de generar un reporte para ver el resumen aquí.")
        ai_layout.addWidget(self.ai_summary_text)
        ai_group.setLayout(ai_layout)

        # -- Añadir widgets al layout principal --
        main_layout.addLayout(kpi_layout)
        content_layout.addWidget(charts_group, 0, 0)
        content_layout.addWidget(ai_group, 0, 1)
        main_layout.addLayout(content_layout)
        
        self.actualizar_reporte()

    def crear_chart_view(self, title):
        chart = QChart(); chart.setTitle(title); chart.setTitleFont(QFont("Roboto", 16, QFont.Weight.Bold))
        chart.setAnimationOptions(QChart.AllAnimations); chart.legend().setAlignment(Qt.AlignBottom)
        chart_view = QChartView(chart); chart_view.setRenderHint(QPainter.Antialiasing)
        apply_shadow_effect(chart_view); chart_view.setStyleSheet("background-color: white; border-radius: 8px;")
        return chart_view

    def actualizar_reporte(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.ai_summary_text.clear()
        self.btn_generate_ai.setEnabled(False)

        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Obtener y actualizar KPIs
        total_ingresos = data_manager.get_total_revenue(start_date, end_date)
        total_citas = data_manager.get_total_attended_appointments(start_date, end_date)
        self.kpi_ingresos.set_value(f"S/ {total_ingresos:.2f}")
        self.kpi_citas.set_value(str(total_citas))
        
        # Obtener datos para gráficos avanzados
        specialty_data = data_manager.get_performance_by_specialty(start_date, end_date)
        trend_data = data_manager.get_appointments_per_day(start_date, end_date)
        
        # Guardar datos para la IA
        self.current_report_data = {
            "start_date": start_date,
            "end_date": end_date,
            "kpis": {"revenue": total_ingresos, "appointments": total_citas},
            "specialty_data": specialty_data
        }

        # Actualizar Gráficos
        self.actualizar_grafico_especialidades(specialty_data)
        self.actualizar_grafico_tendencia(trend_data)
        
        self.btn_generate_ai.setEnabled(True)
        QApplication.restoreOverrideCursor()
        QMessageBox.information(self, "Reporte Generado", "El reporte se ha actualizado con los datos del período seleccionado.")

    def actualizar_grafico_especialidades(self, data):
        chart = self.chart_view_specialty.chart()
        chart.removeAllSeries()
        
        if not data:
            chart.setTitle("Rendimiento por Especialidad (No hay datos)")
            return
        
        chart.setTitle("Rendimiento por Especialidad")
        
        set_ingresos = QBarSet("Ingresos (S/)")
        set_citas = QBarSet("N° Citas")
        
        categories = []
        for row in data:
            set_ingresos.append(row['ingresos_totales'])
            set_citas.append(row['numero_citas'])
            categories.append(row['especialidad'])

        series = QBarSeries()
        series.append(set_ingresos)
        series.append(set_citas)
        chart.addSeries(series)
        
        axis_x = QBarCategoryAxis(); axis_x.append(categories)
        chart.setAxisX(axis_x, series)
        axis_y = QValueAxis(); axis_y.setLabelFormat("S/ %.0f")
        chart.setAxisY(axis_y, series)

    def actualizar_grafico_tendencia(self, data):
        chart = self.chart_view_trend.chart()
        chart.removeAllSeries()

        if not data:
            chart.setTitle("Tendencia de Citas Diarias (No hay datos)")
            return

        chart.setTitle("Tendencia de Citas Diarias")

        series = QLineSeries()
        series.setName("Citas Atendidas")
        
        for row in data:
            fecha_dt = datetime.strptime(row['fecha'], '%Y-%m-%d')
            timestamp = fecha_dt.timestamp() * 1000
            series.append(QPointF(timestamp, row['numero_citas']))
        
        chart.addSeries(series)

        axis_x = QDateTimeAxis(); axis_x.setFormat("dd MMM yyyy"); axis_x.setTitleText("Fecha")
        chart.setAxisX(axis_x, series)
        axis_y = QValueAxis(); axis_y.setLabelFormat("%i"); axis_y.setTitleText("N° de Citas")
        chart.setAxisY(axis_y, series)
        axis_y.setMin(0)

    def generar_analisis_ia(self):
        if not self.current_report_data or not self.current_report_data.get('kpis'):
            QMessageBox.warning(self, "Datos Insuficientes", "Primero debe generar un reporte para poder analizarlo.")
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.ai_summary_text.setText("Generando análisis con IA, por favor espere...")

        data = self.current_report_data
        informe = data_manager.generate_report_summary_with_ai(
            data['start_date'],
            data['end_date'],
            data['kpis'],
            data['specialty_data']
        )
        
        if informe.startswith("ERROR:"):
            QMessageBox.critical(self, "Error de IA", informe)
            self.ai_summary_text.setText(f"<b><font color='red'>{informe}</font></b>")
        else:
            self.ai_summary_text.setMarkdown(informe)
        
        QApplication.restoreOverrideCursor()