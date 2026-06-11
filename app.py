import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Konfigurasi Halaman (Mengatur judul tab browser dan membuat tampilan penuh/wide)
st.set_page_config(page_title="Forecasting Inflasi", layout="wide")

# ==========================================
# 1. MENGAMBIL DATA DARI AIVEN POSTGRESQL
# ==========================================
# @st.cache_data memastikan fungsi ini hanya berjalan sekali (di-cache) untuk menghemat loading
@st.cache_data
def load_data():
    """Mengambil dan melakukan pra-pemrosesan data mentah dari database."""
    # Load variabel environment dari file .env (jika dijalankan lokal)
    load_dotenv()
    
    # Mencoba mengambil kredensial database
    # Prioritas: st.secrets (jika di Streamlit Cloud) > os.getenv (jika di lokal)
    try:
        aiven_user = st.secrets.get("AIVEN_USER") or os.getenv("AIVEN_USER")
        aiven_password = st.secrets.get("AIVEN_PASSWORD") or os.getenv("AIVEN_PASSWORD")
        aiven_host = st.secrets.get("AIVEN_HOST") or os.getenv("AIVEN_HOST")
        aiven_port = st.secrets.get("AIVEN_PORT") or os.getenv("AIVEN_PORT")
        aiven_database = st.secrets.get("AIVEN_DATABASE") or os.getenv("AIVEN_DATABASE")
    except Exception:
        # Fallback jika st.secrets benar-benar tidak tersedia
        aiven_user = os.getenv("AIVEN_USER")
        aiven_password = os.getenv("AIVEN_PASSWORD")
        aiven_host = os.getenv("AIVEN_HOST")
        aiven_port = os.getenv("AIVEN_PORT")
        aiven_database = os.getenv("AIVEN_DATABASE")
    
    # Validasi: Pastikan semua kredensial tidak ada yang kosong
    if not all([aiven_user, aiven_password, aiven_host, aiven_port, aiven_database]):
        raise ValueError(
            "Database credentials tidak lengkap. "
            "Pastikan AIVEN_USER, AIVEN_PASSWORD, AIVEN_HOST, AIVEN_PORT, AIVEN_DATABASE tersedia."
        )
    
    # Membentuk string koneksi (Connection String) PostgreSQL menggunakan Psycopg2
    conn_str = (
        f"postgresql+psycopg2://{aiven_user}:{aiven_password}"
        f"@{aiven_host}:{aiven_port}"
        f"/{aiven_database}?sslmode=require"
    )
    
    # Membuat engine SQLAlchemy (jembatan penghubung Python ke Database) dengan batas waktu 10 detik
    engine = create_engine(conn_str, connect_args={"connect_timeout": 10})
    
    # Menarik seluruh data (Query SQL) dari tabel inflasi dan merubahnya menjadi DataFrame Pandas
    df_mentah = pd.read_sql("SELECT * FROM inflasi_minyak_indonesia", engine)
    
    # Agregasi (Grouping): Mengubah data dari tingkat kota menjadi rata-rata tingkat nasional per bulan
    df_nasional = (
        df_mentah.groupby(["tahun", "bulan"], as_index=False)
        .agg(
            inflasi_rata2     = ("inflasi_persen", "mean"),   # Rata-rata inflasi nasional
            harga_minyak_usd  = ("harga_minyak_usd", "first"), # Harga minyak dunia bulan itu
            kurs_usd_idr      = ("kurs_usd_idr", "first"),    # Kurs rupiah bulan itu
        )
        .sort_values(["tahun", "bulan"]) # Urutkan dari tahun terlama ke terbaru
        .reset_index(drop=True)
    )
    
    # Membuat kolom 'tanggal' format DateTime (Tahun-Bulan-01) untuk keperluan plot grafik
    df_nasional["tanggal"] = pd.to_datetime(
        df_nasional["tahun"].astype(str) + "-" + df_nasional["bulan"].astype(str) + "-01"
    )
    
    # Menghitung persentase perubahan harga minyak dari bulan ke bulan (Fitur yang sangat penting bagi model ML)
    df_nasional["perubahan_persen_minyak"] = df_nasional["harga_minyak_usd"].pct_change().fillna(0) * 100
    
    # Merubah nama kolom agar lebih mudah dipahami
    df_nasional.rename(columns={"inflasi_rata2": "inflasi_persen"}, inplace=True)
    
    return df_nasional

# Menjalankan fungsi load_data() dengan try-except untuk menangkap error koneksi
try:
    df = load_data()
except Exception as e:
    st.error(f"Koneksi database gagal: {e}")
    st.stop() # Hentikan aplikasi jika database mati

# ==========================================
# 2. MEMUAT MODEL MACHINE LEARNING
# ==========================================
# Menentukan lokasi folder 'models' relatif terhadap lokasi file app.py ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# @st.cache_resource memastikan model hanya diload 1x dari disk ke memory (bukan data, tapi objek Python)
@st.cache_resource
def load_saved_model():
    """Memuat model yang sudah dilatih (dari file .pkl)."""
    model_path = os.path.join(MODEL_DIR, "best_model.pkl")
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    
    # Validasi: Jika file tidak ada, lemparkan peringatan error yang jelas (karena ini wajib ada)
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError(
            "File model tidak ditemukan di folder 'models/'. "
            "Pastikan best_model.pkl dan scaler.pkl tersedia."
        )
    
    # Memuat algoritma Gradient Boosting dan objek Scaler menggunakan joblib
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler

# Memanggil fungsi pemuatan model
gb_model, scaler = load_saved_model()

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
    # Tautan eksternal ke dashboard reporting
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

# Membagi layar menjadi 2 kolom: Kiri untuk input slider, Kanan untuk hasil output
col_input, col_jarak, col_output = st.columns([3, 0.5, 4])

with col_input:
    # Mengambil nilai aktual terbaru (baris paling bawah) dari database sebagai nilai awal slider
    minyak_bulan_lalu = float(df['harga_minyak_usd'].iloc[-1])
    kurs_bulan_lalu = int(df['kurs_usd_idr'].iloc[-1])
    
    # Membuat komponen Slider interaktif
    minyak_in = st.slider("Harga Minyak Mentah (USD/Barel)", 40.0, 150.0, minyak_bulan_lalu, 0.5)
    kurs_in = st.slider("Nilai Tukar (USD/IDR)", 13500, 18000, kurs_bulan_lalu, 100)

with col_output:
    # Menghitung persentase perubahan harga minyak (Nilai Slider - Nilai Asli Bulan Lalu) / Nilai Asli Bulan Lalu
    if minyak_bulan_lalu != 0:
        perubahan_minyak_in = ((minyak_in - minyak_bulan_lalu) / minyak_bulan_lalu) * 100 
    else:
        perubahan_minyak_in = 0
    
    # Membungkus 3 fitur input ke dalam format DataFrame persis seperti saat model dilatih di notebook
    tabel_input = pd.DataFrame([{
        "harga_minyak_usd": minyak_in,
        "perubahan_persen_minyak": perubahan_minyak_in,
        "kurs_usd_idr": kurs_in
    }])
    
    # Pra-pemrosesan: Menyamakan skala nilai input (Scaling) agar sesuai standar pemahaman model
    input_scaled = scaler.transform(tabel_input)
    
    # Mengeksekusi model untuk melakukan prediksi (output berupa array, jadi diambil indeks [0])
    pred_final = round(gb_model.predict(input_scaled)[0], 2)
    inflasi_bulan_lalu = df['inflasi_persen'].iloc[-1]

    # Menampilkan hasil prediksi utama berupa metrik besar (Angka Inflasi dan Deltanya)
    st.metric("Proyeksi Inflasi Bulan Berikutnya", f"{pred_final:.2f}%", f"{pred_final - inflasi_bulan_lalu:+.2f}% dari bulan sebelumnya")

    # Menampilkan rincian tabel fitur yang masuk ke model sebagai transparansi (Explanatory Analytics)
    st.markdown("**Fitur yang Digunakan Model:**")
    df_rincian = pd.DataFrame({
        "Fitur": ["Harga Minyak Mentah", "Perubahan Harga Minyak", "Nilai Tukar (Kurs)"],
        "Nilai Input": [f"${minyak_in:.1f}/barel", f"{perubahan_minyak_in:+.2f}%", f"Rp {kurs_in:,}/USD"]
    })
    st.dataframe(df_rincian, hide_index=True, width='stretch')

    # Ambang batas status peringatan (disesuaikan agar lebih sensitif terhadap skenario ekstrem/krisis)
    if pred_final > 0.7:
        st.error("Peringatan: Risiko inflasi tinggi terdeteksi pada skenario ini.") # Merah (Bahaya)
    elif pred_final > 0.3:
        st.warning("Catatan: Tingkat inflasi berada pada level moderat.") # Kuning (Hati-hati)
    else:
        st.success("Status: Tingkat inflasi terkendali (rendah).") # Hijau (Aman)

st.divider()

# ==========================================
# 6. GRAFIK FORECAST TIGA BULAN
# ==========================================
st.subheader("Proyeksi Tren Inflasi (3 Bulan Kedepan)")
st.caption("Visualisasi linimasa hasil prediksi model berdasarkan skenario simulasi yang diterapkan.")

# Mengambil tanggal dari data paling akhir, dan meng-generate 3 rentang bulan ke depannya
tanggal_terakhir = df.iloc[-1]['tanggal']
tanggal_depan = pd.date_range(tanggal_terakhir + pd.DateOffset(months=1), periods=3, freq='MS')

# List untuk menyimpan hasil proyeksi 3 titik
hasil_tebakan_3_bulan = []
hasil_tebakan_3_bulan.append(pred_final) # Titik pertama adalah hasil kalkulasi di Panel Simulasi

# Loop simulasi bulan ke-2 dan bulan ke-3
for bulan_ke in range(1, 3):
    # Asumsi ekonomi stagnan (Ceteris Paribus): Harga minyak dan kurs diasumsikan konstan
    # (sama dengan nilai slider), sehingga persentase perubahan minyak dari bulan ke bulan = 0.0%
    tabel_pred = pd.DataFrame([{
        "harga_minyak_usd": minyak_in,
        "perubahan_persen_minyak": 0.0,
        "kurs_usd_idr": kurs_in
    }])
    
    # Skalasi input dan eksekusi prediksi model
    pred_scaled = scaler.transform(tabel_pred)
    tebakan_ml = gb_model.predict(pred_scaled)[0]
    hasil_tebakan_3_bulan.append(round(tebakan_ml, 2))

# Inisialisasi library grafik Plotly
fig_fc = go.Figure()

# GARIS 1: Menarik 12 data historis terakhir asli dari database (Garis Biru Solid)
df_sejarah = df.tail(12)
fig_fc.add_trace(go.Scatter(
    x=df_sejarah['tanggal'], 
    y=df_sejarah['inflasi_persen'], 
    name='Historis Tersimpan', 
    line=dict(color='#2563eb', width=2) # Biru profesional
))

# GARIS 2: Menggabungkan titik data historis terakhir dengan 3 titik proyeksi masa depan (Garis Oranye Putus-putus)
fig_fc.add_trace(go.Scatter(
    x=[df_sejarah['tanggal'].iloc[-1]] + list(tanggal_depan),
    y=[df_sejarah['inflasi_persen'].iloc[-1]] + hasil_tebakan_3_bulan,
    name='Proyeksi Model', mode='lines+markers',
    line=dict(color='#d97706', width=3, dash='dash'), # Oranye gelap profesional
    marker=dict(size=8, symbol='circle')
))

# Kustomisasi tata letak (Layout) grafik agar terlihat elegan
fig_fc.update_layout(
    title=f"Analisis Skenario Lanjutan (Basis Harga Minyak: ${minyak_in})",
    height=400, yaxis_title="Tingkat Inflasi (%)",
    hovermode="x unified", # Menyatukan pop-up detail saat mouse diarahkan ke garis
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"), # Meletakkan legenda di atas
    margin=dict(l=0, r=0, t=40, b=0)
)

# Render grafik Plotly ke dalam antarmuka Streamlit
st.plotly_chart(fig_fc, width='stretch')
