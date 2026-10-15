import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, time, datetime, timedelta
from io import BytesIO

st.set_page_config(page_title="BELLEZA PRO", page_icon="💄", layout="wide")

DATA_DIR = Path("datos_belleza")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "citas": DATA_DIR / "citas.csv",
    "servicios": DATA_DIR / "servicios.csv",
    "inventario": DATA_DIR / "inventario.csv",
    "movimientos": DATA_DIR / "movimientos.csv",}
SCHEMAS = {
    "citas": ["id", "fecha", "hora", "nombre", "apellido", "telefono", "servicio", "producto", "valor", "estado", "notas", "creado"],
    "servicios": ["servicio", "duracion_min", "precio", "activo"],
    "inventario": ["producto", "categoria", "cantidad", "unidad", "costo_unitario", "stock_minimo"],
    "movimientos": ["fecha", "hora", "producto", "tipo", "cantidad", "motivo"],
}

DEFAULT_SERVICES = [
    {"servicio": "Diseño de cejas", "duracion_min": 30, "precio": 0, "activo": "Sí"},
    {"servicio": "Depilación de cejas", "duracion_min": 20, "precio": 0, "activo": "Sí"},
    {"servicio": "Pestañas", "duracion_min": 45, "precio": 0, "activo": "Sí"},
    {"servicio": "Laminado de cejas", "duracion_min": 45, "precio": 0, "activo": "Sí"},
    {"servicio": "Masaje corporal", "duracion_min": 60, "precio": 0, "activo": "Sí"},
    {"servicio": "Depilación con cera", "duracion_min": 30, "precio": 0, "activo": "Sí"},
    {"servicio": "Masaje + depilación con cera", "duracion_min": 90, "precio": 0, "activo": "Sí"},
]

def load_table(key):
    path = FILES[key]
    if path.exists():
        try:
            df = pd.read_csv(path, dtype={"telefono": str}, keep_default_na=False)
            for col in SCHEMAS[key]:
                if col not in df.columns:
                    df[col] = ""
            return df[SCHEMAS[key]]
        except Exception:
            pass
    df = pd.DataFrame(columns=SCHEMAS[key])
    if key == "servicios":
        df = pd.DataFrame(DEFAULT_SERVICES, columns=SCHEMAS[key])
        save_table(key, df)
    else:
        save_table(key, df)
    return df

def save_table(key, df):
    df = df.copy()
    for col in SCHEMAS[key]:
        if col not in df.columns:
            df[col] = ""
    df[SCHEMAS[key]].to_csv(FILES[key], index=False)

def money(value):
    try:
        return "$ {:,.0f}".format(float(value)).replace(",", ".")
    except (ValueError, TypeError):
        return "$ 0"

def excel_bytes(tables):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in tables.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    output.seek(0)
    return output.getvalue()

st.title("💄 BELLEZA PRO — Agenda e Inventario")
st.caption("Organiza citas, servicios, productos y movimientos de tu negocio.")
st.warning("Importante: esta versión guarda datos en archivos CSV dentro de la aplicación. En Streamlit Cloud, esos archivos pueden perderse al reiniciar o volver a desplegar. Descarga copias de Excel periódicamente; para almacenamiento permanente compartido se debe conectar una base de datos.")

citas = load_table("citas")
servicios = load_table("servicios")
inventario = load_table("inventario")
movimientos = load_table("movimientos")

with st.sidebar:
    st.header("📋 Menú principal")
    seccion = st.radio("Selecciona una sección", [
        "Resumen", "Agenda de reservas", "Catálogo de servicios",
        "Inventario", "Movimientos de productos", "Reportes y copia de seguridad"
    ])
    st.divider()
    st.caption("BELLEZA PRO • Gestión del salón")

if seccion == "Resumen":
    hoy = date.today().isoformat()
    citas_hoy = citas[citas["fecha"].astype(str) == hoy] if not citas.empty else citas
    pendientes = citas[citas["estado"].isin(["Pendiente", "Confirmada"])] if not citas.empty else citas
    stock_bajo = inventario[
        pd.to_numeric(inventario["cantidad"], errors="coerce").fillna(0)
        <= pd.to_numeric(inventario["stock_minimo"], errors="coerce").fillna(0)
    ] if not inventario.empty else inventario
    a, b, c, d = st.columns(4)
    a.metric("Citas de hoy", len(citas_hoy))
    b.metric("Citas pendientes/confirmadas", len(pendientes))
    c.metric("Productos registrados", len(inventario))
    d.metric("Alertas de stock bajo", len(stock_bajo))
    st.subheader("Próximas reservas")
    if not citas.empty:
        proximas = citas[citas["fecha"].astype(str) >= hoy].copy()
        if not proximas.empty:
            proximas["_orden"] = proximas["fecha"].astype(str) + " " + proximas["hora"].astype(str)
            proximas = proximas.sort_values("_orden").drop(columns="_orden")
          st.dataframe( proximas.head(10).astype(str), use_container_width=True, hide_index=True )
        else:st.info("No hay reservas futuras registradas.")
    else:st.info("Todavía no hay citas. Entra a «Agenda de reservas» para crear la primera.")
    if not stock_bajo.empty:
        st.subheader("⚠️ Productos por reponer")
        st.dataframe(stock_bajo.astype(str), use_container_width=True, hide_index=True)
elif seccion == "Agenda de reservas":
    st.header("📅 Agenda de reservas")
    st.write("Registra los datos del cliente y el servicio. Los campos marcados con * son obligatorios.")
    activos = servicios[servicios["activo"].astype(str).str.lower().isin(["sí", "si", "true", "1"])] if not servicios.empty else servicios
    opciones = activos["servicio"].astype(str).tolist() if not activos.empty else []
    with st.form("nueva_cita", clear_on_submit=True):
        st.subheader("➕ Agendar nueva cita")
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre del cliente *")
        apellido = col2.text_input("Apellido del cliente *")
        telefono = col1.text_input("Teléfono / WhatsApp")
        fecha_cita = col2.date_input("Fecha de la reserva *", value=date.today(), min_value=date.today())
        hora_cita = col1.time_input("Hora de la reserva *", value=time(9, 0), step=timedelta(minutes=15))
        if opciones:
            servicio = col2.selectbox("Servicio que se realizará *", opciones)
        else:
            servicio = col2.text_input("Servicio que se realizará *", placeholder="Ej. Laminado de cejas")
        producto = st.text_input("Producto que se aplicará (si corresponde)")
        col3, col4 = st.columns(2)
        precio_sugerido = 0.0
        if opciones and servicio:
            fila = activos[activos["servicio"].astype(str) == str(servicio)]
            if not fila.empty:
                try: precio_sugerido = float(fila.iloc[0]["precio"] or 0)
                except (ValueError, TypeError): pass
        valor = col3.number_input("Valor de la cita ($)", min_value=0.0, value=precio_sugerido, step=500.0)
        estado = col4.selectbox("Estado", ["Pendiente", "Confirmada", "Atendida", "Cancelada"])
        notas = st.text_area("Notas / indicaciones")
        guardar = st.form_submit_button("💾 Guardar reserva", use_container_width=True)
        if guardar:
            if not nombre.strip() or not apellido.strip() or not str(servicio).strip():
                st.error("Escribe el nombre, apellido y servicio antes de guardar.")
            else:
                nueva = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "fecha": fecha_cita.isoformat(), "hora": hora_cita.strftime("%H:%M"),
                    "nombre": nombre.strip(), "apellido": apellido.strip(), "telefono": telefono.strip(),
                    "servicio": str(servicio), "producto": producto.strip(), "valor": valor,
                    "estado": estado, "notas": notas.strip(), "creado": datetime.now().isoformat(timespec="seconds")
                }
                citas = pd.concat([citas, pd.DataFrame([nueva])], ignore_index=True)
                save_table("citas", citas)
                st.success("¡Reserva guardada!")
                st.rerun()
    st.divider()
    st.subheader("🔎 Consultar y administrar reservas")
    f1, f2 = st.columns(2)
    filtro_fecha = f1.date_input("Filtrar por fecha", value=date.today(), key="filtro_fecha")
    filtro_estado = f2.selectbox("Filtrar por estado", ["Todos", "Pendiente", "Confirmada", "Atendida", "Cancelada"])
    vista = citas.copy()
    if not vista.empty:
        if filtro_fecha:
            vista = vista[vista["fecha"].astype(str) == filtro_fecha.isoformat()]
        if filtro_estado != "Todos":
            vista = vista[vista["estado"].astype(str) == filtro_estado]
        if vista.empty:
            st.info("No hay reservas que coincidan con esos filtros.")
        else:
            st.dataframe(vista[["fecha","hora","nombre","apellido","telefono","servicio","producto","valor","estado","notas"]], use_container_width=True, hide_index=True)
        st.subheader("Cambiar estado o eliminar una reserva")
        ids = citas["id"].astype(str).tolist()
        if ids:
            labels = {}
            for _, r in citas.iterrows():
                labels[str(r["id"])] = f'{r["fecha"]} {r["hora"]} — {r["nombre"]} {r["apellido"]} ({r["servicio"]})'
            id_sel = st.selectbox("Selecciona la reserva", ids, format_func=lambda x: labels.get(x, x))
            r1, r2 = st.columns(2)
            estado_nuevo = r1.selectbox("Nuevo estado", ["Pendiente", "Confirmada", "Atendida", "Cancelada"], key="estado_nuevo")
            if r1.button("Actualizar estado"):
                citas.loc[citas["id"].astype(str) == str(id_sel), "estado"] = estado_nuevo
                save_table("citas", citas)
                st.success("Estado actualizado.")
                st.rerun()
            confirmar_borrado = r2.checkbox("Confirmo que deseo eliminar esta reserva")
            if r2.button("Eliminar reserva", disabled=not confirmar_borrado):
                citas = citas[citas["id"].astype(str) != str(id_sel)]
                save_table("citas", citas)
                st.success("Reserva eliminada.")
                st.rerun()
    else:
        st.info("Aún no se han guardado reservas.")

elif seccion == "Catálogo de servicios":
    st.header("✨ Catálogo de servicios")
    with st.form("agregar_servicio", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nuevo_servicio = c1.text_input("Nombre del servicio *")
        duracion = c2.number_input("Duración (minutos)", min_value=5, max_value=480, value=30, step=5)
        precio = c3.number_input("Precio ($)", min_value=0.0, value=0.0, step=500.0)
        activo = st.selectbox("¿Disponible para reservas?", ["Sí", "No"])
        if st.form_submit_button("Agregar servicio"):
            if not nuevo_servicio.strip():
                st.error("Escribe el nombre del servicio.")
            elif servicios["servicio"].astype(str).str.lower().eq(nuevo_servicio.strip().lower()).any():
                st.error("Ese servicio ya está registrado.")
            else:
                servicios = pd.concat([servicios, pd.DataFrame([{"servicio":nuevo_servicio.strip(),"duracion_min":duracion,"precio":precio,"activo":activo}])], ignore_index=True)
                save_table("servicios", servicios)
                st.success("Servicio agregado.")
                st.rerun()
    st.subheader("Servicios registrados")
    if not servicios.empty:
        st.dataframe(servicios, use_container_width=True, hide_index=True)
        st.caption("Para cambiar precios o duración, edita la tabla y pulsa Guardar cambios.")
        editados = st.data_editor(servicios, use_container_width=True, hide_index=True, key="editor_servicios")
        if st.button("Guardar cambios del catálogo"):
            save_table("servicios", editados)
            st.success("Catálogo actualizado.")
            st.rerun()
        borrar_servicio = st.selectbox("Servicio para eliminar", servicios["servicio"].astype(str).tolist())
        if st.button("Eliminar servicio seleccionado"):
            servicios = servicios[servicios["servicio"].astype(str) != borrar_servicio]
            save_table("servicios", servicios)
            st.success("Servicio eliminado.")
            st.rerun()
    else:
        st.info("Agrega el primer servicio usando el formulario.")

elif seccion == "Inventario":
    st.header("📦 Inventario de productos")
    with st.form("nuevo_producto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre_prod = c1.text_input("Nombre del producto *")
        categoria = c2.text_input("Categoría", placeholder="Ej. Cejas, pestañas, cuidado facial")
        c3, c4, c5, c6 = st.columns(4)
        cantidad = c3.number_input("Cantidad inicial", min_value=0.0, value=0.0, step=1.0)
        unidad = c4.selectbox("Unidad", ["unidad", "ml", "litro", "gramo", "kg", "paquete", "otro"])
        costo = c5.number_input("Costo unitario ($)", min_value=0.0, value=0.0, step=500.0)
        minimo = c6.number_input("Avisar cuando queden", min_value=0.0, value=2.0, step=1.0)
        if st.form_submit_button("Agregar producto"):
            if not nombre_prod.strip():
                st.error("Escribe el nombre del producto.")
            elif inventario["producto"].astype(str).str.lower().eq(nombre_prod.strip().lower()).any():
                st.error("Ya existe un producto con ese nombre.")
            else:
                nuevo = {"producto":nombre_prod.strip(),"categoria":categoria.strip(),"cantidad":cantidad,"unidad":unidad,"costo_unitario":costo,"stock_minimo":minimo}
                inventario = pd.concat([inventario, pd.DataFrame([nuevo])], ignore_index=True)
                save_table("inventario", inventario)
                st.success("Producto agregado al inventario.")
                st.rerun()
    st.subheader("Existencias")
    if not inventario.empty:
        vista_inv = inventario.copy()
        vista_inv["cantidad_num"] = pd.to_numeric(vista_inv["cantidad"], errors="coerce").fillna(0)
        vista_inv["minimo_num"] = pd.to_numeric(vista_inv["stock_minimo"], errors="coerce").fillna(0)
        vista_inv["Alerta"] = vista_inv.apply(lambda r: "⚠️ Reponer" if r["cantidad_num"] <= r["minimo_num"] else "Disponible", axis=1)
        st.dataframe(vista_inv.drop(columns=["cantidad_num","minimo_num"]), use_container_width=True, hide_index=True)
        st.subheader("Editar producto")
        producto_sel = st.selectbox("Selecciona producto", inventario["producto"].astype(str).tolist())
        fila_idx = inventario.index[inventario["producto"].astype(str) == producto_sel][0]
        fila = inventario.loc[fila_idx]
        with st.form("editar_producto"):
            ec1, ec2, ec3 = st.columns(3)
            nueva_cantidad = ec1.number_input("Cantidad actual", min_value=0.0, value=float(pd.to_numeric(fila["cantidad"], errors="coerce") or 0), step=1.0)
            nuevo_costo = ec2.number_input("Costo unitario", min_value=0.0, value=float(pd.to_numeric(fila["costo_unitario"], errors="coerce") or 0), step=500.0)
            nuevo_minimo = ec3.number_input("Stock mínimo", min_value=0.0, value=float(pd.to_numeric(fila["stock_minimo"], errors="coerce") or 0), step=1.0)
            if st.form_submit_button("Guardar producto"):
                inventario.loc[fila_idx, "cantidad"] = nueva_cantidad
                inventario.loc[fila_idx, "costo_unitario"] = nuevo_costo
                inventario.loc[fila_idx, "stock_minimo"] = nuevo_minimo
                save_table("inventario", inventario)
                st.success("Inventario actualizado.")
                st.rerun()
        confirmar = st.checkbox("Confirmo eliminar este producto")
        if st.button("Eliminar producto", disabled=not confirmar):
            inventario = inventario[inventario["producto"].astype(str) != producto_sel]
            save_table("inventario", inventario)
            st.success("Producto eliminado.")
            st.rerun()
    else:
        st.info("Todavía no hay productos registrados.")

elif seccion == "Movimientos de productos":
    st.header("🔄 Entradas y salidas de productos")
    if inventario.empty:
        st.info("Primero agrega productos en la sección Inventario.")
    else:
        with st.form("movimiento_producto", clear_on_submit=True):
            prod = st.selectbox("Producto", inventario["producto"].astype(str).tolist())
            tipo = st.radio("Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
            cant_mov = st.number_input("Cantidad", min_value=0.1, value=1.0, step=1.0)
            motivo = st.text_input("Motivo", placeholder="Compra, uso en servicio, ajuste...")
            if st.form_submit_button("Registrar movimiento"):
                idx = inventario.index[inventario["producto"].astype(str) == prod][0]
                actual = float(pd.to_numeric(inventario.loc[idx, "cantidad"], errors="coerce") or 0)
                if tipo == "Salida" and cant_mov > actual:
                    st.error(f"No hay suficiente existencia. Disponible: {actual:g}")
                else:
                    nueva_cant = actual + cant_mov if tipo == "Entrada" else actual - cant_mov
                    inventario.loc[idx, "cantidad"] = nueva_cant
                    save_table("inventario", inventario)
                    movimiento = {"fecha":date.today().isoformat(),"hora":datetime.now().strftime("%H:%M"),"producto":prod,"tipo":tipo,"cantidad":cant_mov,"motivo":motivo.strip()}
                    movimientos = pd.concat([movimientos, pd.DataFrame([movimiento])], ignore_index=True)
                    save_table("movimientos", movimientos)
                    st.success("Movimiento registrado y existencias actualizadas.")
                    st.rerun()
    st.subheader("Historial de movimientos")
    if not movimientos.empty:
        st.dataframe(movimientos.sort_values(["fecha","hora"], ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay movimientos.")

elif seccion == "Reportes y copia de seguridad":
    st.header("📊 Reportes y copia de seguridad")
    total_citas = len(citas)
    atendidas = citas[citas["estado"].astype(str) == "Atendida"] if not citas.empty else citas
    ingresos_atendidos = pd.to_numeric(atendidas["valor"], errors="coerce").fillna(0).sum() if not atendidas.empty else 0
    a,b,c = st.columns(3)
    a.metric("Reservas registradas", total_citas)
    b.metric("Servicios atendidos", len(atendidas))
    c.metric("Ingresos de citas atendidas", money(ingresos_atendidos))
    st.caption("Los ingresos se calculan sumando el valor de las citas marcadas como «Atendida»; no reemplazan una contabilidad formal.")
    st.download_button("⬇️ Descargar copia de seguridad Excel", data=excel_bytes({
        "Reservas": citas, "Servicios": servicios, "Inventario": inventario, "Movimientos": movimientos
    }), file_name=f"respaldo_belleza_{date.today().isoformat()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.download_button("⬇️ Descargar reservas CSV", data=citas.to_csv(index=False).encode("utf-8-sig"), file_name="reservas_belleza.csv", mime="text/csv", use_container_width=True)
    st.subheader("Vista de datos")
    with st.expander("Reservas"): st.dataframe(citas, use_container_width=True, hide_index=True)
    with st.expander("Servicios"): st.dataframe(servicios, use_container_width=True, hide_index=True)
    with st.expander("Inventario"): st.dataframe(inventario, use_container_width=True, hide_index=True)
    with st.expander("Movimientos"): st.dataframe(movimientos, use_container_width=True, hide_index=True)
