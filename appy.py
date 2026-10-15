import streamlit as st
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
