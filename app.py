import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Library untuk nyambung ke database
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Library untuk Machine Learning
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

# Mengatur tampilan halaman web Streamlit
st.set_page_config(page_title="Forecasting Inflasi Indonesia", layout="wide", page_icon="🔮")

# ==========================================
# 1. MENGAMBIL DATA DARI AIVEN POSTGRESQL
# ==========================================
# @st.cache_data fungsinya agar data disimpan di memori sementara.
# Jadi kalau kita geser-geser slider, webnya gak lemot narik data terus dari DB.
@st.cache_data
def load_data():
    """Fungsi ini untuk mengambil data mentah dari DB dan merapikannya"""
    
    # Membaca password database dari file rahasia (.env)
    load_dotenv()
    conn_str = (
        f"postgresql+psycopg2://{os.getenv('AIVEN_USER')}:{os.getenv('AIVEN_PASSWORD')}"
        f"@{os.getenv('AIVEN_HOST')}:{os.getenv('AIVEN_PORT')}"
        f"/{os.getenv('AIVEN_DATABASE')}?sslmode=require"
    )
    
    # Membuat mesin penghubung ke database
    engine = create_engine(conn_str, connect_args={"connect_timeout": 10})
    
    # Download semua isi tabel menggunakan Pandas SQL
    df_mentah = pd.read_sql("SELECT * FROM inflasi_minyak_indonesia", engine)
    
    # Mengelompokkan (Group By) data kota-kota menjadi data rata-rata Nasional per bulan
    df_nasional = (
        df_mentah.groupby(["tahun", "bulan"], as_index=False)
        .agg(
            inflasi_rata2     = ("inflasi_persen", "mean"),   # Cari rata-rata inflasi
            harga_minyak_usd  = ("harga_minyak_usd", "first"), # Ambil harga minyak bulan itu
            kurs_usd_idr      = ("kurs_usd_idr", "first"),     # Ambil harga kurs bulan itu
        )
        .sort_values(["tahun", "bulan"]) # Urutkan dari tahun tertua ke terbaru
        .reset_index(drop=True)
    )
    
    # Bikin kolom tanggal baru gabungan dari tahun dan bulan (biar gampang dibikin grafik)
    df_nasional["tanggal"] = pd.to_datetime(
        df_nasional["tahun"].astype(str) + "-" + df_nasional["bulan"].astype(str) + "-01"
    )
    
    # MACHINE LEARNING BUTUH KOLOM "PERSENTASE NAIK-TURUN HARGA MINYAK"
    # Di Pandas ada rumus cepatnya yaitu pct_change() lalu dikali 100
    df_nasional["perubahan_persen_minyak"] = df_nasional["harga_minyak_usd"].pct_change().fillna(0) * 100
    
    # Ganti nama kolom "inflasi_rata2" jadi "inflasi_persen" biar gampang dibaca
    df_nasional.rename(columns={"inflasi_rata2": "inflasi_persen"}, inplace=True)
    
    return df_nasional

# Coba jalankan fungsi load_data() di atas
try:
    df = load_data()
except Exception as e:
    st.error(f"Waduh, gagal narik data dari database nih! Error: {e}")
    st.stop()


# ==========================================
# 2. MELATIH MODEL MACHINE LEARNING (TRAINING)
# ==========================================
# @st.cache_resource fungsinya agar otak ML-nya diingat terus dan tidak perlu belajar ulang dari nol
@st.cache_resource
def train_model(data):
    """Fungsi ini menyuruh algoritma belajar mengenali pola inflasi"""
    
    # 3 Faktor penentu (Input/X)
    fitur_kolom = ["harga_minyak_usd", "perubahan_persen_minyak", "kurs_usd_idr"]
    
    # Hasil akhir yang mau ditebak (Target/Y)
    target_kolom = "inflasi_persen"
    
    X = data[fitur_kolom].copy()
    y = data[target_kolom].copy()
    
    # Karena harga minyak kecil ($60) dan kurs gede banget (Rp 15000), 
    # kita harus samakan skalanya biar adil pakai StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Kita pilih algoritma pintar bernama Gradient Boosting
    gb_model = GradientBoostingRegressor(
        n_estimators=200,    # Belajar mengulang sebanyak 200 kali
        learning_rate=0.05,  # Kecepatan belajar (pelan-pelan asal teliti)
        max_depth=5,         # Batas kedalaman berpikir
        random_state=42
    )
    
    # Mulai proses belajar (Fit)
    gb_model.fit(X_scaled, y)
    
    # Kembalikan otak ML yang sudah pintar (gb_model) dan timbangan skalanya (scaler)
    return gb_model, scaler

# Panggil fungsi training-nya
gb_model, scaler = train_model(df)


# ==========================================
# 3. MEMBUAT TAMPILAN SIDEBAR DI KIRI
# ==========================================
with st.sidebar:
    st.header("⚙️ Konfigurasi")

    st.caption("📡 Sumber Data")
    st.code("Aiven PostgreSQL\n→ Data Agregasi Bulanan\n→ Streamlit", language="text")
    st.success("✅ Terhubung ke Aiven PostgreSQL.", icon="✅")

    st.divider()
    st.caption("📊 Dashboard BI")
    st.markdown("[Buka di Looker Studio →](https://datastudio.google.com/u/0/reporting/02a859af-c1e9-4960-864a-0a2b3949b3f3/page/wms0F)")


# ==========================================
# 4. JUDUL UTAMA HALAMAN
# ==========================================
st.markdown("## 🔮 Forecasting & Prediksi Inflasi Indonesia")
st.caption("Machine Learning (Gradient Boosting) untuk prediksi inflasi berdasarkan harga minyak global, kurs USD/IDR, dan kebijakan BBM.")


# ==========================================
# 5. PANEL KENDALI (SIMULATOR WHAT-IF)
# ==========================================
st.subheader("🎛️ Simulator What-If")
st.caption("Ubah angka di bawah ini untuk mensimulasikan masa depan. Hasilnya akan otomatis tergambar di grafik.")

# Membagi layar jadi 3 kolom (kiri 3, tengah spasi 0.5, kanan 4)
ci, _, co = st.columns([3, 0.5, 4])

# BAGIAN KIRI (INPUT SLIDER)
with ci:
    # Ambil harga minyak bulan terakhir dari database untuk jadi patokan slider
    minyak_bulan_lalu = float(df['harga_minyak_usd'].iloc[-1])
    kurs_bulan_lalu = int(df['kurs_usd_idr'].iloc[-1])
    
    minyak_in = st.slider("🛢️ Harga Minyak (USD/Barel)", 40.0, 150.0, minyak_bulan_lalu, 0.5)
    kurs_in = st.slider("💵 Kurs USD/IDR", 13500, 18000, kurs_bulan_lalu, 100)
    bbm_in = st.radio("⛽ Kebijakan Harga BBM Subsidi", ["Tetap", "Naik (+Rp 2.000)", "Turun (-Rp 2.000)"], horizontal=True)

# BAGIAN KANAN (HASIL PREDIKSI)
with co:
    # Langkah 1: Hitung Persen Perubahan Minyak dari bulan lalu ke angka simulasi
    if minyak_bulan_lalu != 0:
        perubahan_minyak_in = ((minyak_in - minyak_bulan_lalu) / minyak_bulan_lalu) * 100 
    else:
        perubahan_minyak_in = 0
    
    # Langkah 2: Bungkus 3 angka inputan tadi jadi sebuah tabel mini
    tabel_input = pd.DataFrame([{
        "harga_minyak_usd": minyak_in,
        "perubahan_persen_minyak": perubahan_minyak_in,
        "kurs_usd_idr": kurs_in
    }])
    
    # Langkah 3: Samakan timbangan skalanya, lalu suruh ML memprediksi (Predict)
    input_scaled = scaler.transform(tabel_input)
    pred_dasar_ml = gb_model.predict(input_scaled)[0]
    
    # Langkah 4: Tambahkan Efek Kaget Kebijakan BBM secara manual
    # Kalau BBM naik, tambah inflasi 1.0%. Kalau turun kurangi 0.4%
    if "Naik" in bbm_in:
        efek_bbm = 1.0 
    elif "Turun" in bbm_in:
        efek_bbm = -0.4 
    else:
        efek_bbm = 0
        
    # Hasil akhir = Prediksi ML Murni + Efek Kaget BBM
    pred_final = round(pred_dasar_ml + efek_bbm, 2)
    
    inflasi_bulan_lalu = df['inflasi_persen'].iloc[-1]

    # Tampilkan angka besar (Metric)
    st.metric("📈 Prediksi Inflasi Bulan Depan", f"{pred_final:.2f}%", f"{pred_final - inflasi_bulan_lalu:+.2f}% vs bulan lalu")

    st.markdown(f"""
    **Rincian Hasil Tebakan:**
    - Tebakan ML Murni (Efek Minyak & Kurs) → `{pred_dasar_ml:.2f}%`
    - Tambahan Kaget BBM (Manual) → `{efek_bbm:+.2f}%`
    """)

    # Beri warna merah/kuning/hijau tergantung bahayanya
    if pred_final > 1.0:
        st.error(f"⚠️ Bahaya! Inflasi diprediksi **tinggi** ({pred_final:.2f}%).")
    elif pred_final > 0.5:
        st.warning(f"⚡ Hati-hati. Inflasi **moderat** ({pred_final:.2f}%).")
    else:
        st.success(f"✅ Aman. Inflasi **rendah dan stabil** ({pred_final:.2f}%).")

st.divider()


# ==========================================
# 6. GRAFIK FORECAST (MENGGAMBAR MASA DEPAN)
# ==========================================
st.subheader("📈 Forecast Inflasi (3 Bulan ke Depan)")
st.caption("*Grafik garis putus-putus ini mengikuti skenario What-If yang kamu pilih di atas.*")

# Ambil tanggal terakhir, lalu siapkan 3 tanggal baru untuk bulan ke depan
tanggal_terakhir = df.iloc[-1]['tanggal']
tanggal_depan = pd.date_range(tanggal_terakhir + pd.DateOffset(months=1), periods=3, freq='MS')

# Tempat menampung hasil tebakan 3 bulan
hasil_tebakan_3_bulan = []

# --- Prediksi Bulan 1 ---
# Kita langsung pakai angka hasil dari What-If di atas
hasil_tebakan_3_bulan.append(pred_final)

# --- Prediksi Bulan 2 & 3 ---
# Biar grafiknya gak jadi garis datar, kita buat skenario minyaknya perlahan naik 
sim_minyak = minyak_in
sim_kurs = kurs_in

for bulan_ke in range(1, 3):
    minyak_sebelumnya = sim_minyak
    
    # Asumsi: Tiap bulan harga minyak merayap naik $0.5, kurs melemah Rp50
    sim_minyak = sim_minyak + 0.5 
    sim_kurs = sim_kurs + 50
    
    # Hitung persen perubahan
    perubahan_persen = ((sim_minyak - minyak_sebelumnya) / minyak_sebelumnya) * 100 if minyak_sebelumnya != 0 else 0
    
    # Bungkus jadi tabel mini
    tabel_pred = pd.DataFrame([{
        "harga_minyak_usd": sim_minyak,
        "perubahan_persen_minyak": perubahan_persen,
        "kurs_usd_idr": sim_kurs
    }])
    
    # Tebak hasilnya
    pred_scaled = scaler.transform(tabel_pred)
    tebakan_ml = gb_model.predict(pred_scaled)[0]
    
    # Teori Ekonomi: Efek kaget harga BBM akan berkurang setengahnya di bulan-bulan berikutnya
    sisa_efek_bbm = efek_bbm * (0.5 ** bulan_ke) 
    
    tebakan_total = tebakan_ml + sisa_efek_bbm
    hasil_tebakan_3_bulan.append(round(tebakan_total, 2))


# MENGGAMBAR GRAFIK DENGAN PLOTLY
fig_fc = go.Figure()

# Menggambar Garis Biru (Sejarah Masa Lalu) - Ambil 12 bulan terakhir saja biar rapi
df_sejarah = df.tail(12)
fig_fc.add_trace(go.Scatter(
    x=df_sejarah['tanggal'], 
    y=df_sejarah['inflasi_persen'], 
    name='Sejarah Asli', 
    line=dict(color='#6366f1', width=2)
))

# Menggambar Garis Oranye (Tebakan Masa Depan)
fig_fc.add_trace(go.Scatter(
    x=[df_sejarah['tanggal'].iloc[-1]] + list(tanggal_depan),
    y=[df_sejarah['inflasi_persen'].iloc[-1]] + hasil_tebakan_3_bulan,
    name='Tebakan Model ML', mode='lines+markers',
    line=dict(color='#f59e0b', width=3, dash='dash'),
    marker=dict(size=8, symbol='diamond')
))

# Merapikan tampilan grafik
fig_fc.update_layout(
    title=f"Proyeksi Garis Inflasi jika Harga Minyak Sentuh ${minyak_in}",
    height=400, yaxis_title="Inflasi (%)",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
)

# Tampilkan ke layar Streamlit
st.plotly_chart(fig_fc, use_container_width=True)
