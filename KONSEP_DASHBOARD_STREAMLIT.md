# Draft Konsep Dashboard BI & Machine Learning (Streamlit)

Dokumen ini berisi rancangan ide untuk pembuatan Dashboard interaktif menggunakan Streamlit. Pengerjaan dashboard ini (oleh Alvin/Hanif) akan dieksekusi setelah tim Data Engineer menyelesaikan proses Pipeline ETL dan menaikkan data ke Aiven PostgreSQL.

## Struktur Halaman Dashboard

Dashboard akan dibagi menjadi dua Tab/Halaman utama:

### 💡 Tab 1: Dashboard BI Historis (Melihat Masa Lalu)
Menampilkan data historis yang ditarik secara *real-time* dari database Aiven PostgreSQL.
*   **KPI Cards:** Menampilkan metrik utama bulan terakhir (Inflasi, Harga Minyak, Kurs USD/IDR) dengan indikator naik/turun (hijau/merah).
*   **Grafik Tren Interaktif (Line Chart):** Grafik garis (misal menggunakan *Plotly*) yang menunjukkan pergerakan Inflasi vs Harga Minyak dari awal data (misal 2020) hingga sekarang. Bisa di-zoom dan interaktif.
*   **Tabel Master Data:** Menampilkan *preview* `df_master` yang ada di database Aiven agar dosen bisa melihat wujud datanya.

### 💡 Tab 2: Machine Learning & Forecasting (Simulator Masa Depan)
Mendemonstrasikan model Machine Learning yang telah dibuat untuk memprediksi inflasi.
*   **Fitur A: Grafik Forecast (Time Series):** Menampilkan grafik garis lanjutan yang berisi tebakan model ML untuk inflasi 3 hingga 6 bulan ke depan berdasarkan *trend* yang ada.
*   **Fitur B: Simulator "What-If" (Jika... Maka...):** Panel interaktif berisi input form / *slider* di mana pengguna bisa mensimulasikan kondisi ekonomi:
    *   *Slider* Harga Minyak (USD/Barel)
    *   *Slider* Kurs (USD/IDR)
    *   *Input* Harga BBM (Pertalite)
    *   **Output:** Saat *slider* digeser, model ML akan langsung berjalan di latar belakang dan memunculkan angka prediksi inflasi saat itu juga. (Misal: *"Jika minyak $90 dan kurs Rp 16.500, prediksi inflasi = 3.5%"*).

---

## Status Pekerjaan Saat Ini (Blocker)

Bagian pembuatan Dashboard ini statusnya **MENUNGGU (PENDING)**. 
Kita baru bisa mulai membangun dashboard dan mengkoneksikannya jika proses berikut sudah selesai:
1. [ ] **ETL Selesai:** Dataset master (`df_master`) gabungan dari Inflasi, Harga Minyak, Kurs, dan BBM sudah berhasil dibersihkan di Jupyter Notebook.
2. [ ] **Aiven Database Ready:** Data `df_master` tersebut sudah berhasil di-*upload* / di-*load* ke database PostgreSQL di Aiven.
3. [ ] **Model ML (Hanif):** Logic algoritma *Machine Learning* untuk prediksi sudah difinalisasi.
