import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

# -----------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------
st.set_page_config(
    page_title="Dashboard de Competencia Bancaria",
    page_icon="📊",
    layout="wide"
)

# -----------------------
# ESTILOS
# -----------------------
st.markdown(
    """
    <style>
    .kpi-card {
        padding: 18px; border-radius: 16px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        background-color: #f5f7fa;
        margin: 5px;
    }
    .kpi-title {font-size: 0.9rem; opacity: 0.7;}
    .kpi-value {font-size: 1.6rem; font-weight: 700;}
    .pos {color: #167e36}
    .neg {color: #b00020}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------
# INTRODUCCIÓN
# -----------------------
st.title("📊 Dashboard de Monitoreo de Competencia Bancaria")
st.markdown(
    """
    Este dashboard permite **comparar bancos competidores** en:
    - **Savings APY (%):** Tasa de interés para ahorros/plazos fijos.
    - **Loan APR (%):** Tasa de interés para préstamos.
    - **Fee mantenimiento (ARS):** Cargo mensual de cuenta.
    - **Promo Score (0-100):** Intensidad y presencia de promociones.

    ⚠️ *Los datos que se muestran son simulados a modo de demostración.*
    """
)

# -----------------------
# DATOS SIMULADOS
# -----------------------
@st.cache_data
def generar_datos(seed: int = 228, dias: int = 120):
    np.random.seed(seed)
    bancos = ["Galicia", "Nación", "Santander", "BBVA"]
    hoy = datetime.today().date()
    fechas = pd.date_range(end=hoy, periods=dias).date

    registros = []
    base_tea = {"Galicia": 74, "Nación": 72, "Santander": 73.5, "BBVA": 73}
    for banco in bancos:
        tea_series = base_tea[banco] + np.cumsum(np.random.normal(0, 0.06, size=dias))
        prestamo_series = tea_series + 20 + np.random.normal(0, 0.05, size=dias)
        fee_series = np.clip(18000 + np.cumsum(np.random.normal(0, 40, size=dias)), 12000, None)
        promo_series = np.clip(50 + np.cumsum(np.random.normal(0, 0.4, size=dias)), 0, 100)
        for i, f in enumerate(fechas):
            registros.append({
                "fecha": f,
                "banco": banco,
                "savings_APY_%": round(float(tea_series[i]), 2),
                "loan_APR_%": round(float(prestamo_series[i]), 2),
                "fee_mantenimiento": round(float(fee_series[i]), 0),
                "promo_score": round(float(promo_series[i]), 1)
            })
    return pd.DataFrame(registros)

df = generar_datos()
fecha_min, fecha_max = df["fecha"].min(), df["fecha"].max()

# -----------------------
# SIDEBAR FILTROS
# -----------------------
st.sidebar.header("⚙️ Filtros")
bancos_sel = st.sidebar.multiselect("Bancos", df["banco"].unique(), df["banco"].unique())
rango = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_max - relativedelta(months=1), fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)
umbral = st.sidebar.slider("Umbral de alerta (% variación diaria)", 1.0, 10.0, 3.0, 0.5)

# -----------------------
# FILTRO DE VISTA
# -----------------------
start_date, end_date = rango if isinstance(rango, tuple) else (fecha_min, fecha_max)
view = df[(df["banco"].isin(bancos_sel)) & (df["fecha"].between(start_date, end_date))]

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 KPIs – Último día analizado")
cols = st.columns(len(bancos_sel))
ultimo = view[view["fecha"] == end_date]
for i, banco in enumerate(bancos_sel):
    fila = ultimo[ultimo["banco"] == banco]
    if not fila.empty:
        with cols[i]:
            st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-title'>Banco</div><div class='kpi-value'>{banco}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-title'>Savings APY</div><div class='kpi-value'>{fila['savings_APY_%'].values[0]}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-title'>Loan APR</div><div class='kpi-value'>{fila['loan_APR_%'].values[0]}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-title'>Fee mantenimiento</div><div class='kpi-value'>$ {fila['fee_mantenimiento'].values[0]:,.0f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-title'>Promo score</div><div class='kpi-value'>{fila['promo_score'].values[0]}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# EVOLUCIÓN TEMPORAL
# -----------------------
st.subheader("📈 Evolución temporal de métricas")
metrica = st.selectbox("Seleccioná una métrica para analizar", ["savings_APY_%","loan_APR_%","fee_mantenimiento","promo_score"])
pivot = view.pivot(index="fecha", columns="banco", values=metrica)
st.line_chart(pivot, height=400)

# -----------------------
# COMPARACIÓN ÚLTIMO DÍA
# -----------------------
st.subheader("📊 Comparación en el último día")
cols_order = ["savings_APY_%","loan_APR_%","fee_mantenimiento","promo_score"]
st.bar_chart(ultimo.set_index("banco")[cols_order])

# -----------------------
# RANKING POR FEE
# -----------------------
st.subheader("🏆 Ranking de bancos por fee de mantenimiento")
ranking = ultimo[["banco","fee_mantenimiento"]].sort_values("fee_mantenimiento")
st.dataframe(ranking.reset_index(drop=True))

# -----------------------
# ALERTAS
# -----------------------
st.subheader("🚨 Alertas de variación")
alertas = []
for banco in bancos_sel:
    df_b = view[view["banco"]==banco].sort_values("fecha").copy()
    for m in cols_order:
        df_b[m+"_var%"] = df_b[m].pct_change()*100
        cambios = df_b[df_b[m+"_var%"].abs()>=umbral]
        for _,r in cambios.iterrows():
            alertas.append({"fecha":r["fecha"],"banco":banco,"métrica":m,"variación_%":round(r[m+'_var%'],2),"valor":r[m]})
if alertas:
    st.dataframe(pd.DataFrame(alertas).sort_values("fecha",ascending=False))
else:
    st.success("No se detectaron variaciones que superen el umbral seleccionado.")

# -----------------------
# NOTA FINAL
# -----------------------
st.markdown("---")
st.info("💡 Este dashboard usa datos simulados. Para usar datos reales, reemplazá la función `generar_datos()` con conectores a APIs o bases reales, y configurá credenciales en `st.secrets`.")
