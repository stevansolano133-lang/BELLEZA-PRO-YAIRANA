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
        {"Servicio": "Laminad…
[2:16 a. m., 15/10/2026] Dios Es Amor 😍: import streamlit as st
import pandas as pd
from datetime import date
from openai import OpenAI
import io
from pypdf import PdfReader
from docx import Document

# 1. Configuración de la página (¡Estilo estético!)
st.set_page_config(
    page_title="Belleza Pro Yairana",
    page_icon="✨",
    layout="centered"
)

# Estilos visuales personalizados
st.markdown("""
    <style>
    .main-title {
        color: #D4AF37; /* Dorado */
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        margin-bottom: 20px;
    }
    .subtitle {
        color: #555555;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }
    </style>
""", unsafe_allowed_html=True)

st.markdown('<h1 class="main-title">✨ BELLEZA PRO YAIRANA ✨</h1>', unsafe_allowed_html=True)
st.markdown('<p class="subtitle">Sistema Inteligente de Gestión y Asesoría Estética</p>', unsafe_allowed_html=True)

# 2. Conexión segura con OpenAI (Usa los Secrets de Streamlit)
# Recuerda configurar tu 'OPENAI_API_KEY' en los Settings de Streamlit Cloud
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    client = None

# 3. Menú de navegación de la aplicación
menu = ["Gestión de Clientes", "Asesor de Belleza IA", "Análisis de Documentos"]
choice = st.sidebar.selectbox("Selecciona una opción:", menu)

# --- MÓDULO 1: GESTIÓN DE CLIENTES ---
if choice == "Gestión de Clientes":
    st.subheader("📋 Registro de Citas y Tratamientos")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del Cliente:")
        servicio = st.selectbox("Servicio / Tratamiento:", ["Cuidado Facial", "Estética Corporal", "Maquillaje Profesional", "Asesoría de Imagen", "Otro"])
    with col2:
        fecha = st.date_input("Fecha de la Cita:", date.today())
        telefono = st.text_input("Teléfono de Contacto:")
        
    notas = st.text_area("Notas del tratamiento o alergias importantes:")
    
    if st.button("Guardar Registro"):
        if nombre and telefono:
            st.success(f"✔️ ¡Cita guardada con éxito para {nombre} el día {fecha}!")
            # Aquí puedes expandir el código para guardar los datos en un Excel usando openpyxl o pandas
        else:
            st.warning("⚠️ Por favor completa el nombre y el teléfono del cliente.")

# --- MÓDULO 2: ASESOR DE BELLEZA IA ---
elif choice == "Asesor de Belleza IA":
    st.subheader("🤖 Asistente de Estética Inteligente")
    st.write("Consulta combinaciones de productos, rutinas de cuidado de la piel o recomendaciones personalizadas.")
    
    if client is None:
        st.info("💡 Para activar los consejos de la IA, recuerda conectar tu API Key de OpenAI en la configuración de Streamlit.")
    
    pregunta_usuario = st.text_area("Describe el tipo de piel o la consulta estética del cliente:")
    
    if st.button("Generar Recomendación Profesional"):
        if pregunta_usuario:
            if client:
                with st.spinner("Analizando con IA..."):
                    try:
                        prompt_sistema = "Eres un experto de nivel mundial en cosmetología, estética, cuidado de la piel y estilismo para el centro estético Belleza Pro Yairana. Brinda recomendaciones detalladas, amables y profesionales."
                        
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": prompt_sistema},
                                {"role": "user", "content": pregunta_usuario}
                            ]
                        )
                        st.markdown("### 📋 Recomendación del Asistente:")
                        st.write(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Hubo un error con la IA: {e}")
            else:
                # Respuesta de simulación en caso de que no tenga la API key configurada todavía
                st.markdown("### 📋 Recomendación Estándar (Simulada):")
                st.write("Para pieles sensibles, se sugiere una rutina enfocada en la hidratación con productos hipoalergénicos, libres de fragancias artificiales, incorporando ceramidas y protector solar mineral FPS 50+ diariamente.")
        else:
            st.warning("⚠️ Escribe una consulta antes de enviar.")

# --- MÓDULO 3: ANÁLISIS DE DOCUMENTOS ---
elif choice == "Análisis de Documentos":
    st.subheader("📄 Lector de Archivos (Fichas Técnicas / PDF / Word)")
    st.write("Carga documentos de proveedores, ingredientes o fichas de clientes para extraer el texto.")
    
    archivo_cargado = st.file_uploader("Sube un archivo (.pdf, .docx, .txt):", type=["pdf", "docx", "txt"])
    
    if archivo_cargado is not None:
        nombre_archivo = archivo_cargado.name.lower()
        texto_extraido = ""
        
        with st.spinner("Procesando archivo..."):
            if nombre_archivo.endswith(".pdf"):
                lector_pdf = PdfReader(archivo_cargado)
                for pagina in lector_pdf.pages:
                    texto_extraido += pagina.extract_text() + "\n"
            elif nombre_archivo.endswith(".docx"):
                doc = Document(archivo_cargado)
                for parrafo in doc.paragraphs:
                    texto_extraido += parrafo.text + "\n"
            else:
                texto_extraido = archivo_cargado.read().decode("utf-8")
                
        st.success("¡Archivo leído correctamente!")
        st.text_area("Contenido extraído del documento:", texto_extraido, height=250)
