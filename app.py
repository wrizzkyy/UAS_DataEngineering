import streamlit as st
import pandas as pd
import numpy as np

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Dashboard Inflasi Indonesia", layout="wide", page_icon="📈")

st.title("📈 Dashboard BI & Forecasting Inflasi Indonesia")
st.markdown("*(Status: Mode Dummy - Sedang menunggu integrasi Pipeline Aiven)*")

# Membuat 2 Tab utama sesuai konsep
tab1, tab2 = st.tabs(["📊 Dashboard BI Historis", "🔮 ML Forecasting Simulator"])

# ==========================================
# TAB 1: DASHBOARD BI HISTORIS
# ==========================================
with tab1:
    st.header("Kondisi Makroekonomi Saat Ini")
    st.info("💡 Nantinya data di halaman ini akan di-query langsung secara real-time dari database Aiven PostgreSQL.")
    
    # --- 1. KPI Cards (Dummy) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Inflasi Bulan Terakhir", "2.8%", "-0.2%")
    col2.metric("Harga Minyak (WTI)", "$82.50", "+$1.20")
    col3.metric("Kurs USD/IDR", "Rp 16,100", "+Rp 50")
    
    st.divider()
    
    # --- 2. Chart Tren (Dummy) ---
    st.subheader("Tren Historis Inflasi (Dummy Data)")
    # Membuat data acak untuk visualisasi sementara
    dummy_dates = pd.date_range(start='2023-01-01', periods=12, freq='ME')
    dummy_data = pd.DataFrame({
        'Tanggal': dummy_dates,
        'Inflasi (%)': np.random.uniform(2.0, 5.0, 12),
    })
    st.line_chart(dummy_data.set_index('Tanggal'))
    
    # --- 3. Tabel Master Data (Dummy) ---
    st.subheader("Preview Dataset Master (Dummy)")
    st.dataframe(dummy_data, use_container_width=True)


# ==========================================
# TAB 2: ML FORECASTING SIMULATOR
# ==========================================
with tab2:
    st.header("Simulator Prediksi Inflasi (What-If Analysis)")
    st.info("💡 Nantinya input dari slider ini akan diumpankan ke model Machine Learning (Linear Regression/Random Forest) buatan Hanif.")
    
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        st.subheader("Parameter Input")
        st.write("Silakan geser parameter berikut:")
        
        minyak_input = st.slider("Harga Minyak Dunia (USD/Barel)", min_value=40.0, max_value=120.0, value=80.0, step=0.5)
        kurs_input = st.slider("Kurs (USD/IDR)", min_value=14000, max_value=17500, value=16000, step=100)
        bbm_input = st.number_input("Harga Pertalite (Rp/Liter)", value=10000, step=500)
        
    with col_output:
        st.subheader("Hasil Prediksi Model")
        
        # Logic Dummy untuk simulasi pergerakan angka prediksi
        base_inflasi = 2.5
        pengaruh_minyak = (minyak_input - 80) * 0.05
        pengaruh_kurs = (kurs_input - 15000) * 0.001
        prediksi_dummy = base_inflasi + pengaruh_minyak + pengaruh_kurs
        
        # Tampilan Hasil
        st.success(f"📈 Prediksi Inflasi bulan depan adalah: **{prediksi_dummy:.2f}%**")
        
        st.markdown(f"""
        **Interpretasi (Contoh):** 
        Jika harga minyak menyentuh **${minyak_input}** dan nilai tukar dolar melemah di angka **Rp {kurs_input}**, maka model Machine Learning memperkirakan tingkat inflasi Indonesia akan berada di kisaran **{prediksi_dummy:.2f}%**.
        """)
