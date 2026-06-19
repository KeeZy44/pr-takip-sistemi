import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Sayfa Ayarları
st.set_page_config(page_title="PR Kampanya & Borç Otomasyonu", layout="wide")

# --- PATRON GİRİŞ ŞİFRESİ ---
PATRON_SIFRESI = "1907"

# --- VERİTABANI ALTYAPISI ---
def veritabanini_hazirla():
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kampanyalar (kampanya_adi TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pr_kayitlar 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tarih TEXT, 
                  kampanya_adi TEXT, 
                  sayfa_adi TEXT, 
                  video_linki TEXT, 
                  ucret REAL)''')
    conn.commit()
    conn.close()

veritabanini_hazirla()

def kampanya_ekle(isim):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO kampanyalar VALUES (?)", (isim.strip(),))
        conn.commit()
    except:
        pass
    conn.close()

def kampanya_sil(isim):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("DELETE FROM kampanyalar WHERE kampanya_adi = ?", (isim,))
    c.execute("DELETE FROM pr_kayitlar WHERE kampanya_adi = ?", (isim,))
    conn.commit()
    conn.close()

def kampanyalari_getir():
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("SELECT kampanya_adi FROM kampanyalar")
    liste = [row[0] for row in c.fetchall()]
    conn.close()
    return liste

def link_kaydet(campaign, sayfa, link, ucret):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO pr_kayitlar (tarih, kampanya_adi, sayfa_adi, video_linki, ucret) VALUES (?, ?, ?, ?, ?)",
              (tarih, campaign, sayfa, link, ucret))
    conn.commit()
    conn.close()

def kayit_guncelle(kayit_id, yeni_kampanya):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("UPDATE pr_kayitlar SET kampanya_adi = ? WHERE id = ?", (yeni_kampanya, kayit_id))
    conn.commit()
    conn.close()

def kayit_sil(kayit_id):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("DELETE FROM pr_kayitlar WHERE id = ?", (kayit_id,))
    conn.commit()
    conn.close()

# --- ARAYÜZ ---
st.title("🎵 PR Kampanya & TikTok Lyrics Takip Merkezi")

st.sidebar.markdown("### 🔒 Yönetim Girişi")
girilen_sifre = st.sidebar.text_input("Patron şifresini girin:", type="password", placeholder="Şifre...")

is_patron = (girilen_sifre == PATRON_SIFRESI)

if is_patron:
    tab_link_ekle, tab_patron_paneli, tab_kampanya_yonetimi = st.tabs([
        "📥 Lyrics Sayfa Girişi", "📊 Patron Rapor Odası (GİZLİ)", "⚙️ Kampanya Yönetimi (GİZLİ)"
    ])
else:
    tab_link_ekle = st.tabs(["📥 Lyrics Sayfa Girişi"])[0]

# --- SEKME 1: SAYFALARIN GÖRECEĞİ ALAN (HERKESE AÇIK) ---
with tab_link_ekle:
    st.error("🚨 DİKKAT: Lütfen formu doldurmadan önce en üstteki kutudan DOĞRU SANATÇI / ŞARKIYI seçtiğinizden emin olun!")
    st.subheader("🔗 Video Linki ve Ücret Bildirim Formu")
    mevcut_kampanyalar = kampanyalari_getir()
    
    if not mevcut_kampanyalar:
        st.warning("Henüz aktif bir PR kampanyası bulunmuyor.")
    else:
        with st.form("sayfa_giriş_formu", clear_on_submit=True):
            secilen_kampanya = st.selectbox("🎯 Reklamını Yaptığınız Şarkıyı Seçin:", mevcut_kampanyalar)
            sayfa_adi = st.text_input("TikTok Sayfa Adınız:", placeholder="@lyrics_sayfam")
            video_linki = st.text_input("Paylaşılan Video Linki:", placeholder="https://vm.tiktok.com/...")
            calisilan_ucret = st.number_input("Anlaşılan Ücret (TL):", min_value=0.0, step=50.0, value=0.0)
            
            submit_butonu = st.form_submit_button("🚀 Bilgileri Gönder ve Kaydet")
            
            if submit_butonu:
                if sayfa_adi and video_linki and calisilan_ucret > 0:
                    link_kaydet(secilen_kampanya, sayfa_adi, video_linki, calisilan_ucret)
                    st.success("✅ Har
