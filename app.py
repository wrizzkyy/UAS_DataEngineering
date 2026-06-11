import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

# Konfigurasi Halaman
st.set_page_config(page_title="Forecasting Inflasi", layout="wide")

# ==========================================
# 1. MENGAMBIL DATA DARI AIVEN POSTGRESQL
# ==========================================
@st.cache_data
def load_data():
    """Mengambil dan melakukan pra-pemrosesan data mentah dari database."""
    load_dotenv()
    
    # Prioritas: st.secrets (Streamlit Cloud) > os.getenv (local .env)
    try:
        aiven_user = st.secrets.get("AIVEN_USER") or os.getenv("AIVEN_USER")
        aiven_password = st.secrets.get("AIVEN_PASSWORD") or os.getenv("AIVEN_PASSWORD")
        aiven_host = st.secrets.get("AIVEN_HOST") or os.getenv("AIVEN_HOST")
        aiven_port = st.secrets.get("AIVEN_PORT") or os.getenv("AIVEN_PORT")
        aiven_database = st.secrets.get("AIVEN_DATABASE") or os.getenv("AIVEN_DATABASE")
    except Exception:
        # Fallback jika st.secrets tidak tersedia
        aiven_user = os.getenv("AIVEN_USER")
        aiven_password = os.getenv("AIVEN_PASSWORD")
        aiven_host = os.getenv("AIVEN_HOST")
        aiven_port = os.getenv("AIVEN_PORT")
        aiven_database = os.getenv("AIVEN_DATABASE")
    
    # Validasi environment variables
    if not all([aiven_user, aiven_password, aiven_host, aiven_port, aiven_database]):
        raise ValueError(
            "Database credentials tidak lengkap. "
            "Pastikan AIVEN_USER, AIVEN_PASSWORD, AIVEN_HOST, AIVEN_PORT, AIVEN_DATABASE tersedia."
        )
    
    conn_str = (
        f"postgresql+psycopg2://{aiven_user}:{aiven_password}"
        f"@{aiven_host}:{aiven_port}"
        f"/{aiven_database}?sslmode=require"
    )
    
    engine = create_engine(conn_str, connect_args={"connect_timeout": 10})
    df_mentah = pd.read_sql("SELECT * FROM inflasi_minyak_indonesia", engine)
    
    # Agregasi data tingkat kota menjadi agregasi bulanan tingkat nasional
    df_nasional = (
        df_mentah.groupby(["tahun", "bulan"], as_index=False)
        .agg(
            inflasi_rata2     = ("inflasi_persen", "mean"),
            harga_minyak_usd  = ("harga_minyak_usd", "first"),
            kurs_usd_idr      = ("kurs_usd_idr", "first"),
        )
        .sort_values(["tahun", "bulan"])
        .reset_index(drop=True)
    )
    
    # Format kolom tanggal
    df_nasional["tanggal"] = pd.to_datetime(
        df_nasional["tahun"].astype(str) + "-" + df_nasional["bulan"].astype(str) + "-01"
    )
    
    # Kalkulasi persentase perubahan harga minyak (Fitur ML)
    df_nasional["perubahan_persen_minyak"] = df_nasional["harga_minyak_usd"].pct_change().fillna(0) * 100
    df_nasional.rename(columns={"inflasi_rata2": "inflasi_persen"}, inplace=True)
    
    return df_nasional

try:
    df = load_data()
except Exception as e:
    st.error(f"Koneksi database gagal: {e}")
    st.stop()

# ==========================================
# 2. MELATIH MODEL MACHINE LEARNING
# ==========================================
@st.cache_resource
def train_model(data):
    """Melatih algoritma Gradient Boosting."""
    fitur_kolom = ["harga_minyak_usd", "perubahan_persen_minyak", "kurs_usd_idr"]
    target_kolom = "inflasi_persen"
    
    X = data[fitur_kolom].copy()
    y = data[target_kolom].copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    gb_model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )
    gb_model.fit(X_scaled, y)
    
    return gb_model, scaler

gb_model, scaler = train_model(df)

# ==========================================
# 3. TAMPILAN SIDEBAR
# ==========================================
with st.sidebar:
    st.subheader("Informasi Sistem")
    st.info("Koneksi Aiven PostgreSQL: Aktif")
    st.caption("Alur Pemrosesan Data (ETL):")
    st.markdown("""
    - **Ekstraksi**: Aiven PostgreSQL
    - **Transformasi**: Agregasi Pandas
    - **Visualisasi & ML**: Streamlit
    """)
    
    st.divider()
    st.subheader("Looker Studio")
    st.markdown("[Buka Dashboard Analisis Historis](https://datastudio.google.com/u/0/reporting/02a859af-c1e9-4960-864a-0a2b3949b3f3/page/wms0F)")

# ==========================================
# 4. JUDUL HALAMAN UTAMA
# ==========================================
st.title("Forecasting & Analisis Inflasi Indonesia")
st.markdown("Sistem analitik berbasis Machine Learning (Gradient Boosting Regressor) untuk memprediksi inflasi di Indonesia berdasarkan harga minyak mentah global dan nilai tukar Rupiah.")
st.divider()

# ==========================================
# 5. PANEL SIMULASI (WHAT-IF)
# ==========================================
st.subheader("Simulator Makroekonomi")
st.caption("Sesuaikan parameter di bawah ini untuk melihat proyeksi inflasi berdasarkan skenario ekonomi tertentu.")

col_input, col_jarak, col_output = st.columns([3, 0.5, 4])

with col_input:
    minyak_bulan_lalu = float(df['harga_minyak_usd'].iloc[-1])
    kurs_bulan_lalu = int(df['kurs_usd_idr'].iloc[-1])
    
    minyak_in = st.slider("Harga Minyak Mentah (USD/Barel)", 40.0, 150.0, minyak_bulan_lalu, 0.5)
    kurs_in = st.slider("Nilai Tukar (USD/IDR)", 13500, 18000, kurs_bulan_lalu, 100)
    bbm_in = st.radio("Penyesuaian Kebijakan BBM Subsidi", ["Tidak Ada", "Kenaikan (+Rp 2.000)", "Penurunan (-Rp 2.000)"], horizontal=True)

with col_output:
    if minyak_bulan_lalu != 0:
        perubahan_minyak_in = ((minyak_in - minyak_bulan_lalu) / minyak_bulan_lalu) * 100 
    else:
        perubahan_minyak_in = 0
    
    tabel_input = pd.DataFrame([{
        "harga_minyak_usd": minyak_in,
        "perubahan_persen_minyak": perubahan_minyak_in,
        "kurs_usd_idr": kurs_in
    }])
    
    input_scaled = scaler.transform(tabel_input)
    pred_dasar_ml = gb_model.predict(input_scaled)[0]
    
    if "Kenaikan" in bbm_in:
        efek_bbm = 1.0 
    elif "Penurunan" in bbm_in:
        efek_bbm = -0.4 
    else:
        efek_bbm = 0
        
    pred_final = round(pred_dasar_ml + efek_bbm, 2)
    inflasi_bulan_lalu = df['inflasi_persen'].iloc[-1]

    st.metric("Proyeksi Inflasi Bulan Berikutnya", f"{pred_final:.2f}%", f"{pred_final - inflasi_bulan_lalu:+.2f}% dari bulan sebelumnya")

    # Menampilkan rincian sebagai tabel agar lebih profesional
    st.markdown("**Dekonstruksi Model:**")
    df_rincian = pd.DataFrame({
        "Komponen Analisis": ["Prediksi Algoritma ML", "Faktor Penyesuaian BBM"],
        "Kontribusi": [f"{pred_dasar_ml:.2f}%", f"{efek_bbm:+.2f}%"]
    })
    st.dataframe(df_rincian, hide_index=True, width='stretch')

    if pred_final > 1.0:
        st.error("Peringatan: Risiko inflasi tinggi terdeteksi pada skenario ini.")
    elif pred_final > 0.5:
        st.warning("Catatan: Tingkat inflasi berada pada level moderat.")
    else:
        st.success("Status: Tingkat inflasi terkendali (rendah).")

st.divider()

# ==========================================
# 6. GRAFIK FORECAST TIGA BULAN
# ==========================================
st.subheader("Proyeksi Tren Inflasi (3 Bulan Kedepan)")
st.caption("Visualisasi linimasa hasil prediksi model berdasarkan skenario simulasi yang diterapkan.")

tanggal_terakhir = df.iloc[-1]['tanggal']
tanggal_depan = pd.date_range(tanggal_terakhir + pd.DateOffset(months=1), periods=3, freq='MS')

hasil_tebakan_3_bulan = []
hasil_tebakan_3_bulan.append(pred_final)

sim_minyak = minyak_in
sim_kurs = kurs_in

for bulan_ke in range(1, 3):
    minyak_sebelumnya = sim_minyak
    sim_minyak = sim_minyak + 0.5 
    sim_kurs = sim_kurs + 50
    
    perubahan_persen = ((sim_minyak - minyak_sebelumnya) / minyak_sebelumnya) * 100 if minyak_sebelumnya != 0 else 0
    
    tabel_pred = pd.DataFrame([{
        "harga_minyak_usd": sim_minyak,
        "perubahan_persen_minyak": perubahan_persen,
        "kurs_usd_idr": sim_kurs
    }])
    
    pred_scaled = scaler.transform(tabel_pred)
    tebakan_ml = gb_model.predict(pred_scaled)[0]
    
    sisa_efek_bbm = efek_bbm * (0.5 ** bulan_ke) 
    tebakan_total = tebakan_ml + sisa_efek_bbm
    hasil_tebakan_3_bulan.append(round(tebakan_total, 2))

fig_fc = go.Figure()

df_sejarah = df.tail(12)
fig_fc.add_trace(go.Scatter(
    x=df_sejarah['tanggal'], 
    y=df_sejarah['inflasi_persen'], 
    name='Historis Tersimpan', 
    line=dict(color='#2563eb', width=2) # Biru profesional
))

fig_fc.add_trace(go.Scatter(
    x=[df_sejarah['tanggal'].iloc[-1]] + list(tanggal_depan),
    y=[df_sejarah['inflasi_persen'].iloc[-1]] + hasil_tebakan_3_bulan,
    name='Proyeksi Model', mode='lines+markers',
    line=dict(color='#d97706', width=3, dash='dash'), # Oranye gelap profesional
    marker=dict(size=8, symbol='circle')
))

fig_fc.update_layout(
    title=f"Analisis Skenario Lanjutan (Basis Harga Minyak: ${minyak_in})",
    height=400, yaxis_title="Tingkat Inflasi (%)",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig_fc, width='stretch')
