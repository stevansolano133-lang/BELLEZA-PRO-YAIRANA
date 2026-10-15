import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="BELLEZA PRO", layout="wide")

st.title("BELLEZA PRO - Agenda e Inventario")
st.subheader("Aplicación Streamlit para estilista/cosmetóloga.")

# Menú lateral para navegar en las funciones que anotaste
opcion = st.sidebar.selectbox(
    "Selecciona una sección:",
    ["Agenda de Reservas", "Catálogo de Servicios", "Inventario", "Caja y Gastos"]
)

if opcion == "Agenda de Reservas":
    st.header("📅 Agenda de Reservas")
    st.write("Próximas citas y control de estados.")
    # Aquí irá el código para guardar citas

elif opcion == "Catálogo de Servicios":
    st.header("💇 Catálogo de Servicios")
    st.write("Gestión de servicios y precios.")

elif opcion == "Inventario":
    st.header("📦 Inventario")
    st.write("Control de existencias, mínimos y vencimientos.")

elif opcion == "Caja y Gastos":
    st.header("💰 Caja, Ingresos y Gastos")
    st.write("Control de saldos pendientes.")
