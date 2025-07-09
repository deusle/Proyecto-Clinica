# pdf_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from config import CLINICA_INFO

def generate_invoice_pdf(cita_info):
    """
    Genera un archivo PDF para la boleta de una cita.
    cita_info es un diccionario con todos los datos necesarios.
    """
    # Crear un subdirectorio para las boletas si no existe
    output_dir = "boletas_generadas"
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre del archivo PDF
    file_name = f"B001-{cita_info['id']}.pdf"
    file_path = os.path.join(output_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # --- ENCABEZADO ---
    try:
        c.drawImage(CLINICA_INFO["logo_path"], 1 * inch, height - 1.5 * inch, width=1.5*inch, height=1.5*inch, preserveAspectRatio=True)
    except:
        c.drawString(1 * inch, height - 1 * inch, "Logo no encontrado")

    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width - 1 * inch, height - 1 * inch, CLINICA_INFO["nombre"])
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 1 * inch, height - 1.2 * inch, f"RUC: {CLINICA_INFO['ruc']}")
    c.drawRightString(width - 1 * inch, height - 1.4 * inch, CLINICA_INFO["direccion"])
    c.drawRightString(width - 1 * inch, height - 1.6 * inch, f"Tel: {CLINICA_INFO['telefono']} | Email: {CLINICA_INFO['email']}")

    c.setStrokeColorRGB(0.1, 0.5, 0.8)
    c.line(1 * inch, height - 2 * inch, width - 1 * inch, height - 2 * inch)

    # --- TÍTULO Y DATOS DE LA BOLETA ---
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 2.5 * inch, "BOLETA DE VENTA ELECTRÓNICA")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 2.7 * inch, f"B001 - {cita_info['id']:08d}")

    # --- DATOS DEL CLIENTE ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1 * inch, height - 3.5 * inch, "CLIENTE:")
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, height - 3.7 * inch, f"Nombre: {cita_info['paciente_nombre']}")
    c.drawString(1 * inch, height - 3.9 * inch, f"DNI: {cita_info['paciente_dni']}")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 1 * inch, height - 3.5 * inch, "FECHA DE EMISIÓN:")
    c.setFont("Helvetica", 11)
    fecha_emision = datetime.now().strftime("%d/%m/%Y")
    c.drawRightString(width - 1 * inch, height - 3.7 * inch, fecha_emision)

    # --- TABLA DE DETALLES ---
    data = [
        ["CANT.", "DESCRIPCIÓN", "P. UNIT.", "TOTAL"],
        ["1", f"Consulta Médica - {cita_info['medico_especialidad']}\nAtendido por: Dr(a). {cita_info['medico_nombre']}", f"S/ {cita_info['monto_pagado']:.2f}", f"S/ {cita_info['monto_pagado']:.2f}"]
    ]
    
    table = Table(data, colWidths=[0.5*inch, 4.5*inch, 1*inch, 1*inch])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#34495e")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    table.setStyle(style)
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 1 * inch, height - 5.5 * inch)
    
    # --- TOTALES ---
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 2.2 * inch, height - 6 * inch, "TOTAL A PAGAR:")
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 1 * inch, height - 6 * inch, f"S/ {cita_info['monto_pagado']:.2f}")

    # --- PIE DE PÁGINA ---
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 1 * inch, "Gracias por su preferencia.")
    
    c.save()
    return file_path