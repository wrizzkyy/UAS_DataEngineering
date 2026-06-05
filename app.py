import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Dashboard Inflasi Indonesia", layout="wide", page_icon="📈")

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80) # Ikon Data
    st.title("Panel Navigasi")
    st.write("Gunakan menu di bawah untuk mengatur filter data.")
    
    st.subheader("Filter Data")
    tahun_pilih = st.selectbox("Pilih Tahun:", ["Semua Tahun", "2024", "2023", "2022", "2021", "2020"])
    wilayah_pilih = st.selectbox("Wilayah:", ["INDONESIA (Nasional)", "MADIUN"])
    
    st.divider()
    st.caption("Status: 🟡 Menunggu Data Aiven")

# ==========================================
# HEADER
# ==========================================
st.title("📈 Dashboard BI & Forecasting Inflasi Indonesia")
st.markdown("*(Mode Dummy - Desain UI/UX)*")

# Membuat 2 Tab utama
tab1, tab2 = st.tabs(["📊 Dashboard BI Historis", "🔮 ML Forecasting Simulator"])

# ==========================================
# TAB 1: DASHBOARD BI HISTORIS
# ==========================================
with tab1:
    st.header("Kondisi Makroekonomi Saat Ini")
    
    # --- 1. KPI Cards (Lebih Rapi) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Inflasi Nasional (Bulan Ini)", value="2.85%", delta="-0.15% (Turun)")
    with col2:
        st.metric(label="Harga Minyak WTI (USD/Barel)", value="$82.50", delta="+$1.20 (Naik)")
    with col3:
        st.metric(label="Kurs (USD/IDR)", value="Rp 16.100", delta="-Rp 50 (Menguat)", delta_color="inverse")
    with col4:
        st.metric(label="Harga Pertalite", value="Rp 10.000", delta="Tetap", delta_color="off")
    
    st.divider()
    
    # --- 2. Chart Tren (Plotly Dual Axis - Lebih Profesional) ---
    st.subheader("Tren Historis Inflasi vs Harga Minyak")
    
    # Generate Dummy Data
    dummy_dates = pd.date_range(start='2022-01-01', periods=24, freq='ME')
    dummy_df = pd.DataFrame({
        'Tanggal': dummy_dates,
        'Inflasi (%)': np.random.uniform(2.0, 6.0, 24).round(2),
        'Harga Minyak ($)': np.random.uniform(70, 110, 24).round(2),
        'Kurs (Rp)': np.random.uniform(14500, 16500, 24).round(0)
    })
    
    # Membuat Chart Plotly dengan 2 Sumbu Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Tambahkan Garis Inflasi (Biru)
    fig.add_trace(
        go.Scatter(x=dummy_df['Tanggal'], y=dummy_df['Inflasi (%)'], name="Inflasi (%)", mode='lines+markers', line=dict(color='royalblue', width=3)),
        secondary_y=False,
    )
    
    # Tambahkan Garis Harga Minyak (Merah)
    fig.add_trace(
        go.Scatter(x=dummy_df['Tanggal'], y=dummy_df['Harga Minyak ($)'], name="Harga Minyak WTI ($)", mode='lines', line=dict(color='firebrick', width=2, dash='dot')),
        secondary_y=True,
    )
    
    # Konfigurasi Layout Chart
    fig.update_layout(
        title_text="Perbandingan Laju Inflasi dan Pergerakan Harga Minyak Dunia",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="<b>Inflasi</b> (%)", secondary_y=False)
    fig.update_yaxes(title_text="<b>Harga Minyak</b> ($)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- 3. Tabel Master Data ---
    st.subheader("Preview Dataset Master")
    st.dataframe(dummy_df.style.format({
        'Inflasi (%)': '{:.2f}%',
        'Harga Minyak ($)': '${:.2f}',
        'Kurs (Rp)': 'Rp {:,.0f}'
    }), use_container_width=True)


# ==========================================
# TAB 2: ML FORECASTING SIMULATOR
# ==========================================
with tab2:
    st.header("Simulator Prediksi Inflasi (What-If Analysis)")
    st.markdown("Uji coba model **Machine Learning (Random Forest/Linear Regression)** dengan memasukkan berbagai skenario ekonomi di masa depan.")
    
    st.write("---")
    
    col_input, col_output = st.columns([1.5, 2])
    
    with col_input:
        st.subheader("⚙️ Parameter Skenario")
        st.write("Sesuaikan *slider* di bawah ini:")
        
        minyak_input = st.slider("🛢️ Harga Minyak Dunia (USD/Barel)", min_value=40.0, max_value=120.0, value=85.0, step=0.5)
        kurs_input = st.slider("💵 Kurs (USD/IDR)", min_value=14000, max_value=17500, value=16200, step=100)
        bbm_input = st.selectbox("⛽ Status Harga BBM Subsidi (Pertalite)", ["Tetap (Rp 10.000)", "Naik (Rp 12.000)", "Turun (Rp 8.000)"])
        
    with col_output:
        st.subheader("📊 Hasil Prediksi Model")
        
        # Logic Dummy ML
        base_inflasi = 2.5
        pengaruh_minyak = (minyak_input - 80) * 0.04
        pengaruh_kurs = (kurs_input - 15000) * 0.001
        
        # Pengaruh BBM
        if "Naik" in bbm_input:
            pengaruh_bbm = 1.2
        elif "Turun" in bbm_input:
            pengaruh_bbm = -0.5
        else:
            pengaruh_bbm = 0
            
        prediksi_dummy = base_inflasi + pengaruh_minyak + pengaruh_kurs + pengaruh_bbm
        
        # Tampilan Hasil
        st.metric(label="Prediksi Inflasi Bulan Depan", value=f"{prediksi_dummy:.2f}%", delta=f"{prediksi_dummy - 2.85:.2f}% (Bandingkan dari bulan ini)")
        
        st.success(f"Berdasarkan skenario yang kamu atur, prediksi inflasi bulan depan akan **{'NAIK' if prediksi_dummy > 2.85 else 'TURUN'}** menjadi **{prediksi_dummy:.2f}%**.")
        
        st.markdown(f"""
        **🧠 Analisis Singkat dari Model:**
        - Harga minyak di **${minyak_input}** menyumbang sekitar `+{pengaruh_minyak:.2f}%` terhadap tekanan inflasi.
        - Nilai tukar di **Rp {kurs_input}** memberikan efek tekanan inflasi sebesar `+{pengaruh_kurs:.2f}%`.
        - Kebijakan BBM subsidi yang dipilih memberikan efek `+{pengaruh_bbm:.2f}%`.
        """)
