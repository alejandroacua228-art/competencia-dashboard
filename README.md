# 📊 Dashboard de Tasas Bancarias – Datos Reales (BCRA)

Este proyecto muestra un **dashboard interactivo** desarrollado en **Streamlit** que consume datos reales del **Banco Central de la República Argentina (BCRA)** y de bancos comerciales.

## 🚀 Funcionalidades
- **TAMAR**: Tasa Máxima de Interés de referencia del sistema (BCRA).
- **TNA Bancos**: Tasas nominales anuales de plazo fijo (30 días) por banco (Galicia, Nación, Santander, BBVA).
- **Banco Nación segmentado**: Tasas de plazos fijos diferenciadas por rango de días.

## 📌 Tecnologías usadas
- Python 3
- Streamlit
- Pandas
- Requests
- BeautifulSoup4

## ▶️ Ejecución local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy
Este dashboard está desplegado en **Streamlit Community Cloud**.

## 📎 Fuente
- [Banco Central de la República Argentina (BCRA)](https://www.bcra.gob.ar)
- [Banco Nación](https://www.bna.com.ar)
- [La Nación – Economía](https://www.lanacion.com.ar/economia)
