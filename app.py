import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Forecasting Inflasi Indonesia", layout="wide", page_icon="🔮")

# ==========================================
# DUMMY DATA — Akan diganti query Aiven nanti
# ==========================================
@st.cache_data
def load_data():
    """Nanti fungsi ini diganti jadi query ke Aiven PostgreSQL."""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2025-12-01', freq='MS')
    n = len(dates)

    oil = np.clip(60 + np.cumsum(np.random.normal(0.5, 3, n)), 20, 130)
    kurs = np.clip(14200 + np.cumsum(np.random.normal(15, 120, n)), 13500, 17000).astype(int)
    inflasi = np.round(0.3 + (oil - 60) * 0.01 + (kurs - 14200) * 0.0002 + np.random.normal(0, 0.15, n), 2)

    return pd.DataFrame({
        'tanggal': dates, 'tahun': dates.year, 'bulan': dates.month,
        'inflasi_mtom': inflasi,
        'harga_minyak_usd': np.round(oil, 2),
        'perubahan_persen_minyak': np.round(np.concatenate([[0], np.diff(oil) / oil[:-1] * 100]), 2),
        'kurs_usd_idr': kurs,
        'perubahan_persen_kurs': np.round(np.concatenate([[0], np.diff(kurs) / kurs[:-1] * 100]), 2),
        'harga_pertalite': np.where(dates < '2022-09-01', 7650, 10000).astype(int),
        'harga_solar': np.where(dates < '2022-09-01', 5150, 6800).astype(int),
    })

df = load_data()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Konfigurasi")

    st.caption("📡 Sumber Data")
    st.code("CSV historis (2020-2026)\n→ ETL Pipeline\n→ Aiven PostgreSQL\n→ Streamlit", language="text")
    st.info("📌 Data **statis historis** (bulanan), bukan real-time.")
    st.warning("⏳ Mode Dummy — belum terhubung Aiven.", icon="⚠️")

    st.divider()
    st.caption("📊 Dashboard BI")
    st.markdown("[Buka di Google Data Studio →](https://datastudio.google.com/u/0/reporting/33b3fc15-7315-4340-a178-3c860fde9ab3/page/T5M0F/edit)")

# ==========================================
# JUDUL
# ==========================================
st.markdown("## 🔮 Forecasting & Prediksi Inflasi Indonesia")
st.caption("Machine Learning untuk prediksi inflasi berdasarkan harga minyak global, kurs USD/IDR, dan harga BBM — Data historis dari Aiven PostgreSQL.")

# ==========================================
# FORECAST GRAFIK
# ==========================================
st.subheader("📈 Forecast Inflasi (3 Bulan ke Depan)")
st.caption("*Akan diganti model ML asli (Linear Regression / Random Forest)*")

# Forecast dummy dari tren 6 bulan terakhir
last_6 = df.tail(6)
trend = np.polyfit(range(6), last_6['inflasi_mtom'].values, 1)
forecast_vals = [trend[0] * (6 + i) + trend[1] for i in range(3)]
future_dates = pd.date_range(df['tanggal'].max() + pd.DateOffset(months=1), periods=3, freq='MS')

fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(x=df['tanggal'], y=df['inflasi_mtom'], name='Data Historis', line=dict(color='#6366f1', width=2)))
fig_fc.add_trace(go.Scatter(
    x=[df['tanggal'].iloc[-1]] + list(future_dates),
    y=[df['inflasi_mtom'].iloc[-1]] + forecast_vals,
    name='Forecast', mode='lines+markers',
    line=dict(color='#f59e0b', width=3, dash='dash'),
    marker=dict(size=8, symbol='diamond')
))
fig_fc.update_layout(
    title="Proyeksi Inflasi 3 Bulan ke Depan (Dummy)",
    height=400, yaxis_title="Inflasi MtM (%)",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
)
st.plotly_chart(fig_fc, use_container_width=True)

st.divider()

# ==========================================
# SIMULATOR WHAT-IF
# ==========================================
st.subheader("🎛️ Simulator What-If")
st.caption("Masukkan skenario ekonomi untuk memprediksi inflasi bulan depan menggunakan model Machine Learning.")

ci, _, co = st.columns([3, 0.5, 4])

with ci:
    minyak_in = st.slider("🛢️ Harga Minyak (USD/Barel)", 40.0, 130.0, float(df['harga_minyak_usd'].iloc[-1]), 0.5)
    kurs_in = st.slider("💵 Kurs USD/IDR", 13500, 18000, int(df['kurs_usd_idr'].iloc[-1]), 100)
    bbm_in = st.radio("⛽ Kebijakan Harga BBM Subsidi", ["Tetap", "Naik (+Rp 2.000)", "Turun (-Rp 2.000)"], horizontal=True)

with co:
    efek_m = (minyak_in - 70) * 0.015
    efek_k = (kurs_in - 14500) * 0.0003
    efek_b = 1.0 if "Naik" in bbm_in else (-0.4 if "Turun" in bbm_in else 0)
    pred = round(0.3 + efek_m + efek_k + efek_b, 2)

    st.metric("📈 Prediksi Inflasi Bulan Depan", f"{pred:.2f}%", f"{pred - df['inflasi_mtom'].iloc[-1]:+.2f}% vs data terakhir")

    st.markdown(f"""
    **Kontribusi per faktor:**
    - Harga Minyak → `{efek_m:+.3f}%`
    - Kurs USD/IDR → `{efek_k:+.3f}%`
    - Kebijakan BBM → `{efek_b:+.3f}%`
    """)

    if pred > 1.0:
        st.error(f"⚠️ Inflasi diprediksi **tinggi** ({pred:.2f}%).")
    elif pred > 0.5:
        st.warning(f"⚡ Inflasi **moderat** ({pred:.2f}%).")
    else:
        st.success(f"✅ Inflasi **rendah** ({pred:.2f}%). Stabil.")
