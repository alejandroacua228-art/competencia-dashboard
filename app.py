import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Monitoreo de Competencia – Bancos", page_icon="📊", layout="wide")

@st.cache_data
def generar_datos(seed=1, dias=90):
    np.random.seed(seed)
    bancos = ["Galicia","Nación","Santander","BBVA"]
    fechas = pd.date_range(end=datetime.today().date(), periods=dias).date
    data = []
    for banco in bancos:
        base = 70 + np.random.rand()*5
        tasas = base + np.cumsum(np.random.normal(0,0.05,dias))
        for i,f in enumerate(fechas):
            data.append({"fecha":f,"banco":banco,"savings_APY_%":round(tasas[i],2)})
    return pd.DataFrame(data)

df = generar_datos()
st.title("📊 Dashboard de Monitoreo de Competencia – Bancos")
st.line_chart(df.pivot(index="fecha", columns="banco", values="savings_APY_%"))
