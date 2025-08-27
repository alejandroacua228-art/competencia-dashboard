import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Dashboard de Tasas Bancarias – BCRA", page_icon="📊", layout="wide")

st.title("📊 Dashboard de Tasas Bancarias – Datos Reales BCRA")

st.markdown(
    """
    Este dashboard muestra **tasas de interés reales** obtenidas de fuentes oficiales
    del **Banco Central de la República Argentina (BCRA)** y de bancos comerciales.
    """
)

# -----------------------
# FUNCIÓN: Obtener TAMAR del BCRA
# -----------------------
def obtener_tamar():
    url = "https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        tabla = soup.find("table", {"class": "table"})
        filas = tabla.find_all("tr")
        for fila in filas:
            celdas = [c.get_text(strip=True) for c in fila.find_all("td")]
            if len(celdas) >= 2 and "Tasa de interés" in celdas[0]:
                return {"Variable": celdas[0], "Valor": celdas[1]}
        return {"Variable": "TAMAR", "Valor": "No encontrado"}
    except Exception as e:
        return {"Variable": "TAMAR", "Valor": str(e)}

# -----------------------
# FUNCIÓN: Obtener TNA por banco (fuente La Nación con datos del BCRA)
# -----------------------
def obtener_tna_bancos():
    url = "https://www.lanacion.com.ar/economia/plazo-fijo-cual-es-la-tasa-de-interes-banco-por-banco-este-lunes-25-de-agosto-nid25082025/"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        bancos = []
        for fila in soup.find_all("tr"):
            cols = [c.get_text(strip=True) for c in fila.find_all("td")]
            if len(cols) == 2:
                bancos.append({"Banco": cols[0], "TNA (%)": cols[1]})
        return pd.DataFrame(bancos)
    except Exception as e:
        return pd.DataFrame([{"Banco": "Error", "TNA (%)": str(e)}])

# -----------------------
# FUNCIÓN: Tasas del Banco Nación (segmentadas)
# -----------------------
def obtener_tasas_bna():
    url = "https://www.bna.com.ar/Personas/PlazoFijoTradicional"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        tabla = soup.find("table")
        filas = tabla.find_all("tr")
        data = []
        for fila in filas:
            cols = [c.get_text(strip=True) for c in fila.find_all("td")]
            if len(cols) >= 2:
                data.append({"Plazo": cols[0], "TNA (%)": cols[1]})
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame([{"Plazo": "Error", "TNA (%)": str(e)}])

# -----------------------
# SECCIONES DEL DASHBOARD
# -----------------------

# TAMAR
st.subheader("📌 Tasa de Referencia del Sistema (TAMAR)")
tamar = obtener_tamar()
st.metric(tamar["Variable"], tamar["Valor"])

# TNA Bancos
st.subheader("🏦 TNA Plazo Fijo (30 días) por Banco")
df_bancos = obtener_tna_bancos()
st.dataframe(df_bancos, use_container_width=True)

# Banco Nación segmentado
st.subheader("🇦🇷 Banco Nación – Tasas Segmentadas")
df_bna = obtener_tasas_bna()
st.dataframe(df_bna, use_container_width=True)

st.markdown("---")
st.caption("Fuente: BCRA y sitios oficiales de bancos comerciales.")
