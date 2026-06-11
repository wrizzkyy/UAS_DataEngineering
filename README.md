# DATA-ENGINEERING

# Proyek : Pengaruh Harga Minyak Mentah Global terhadap Inflasi di Indonesia

---

## Kontributor

| Nama Lengkap                     | NIM | Peran               |
|----------------------------------|-----|---------------------|
| Mohammad Hanif Huda Afrizal      | -   | Data Engineer       |
| Achmad Alvin Al Falah            | -   | Data Analyst        |
| Fachrozzi Rizky Wibowo           | -   | Project Manager     |

---

## Deskripsi Proyek
Project ini dikembangkan untuk mengidentifikasi hubungan antara harga minyak mentah global, nilai tukar USD/IDR, dan tingkat inflasi di Indonesia. Tujuannya adalah menyediakan pipeline ETL yang membersihkan, menggabungkan, dan memproses data ekonomi dari sumber terbuka, lalu membangun model prediksi inflasi yang dapat digunakan untuk analisis kebijakan dan visualisasi interaktif.

Proyek juga menekankan transformasi data menjadi format yang dapat dimuat ke database PostgreSQL, serta menyajikan hasil melalui aplikasi Streamlit dan notebook analisis.

---

## Manfaat Data / Use Case
- **Tujuan Proyek:** Menyediakan data terintegrasi yang menggambarkan hubungan antara harga minyak, kurs USD/IDR, dan inflasi Indonesia.
- **Manfaat:**
  - Menyediakan sumber data yang telah melalui proses validasi dan transformasi, sehingga siap digunakan untuk studi lanjutan.
  - Mendukung pengembangan model prediktif untuk mitigasi risiko inflasi.
  - Hasil ETL proyek ini mendukung dashboard visualisasi interaktif dan analisis tren makroekonomi.

---

## Serving Analisis
Data hasil ETL disimpan dalam database PostgreSQL Aiven dan dapat diakses untuk eksplorasi lanjutan melalui Google Colab atau aplikasi Streamlit.
Penyimpanan ini memungkinkan analisis korelasi, distribusi inflasi, dan pemantauan perubahan nilai tukar serta harga minyak.

## Serving Machine Learning
Dataset bersih digunakan untuk membangun model prediksi inflasi menggunakan machine learning.
Proyek ini mengimplementasikan Gradient Boosting Regressor dan scaler untuk preprocessing fitur.
Model disimpan di folder `models/` dan digunakan oleh `app.py` untuk simulasi prediksi inflasi.

---

# Pipeline
## Extract (Pengambilan Data)
- **Sumber Data:**
  - Harga minyak mentah global – `data/crude-oil-price.csv`
  - Inflasi bulanan Indonesia – file CSV `Inflasi Bulanan (M-to-M), YYYY.csv`
  - Nilai tukar USD/IDR disertakan dalam dataset yang sama

- **Metode Pengambilan:**
  - Pembacaan CSV menggunakan `pandas.read_csv()`
  - Akses data SQL melalui koneksi Aiven PostgreSQL untuk aplikasi Streamlit

---

## Transform (Pembersihan & Transformasi)
- **Pembersihan:**
  - Menghapus kolom dan baris kosong (`dropna()`)
  - Menyelaraskan nama kolom dan format tanggal
  - Memastikan tipe data numerik konsisten untuk analisis

- **Transformasi:**
  - Menggabungkan data inflasi, harga minyak, dan kurs berdasarkan tahun dan bulan
  - Menghitung `perubahan_persen_minyak` sebagai fitur utama
  - Mengonversi hasil agregasi ke bentuk yang siap dimuat ke database

---

## Load (Pemindahan ke Target)
- **Target:**
  - Tabel baru di database PostgreSQL Aiven, sebagai sumber data untuk visualisasi dan analisis.

- **Metode:**
  - `DataFrame.to_sql()` dari Pandas untuk menulis data ke database
  - Koneksi dibuat menggunakan SQLAlchemy dan kredensial environment
  - Verifikasi dilakukan dengan `pd.read_sql()` dan `df.head()`

---

## Arsitektur / Workflow ETL
- **Alur Modular:**
  - Proses ETL diorganisir ke dalam fungsi terpisah untuk ekstraksi, transformasi, dan pemuatan.
  - `app.py` menampilkan hasil simulasi dan menggunakan model yang sudah dilatih.

- **Tools yang Digunakan:**
  - Python 3.x
  - Library: `pandas`, `numpy`, `sqlalchemy`, `matplotlib`, `seaborn`, `scikit-learn`, `joblib`, `streamlit`, `plotly`
  - Database: PostgreSQL Aiven

---

## Kode Program
- **Struktur Kode:**
  - `ETL_Harga_Minyak_Inflasi_Indonesia.ipynb` untuk pipeline ETL
  - `Prediksi_Inflasi_Model.ipynb` untuk pengembangan model ML
  - `app.py` untuk aplikasi Streamlit dan prediksi live

- **Machine Learning:**
  - Model utama: Gradient Boosting Regressor
  - Fitur: harga minyak mentah, perubahan harga minyak, kurs USD/IDR
  - Evaluasi: model disimpan dalam `models/best_model.pkl` dan scaler di `models/scaler.pkl`

---

## Cara Menjalankan
1. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run app.py
   ```
3. Buka notebook untuk eksplorasi ETL dan model.

---

## Struktur Folder
- `app.py` - aplikasi Streamlit untuk prediksi inflasi
- `ETL_Harga_Minyak_Inflasi_Indonesia.ipynb` - notebook ETL
- `Prediksi_Inflasi_Model.ipynb` - notebook machine learning
- `data/` - dataset input
- `models/` - model dan scaler yang disimpan
- `requirements.txt` - dependensi Python
