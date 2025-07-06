# reminder_service.py
import schedule
import time
from datetime import datetime, timedelta
import sqlite3
import json
import database

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_FLOW_SID
from twilio.rest import Client

class ReminderWorker:
    def __init__(self, shutdown_event):
        self.shutdown_event = shutdown_event
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ Worker de Recordatorios (Plantilla Estática) inicializado.")

    def _get_appointments_for_reminder(self):
        conn = database.conectar_db()
        now = datetime.now()
        reminder_window_end = now + timedelta(hours=3, minutes=10)
        
        query = """
        SELECT c.id, c.fecha_hora, 
               p.nombre || ' ' || p.apellidos as nombre_paciente,
               p.telefono as telefono_paciente,
               m.nombre_completo as nombre_medico
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        JOIN medicos m ON c.medico_id = m.id
        WHERE c.estado = 'Programada' 
          AND c.recordatorio_enviado = 0 
          AND datetime(c.fecha_hora) BETWEEN ? AND ?
        """
        citas = conn.execute(query, (now.strftime('%Y-%m-%d %H:%M:%S'), reminder_window_end.strftime('%Y-%m-%d %H:%M:%S'))).fetchall()
        conn.close()
        
        citas_a_llamar = [c for c in citas if (datetime.strptime(c['fecha_hora'], '%Y-%m-%d %H:%M:%S') - now) <= timedelta(hours=3)]
        return citas_a_llamar

    def _generate_reminder_message(self, nombre_paciente, fecha_hora_cita, nombre_medico):
        hora_cita = datetime.strptime(fecha_hora_cita, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
        return f"Hola {nombre_paciente}. Le hablamos de la clínica GesClínica para recordarle su cita de hoy a las {hora_cita} con el doctor {nombre_medico}. Gracias."

    def _trigger_reminder_call(self, patient_phone, reminder_message):
        try:
            params = json.dumps({"reminder_message": reminder_message})
            execution = self.twilio_client.studio.v2.flows(TWILIO_FLOW_SID).executions.create(
                to=patient_phone, from_=TWILIO_PHONE_NUMBER, parameters=params
            )
            print(f"📞 Flow de Twilio Studio disparado para {patient_phone}. SID: {execution.sid}")
            return True
        except Exception as e:
            print(f"❌ Error al disparar el Flow de Twilio Studio para {patient_phone}: {e}")
            return False

    def job(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Buscando citas para recordar...")
        citas = self._get_appointments_for_reminder()
        
        if not citas:
            print("No hay citas pendientes de recordatorio en la próxima ventana.")
            return
            
        for cita in citas:
            if not cita['telefono_paciente']:
                print(f"  ⚠️  Saltando cita ID: {cita['id']} - no tiene número de teléfono.")
                continue

            print(f"  -> Procesando cita ID: {cita['id']} para {cita['nombre_paciente']}")
            mensaje = self._generate_reminder_message(cita['nombre_paciente'], cita['fecha_hora'], cita['nombre_medico'])
            
            if self._trigger_reminder_call(cita['telefono_paciente'], mensaje):
                database.marcar_recordatorio_enviado(cita['id'])
                print(f"  ✅ Cita ID: {cita['id']} marcada como recordada.")

    def run(self):
        print("🚀 Servicio de recordatorios iniciado. Buscando citas cada 5 minutos.")
        schedule.every(5).minutes.do(self.job)
        self.job()
        while not self.shutdown_event.is_set():
            schedule.run_pending()
            time.sleep(1)
        print("🛑 Servicio de recordatorios detenido.")