## Project Information

**Project Name**: the Impact of Global Crude Oil Prices on Indonesia's Inflation
**Created By**: Data Engineering Team 6
**Date**: February 10, 2026
**Version**: 1.0

## 1. Executive Summary

### 1.1 Project Overview

- **Tujuan Project**: Mengembangkan sistem analitik untuk mempredisiksi inflasi berdasarkan harga minyak mentah global
- **Scope Project**: Integrasi data harga minyak mentah global, dan inflasi di Indonesia
- **Expected Outcomes**: Analisis hubungan antara harga minyak mentah global dan inflasi di Indonesia
- **Timeline**: 5 bulan (Februari - Juni 2026)

### 1.2 Stakeholders

- **Project Owner**: Mahasiswa Politeknik Negeri Madiun jurusan TRPL
- **Team Members**:
  - Data Engineer: Mohammad Hanif Huda Afrizal
  - Data Analyst: Achmad Alvin Al Falah
  - Project Manager: Fachrozzi Rizky Wibowo
- **End Users**:
  - Pemerintah Daerah
  - Masyarakat umum

## 2. Data Source Analysis

### 2.1 Data Pemerintah (Open Data BPS)

#### Source Details

- **Dataset Name**: Inflasi Bulanan (M-to-M) 2020-2026
- **URL/Access Point**: https://www.bps.go.id/id/statistics-table/2/MSMy/inflasi-bulanan-m-to-m-.html
- **Data Owner**: Badan Pusat Statistik (BPS) Republik Indonesia
- **Update Frequency**: Bulanan

#### Data Analysis

- **Format Data**: CSV
- **Volume Data**: 69.4 KB (7 file CSV)
- **Time Coverage**: Data persentase inflasi dengan rincian per bulan (Januari - Desember).
- **Data Quality**:
  - Completeness: Sangat Tinggi. Meliputi data pergerakan persentase inflasi bulanan (Month-to-Month) secara lengkap untuk puluhan kota/kabupaten pengukur inflasi di Indonesia.
  - Accuracy: Sangat Tinggi. Merupakan data Indeks Harga Konsumen (IHK) resmi yang dirilis oleh negara.
  - Consistency: Sangat Baik. Format tabel konsisten menyajikan daftar kota/kabupaten yang disandingkan dengan nilai inflasi tiap bulannya.
  - Timeliness: Up-to-date dan rutin diterbitkan oleh BPS setiap awal bulan berikutnya.

### 2.2 Open Data Website

#### Source Details

- **Dataset Name**: Crude Oil Price WTI
- **URL/Access Point**: https://www.macrotrends.net/1369/crude-oil-price-history-chart
- **Creator/Publisher**: Macrotrends LLC (sumber primer: U.S. EIA – Energy Information Administration)
- **Update Frequency:**: Bulanan 

#### Data Analysis

- **Format Data**: CSV
- **Size & Dimensions**: ±18 KB
- **Data Fields**:
  - date
  - value
- **Quality Metrics**:
  - Missing Values: Tidak ada 
  - Data Types: Properly formatted
  - Consistency: High
  - Documentation Quality: Excellent

### 2.3 Public APIs

#### Source Details

- **API Name**: exchange-api
- **Endpoint URL**: https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{YYYY-MM-DD}/v1/currencies/usd.json
- **Provider**: fawazahmed0 (github)
- **Authentication Method**: API Key

#### API Analysis

- **Response Format**: JSON
- **Rate Limits**: No Limit
- **Reliability**: 99.9% uptime
- **Documentation Quality**: Comprehensive
- **Cost**: Free

### 2.4 Open Report Data

#### Source Details

- **Dataset Name**: Laporan Kinerja (LAKIN) Direktorat Jenderal Minyak dan Gas Bumi, Kementerian ESDM Tahun 2022
- **Repository**: https://migas.esdm.go.id/cms/uploads/uploads/LAKIN-Ditjen-Migas-2022-24Feb2023-Final.pdf
- **Report Department**: Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia
- **Publication Date**: 2022

#### Data Analysis

- **Format & Structure**: PDF
- **Data Volume**: ±15 MB
- **Data Quality**: Peer-reviewed