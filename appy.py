# BELLEZA PRO — Agenda e inventario

# Aplicación Streamlit para estilista/cosmetóloga.

## Funciones
#- Agenda de reservas con fecha, hora, duración, datos de clienta, servicio, producto, precio, abono y estado.
#- Avisos de próximas citas mientras la aplicación está abierta.
#- Catálogo editable de servicios y precios.
#- Inventario con existencias, mínimos y vencimiento.
#- Caja, ingresos, gastos y saldos pendientes.
#- Exportación de tablas a CSV y Excel.

## Ejecutar
1. Instala Python.
2. Instala dependencias: `pip install -r requirements.txt`
3. Ejecuta: `streamlit run app.py`

## Publicar en Streamlit Community Cloud
Sube `app.py` y `requirements.txt` a un repositorio GitHub y selecciona `app.py` como archivo principal.

## Importante sobre datos y recordatorios
La base SQLite se guarda localmente en `belleza_pro.db`. En entornos gratuitos en la nube, los archivos locales pueden no ser una solución de almacenamiento permanente; descarga respaldos y considera conectar una base de datos persistente antes de depender de ella para uso diario.
Los recordatorios de esta versión aparecen dentro de la app abierta. Las notificaciones push/SMS/WhatsApp con la app cerrada requieren una integración adicional.

