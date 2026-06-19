import streamlit as st
import sqlite3
import pandas as pd
import datetime
import time

# --- SAYFA AYARLARI & GÖRSEL TEMA (AGRESİF KIRMIZI & SİYAH CSS) ---
st.set_page_config(page_title="PR Kampanya & Borç Otomasyonu", layout="wide")

st.markdown("""
    <style>
    /* Tam Karanlık Saf Siyah Arka Plan */
    .stApp {
        background-color: #090b0f !important;
        color: #f3f4f6 !important;
    }
    /* Form Alanı ve Kutular (Koyu Gri Üzerine Kırmızı Detay) */
    div[data-testid="stForm"] {
        background-color: #121620 !important;
        border: 2px solid #dc2626 !important; /* Canlı Kırmızı */
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px rgba(220, 38, 38, 0.2);
    }
    /* Canlı Kırmızı Premium Butonlar */
    .stButton>button, div[data-testid="stDownloadButton"]>button {
        background: linear-gradient(90deg, #991b1b 0%, #dc2626 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 15px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover, div[data-testid="stDownloadButton"]>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.5);
        color: #ffffff !important;
    }
    /* Seçim Kutuları ve Metin Alanları (Maviyi Tamamen Yok Etme) */
    input, select, textarea, div[role="listbox"] {
        background-color: #1b202e !important;
        color: #f3f4f6 !important;
        border: 1px solid #4b5563 !important;
    }
    input:focus, select:focus, textarea:focus {
        border-color: #dc2626 !important;
        box-shadow: 0 0 0 1px #dc2626 !important;
    }
    /* Başlık Alanları (Kırmızı) */
    h1, h2, h3 {
        color: #dc2626 !important;
        font-family: 'Segoe UI', sans-serif;
        text-shadow: 0px 2px 8px rgba(220, 38, 38, 0.3);
    }
    /* Giriş Alanı Etiketleri */
    label {
        color: #e5e7eb !important;
        font-weight: 500 !important;
    }
    /* Rapor Odasındaki Metrik Kutuları */
    div[data-testid="stMetricValue"] {
        color: #dc2626 !important;
    }
    /* Üst Sekme Çizgileri ve Seçimleri */
    button[data-baseweb="tab"] {
        color: #9ca3af !important;
    }
    button[aria-selected="true"] {
        color: #dc2626 !important;
        border-bottom-color: #dc
