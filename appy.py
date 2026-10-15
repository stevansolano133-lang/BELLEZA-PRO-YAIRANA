
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

import pandas as pd
from datetime import datetime, time
import random

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="BELLEZA-PRO-YAIRANA",
    page_icon="💆‍♀️",
    layout="wide"
)

# 2. INICIALIZACIÓN DE LA BASE DE DATOS (En memoria usando st.session_state)
if "db_reservas" not in st.session_state:
    st.session_state.db_reservas = pd.DataFrame(columns=[
        "Número Reserva", "Cliente", "Teléfono", "Servicio", "Fecha", "Hora", "Recordatorio", "Aviso 30 Min", "Notas"
    ])

# Variables de tiempo de referencia
hoy = datetime.now().date()

# 3. ENCABEZADO PRINCIPAL DE LA APLICACIÓN
st.title("💅 BELLEZA-PRO-YAIRANA")
st.subheader("Sistema Integral de Gestión de Reservas de Cosmetología")
st.markdown("---")

# 4. MENÚ LATERAL DE NAVEGACIÓN
st.sidebar.header("🧭 Panel de Control")
opcion = st.sidebar.radio(
    "Selecciona una acción:",
    ["📋 Ver Agenda y Próximas Reservas", "➕ Agendar Nueva Cita", "📊 Catálogo y Métricas"]
)

# ==========================================
# VISTA 1: VER AGENDA Y PRÓXIMAS RESERVAS
# ==========================================
if opcion == "📋 Ver Agenda y Próximas Reservas":
    st.header("📅 Agenda de Citas")
    
    # KPIs rápidos basados en el DataFrame
    total_citas = len(st.session_state.db_reservas)
    
    col_kpi1, col_kpi2 = st.columns(2)
    col_kpi1.metric("Total de Reservas Históricas", total_citas)
    
    # Filtrar citas futuras o de hoy
    if total_citas > 0:
        df_proximas = st.session_state.db_reservas[
            pd.to_datetime(st.session_state.db_reservas["Fecha"]) >= pd.to_datetime(hoy)
        ]
        col_kpi2.metric("Próximas Citas Activas", len(df_proximas))
    else:
        col_kpi2.metric("Próximas Citas Activas", 0)

    st.markdown("### 🔍 Listado de Próximas Reservas")
    
    if st.session_state.db_reservas.empty:
        st.info("ℹ️ Todavía no hay citas registradas en el sistema. Ve a la sección 'Agendar Nueva Cita' en el menú lateral.")
    else:
        # Mostramos la tabla completa formateada como texto de forma segura para evitar OverflowErrors
        st.dataframe(
            st.session_state.db_reservas.astype(str),
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# VISTA 2: AGENDAR NUEVA CITA
# ==========================================
elif opcion == "➕ Agendar Nueva Cita":
    st.header("📝 Formulario de Reserva Especializado")
    st.write("Completa los datos requeridos para bloquear el espacio en la agenda de cosmetología.")
    
    with st.form("formulario_estetica", clear_on_submit=True):
        
        # --- SECCIÓN 1: DATOS DEL CLIENTE ---
        st.markdown("#### 👤 Datos Básicos")
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre completo de quien reserva *", placeholder="Ej: María Clara Gómez")
        telefono = col2.text_input("Número de Teléfono / WhatsApp *", placeholder="Ej: +57 300 123 4567")
        
        # --- SECCIÓN 2: CATÁLOGO DE SERVICIOS ---
        st.markdown("#### 💆‍♀️ Servicio a Realizar (Catálogo)")
        servicio = st.selectbox(
            "Selecciona el tratamiento solicitado: *",
            [
                "--- Seleccione un servicio del catálogo ---",
                "Depilación de Cejas (Diseño Clásico)",
                "Laminado de Cejas",
                "Extensión de Pestañas",
                "Lifting de Pestañas",
                "Depilación con Cera Facial",
                "Depilación con Cera Corporal",
                "Masaje Corporal Relajante",
                "Masaje Corporal Reductor",
                "Masaje Posquirúrgico / Drenaje",
                "Limpieza Facial Profunda"
            ]
        )
        
        # --- SECCIÓN 3: FECHA Y HORA ---
        st.markdown("#### ⏰ Programación")
        col3, col4 = st.columns(2)
        fecha = col3.date_input("Fecha de la cita", value=hoy)
        hora = col4.time_input("Hora de la cita", value=time(9, 0))
        
        # --- SECCIÓN 4: RECORDATORIOS ---
        st.markdown("#### 🔔 Sistema de Alertas Automáticas")
        col5, col6 = st.columns(2)
        recordatorio = col5.checkbox("Desea recibir recordatorios generales", value=True)
        avisar_media_hora = col6.checkbox("Avisar exactamente media hora antes", value=True)
        
        # Notas adicionales de cabina
        notas = st.text_area("Notas o consideraciones especiales (Alergias, indicaciones médicas, etc.)", placeholder="Ej: Paciente en postoperatorio de 15 días, piel sensible...")
        
        st.markdown("<small>* Campos obligatorios</small>", unsafe_allow_html=True)
        boton_enviar = st.form_submit_button("Confirmar y Registrar Reserva")
        
        if boton_enviar:
            # Validaciones estrictas
            if not nombre.strip():
                st.error("⚠️ El nombre del cliente es obligatorio.")
            elif not telefono.strip():
                st.error("⚠️ El número de contacto es obligatorio para activar las alertas.")
            elif "---" in servicio:
                st.error("⚠️ Por favor, selecciona un servicio válido del catálogo de cosmetología.")
            else:
                # Generamos un número de reserva único de 5 dígitos alfanumérico
                num_reserva = f"YAI-{random.randint(10000, 99999)}"
                
                # Insertamos la información estructurada a nuestro DataFrame
                nueva_reserva = pd.DataFrame([{
                    "Número Reserva": num_reserva,
                    "Cliente": nombre,
                    "Teléfono": telefono,
                    "Servicio": servicio,
                    "Fecha": str(fecha),
                    "Hora": str(hora)[:5], # Guarda solo HH:MM
                    "Recordatorio": "Sí" if recordatorio else "No",
                    "Aviso 30 Min": "Sí" if avisar_media_hora else "No",
                    "Notas": notas if notas.strip() else "Ninguna"
                }])
                
                st.session_state.db_reservas = pd.concat([st.session_state.db_reservas, nueva_reserva], ignore_index=True)
                
                # Feedback visual de éxito
                st.success(f"🎉 ¡Reserva agendada exitosamente! *Número de Reserva asignado: {num_reserva}*")
                st.balloons()

# ==========================================
# VISTA 3: CATÁLOGO Y MÉRICAS
# ==========================================
elif opcion == "📊 Catálogo y Métricas":
    st.header("✨ Catálogo Profesional de Servicios")
    st.write("Especialidades cosméticas y de estética disponibles en el salón:")
    
    # Presentación visual del catálogo estructurado en tabla
    servicios_data = [
        {"Servicio": "Diseño y Depilación de Cejas", "Área": "Facial", "Duración Est.": "30 min"},
        {"Servicio": "Laminado de Cejas", "Área": "Facial", "Duración Est.": "45 min"},
        {"Servicio": "Extensión / Lifting de Pestañas", "Área": "Ojos", "Duración Est.": "1h 30min"},
        {"Servicio": "Depilación con Cera", "Área": "Facial / Corporal", "Duración Est.": "20 - 45 min"},
        {"Servicio": "Masaje Corporal (Relajante / Reductor)", "Área": "Corporal", "Duración Est.": "1h"},
        {"Servicio": "Masaje Posquirúrgico", "Área": "Terapéutico", "Duración Est.": "1h"},
        {"Servicio": "Limpieza Facial Profunda", "Área": "Facial", "Duración Est.": "1h 15min"}
    ]
    st.table(pd.DataFrame(servicios_data))
