from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from datetime import datetime, timedelta
import random
import time as time_lib
from schemas import ReservaCreate, ReservaResponse

app = FastAPI(
    title="API de Reservas y Recordatorios - BELLEZA PRO",
    version="1.0.0"
)

# Base de datos simulada en memoria
db_reservas = {}

def enviar_recordatorio_whatsapp_sms(nombre: str, telefono: str, fecha: str, hora: str):
    """
    Función simulada en segundo plano que enviará la alerta.
    Aquí conectarás proveedores como Twilio, UltraMsg o GreenAPI.
    """
    print(f"[RECORDATORIO CONFIGURADO] Programado para {nombre} al número {telefono}.")
    # Ejemplo de lógica de espera real o integración con Celery / Cron Jobs:
    # time_lib.sleep(segundos_restantes)
    # enviar_mensaje()

@app.post("/api/v1/reservas", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def crear_reserva(reserva: ReservaCreate, background_tasks: BackgroundTasks):
    # 1. Generar número de reserva único de 5 dígitos
    id_unico = random.randint(10000, 99999)
    while id_unico in db_reservas:
        id_unico = random.randint(10000, 99999)

    # 2. Estructurar el registro completo
    nueva_reserva = {
        "id_reserva": id_unico,
        "nombre_cliente": reserva.nombre_cliente,
        "telefono": reserva.telefono,
        "fecha": reserva.fecha,
        "hora": reserva.hora,
        "recordatorio": reserva.recordatorio,
        "avisar_media_hora_antes": reserva.avisar_media_hora_antes,
        "fecha_creacion": datetime.now()
    }
    
    # Guardar en base de datos
    db_reservas[id_unico] = nueva_reserva

    # 3. Lógica para el aviso de media hora antes
    if reserva.recordatorio and reserva.avisar_media_hora_antes:
        # Combinar fecha y hora de la cita
        fecha_cita = datetime.combine(reserva.fecha, reserva.hora)
        fecha_alerta = fecha_cita - timedelta(minutes=30)
        ahora = datetime.now()

        if fecha_alerta > ahora:
            # Añadir a la cola de tareas en segundo plano
            background_tasks.add_task(
                enviar_recordatorio_whatsapp_sms,
                nombre=reserva.nombre_cliente,
                telefono=reserva.telefono,
                fecha=str(reserva.fecha),
                hora=str(reserva.hora)
            )

    return nueva_reserva

@app.get("/api/v1/reservas/{id_reserva}", response_model=ReservaResponse)
async def obtener_reserva(id_reserva: int):
    if id_reserva not in db_reservas:
        raise HTTPException(status_code=404, detail="Número de reserva no encontrado")
    return db_reservas[id_reserva]
