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
    # Hem kampanya adını hem de o kampanyaya ait tüm kayıtları siler
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
    st.subheader("🔗 Video Linki ve Ücret Bildirim Formu")
    mevcut_kampanyalar = kampanyalari_getir()
    
    if not mevcut_kampanyalar:
        st.warning("Henüz aktif bir PR kampanyası bulunmuyor. Sistem hazır olduğunda form burada açılacaktır.")
    else:
        with st.form("sayfa_giriş_formu", clear_on_submit=True):
            secilen_kampanya = st.selectbox("Hangi Şarkı / Kampanya için paylaştınız?", mevcut_kampanyalar)
            sayfa_adi = st.text_input("TikTok Sayfa Adınız:", placeholder="@lyrics_sayfam")
            video_linki = st.text_input("Paylaşılan Video Linki:", placeholder="https://vm.tiktok.com/...")
            calisilan_ucret = st.number_input("Anlaşılan Ücret (TL):", min_value=0.0, step=50.0, value=0.0)
            
            submit_butonu = st.form_submit_button("🚀 Bilgileri Gönder ve Kaydet")
            
            if submit_butonu:
                if sayfa_adi and video_linki and calisilan_ucret > 0:
                    link_kaydet(secilen_kampanya, sayfa_adi, video_linki, calisilan_ucret)
                    st.success("✅ Harika! Veriler başarıyla Mehmet Ali'ye iletildi. Emeğine sağlık!")
                else:
                    st.error("⚠️ Lütfen tüm alanları eksiksiz doldurun ve ücreti girin!")

# --- GİZLİ ALANLAR ---
if is_patron:
    # --- SEKME 2: PATRON RAPOR ODASI ---
    with tab_patron_paneli:
        st.subheader("📊 Canlı PR Raporları ve Toplam Borç Durumu")
        mevcut_kampanyalar_rapor = kampanyalari_getir()
        
        if not mevcut_kampanyalar_rapor:
            st.info("Gösterilecek aktif bir kampanya yok.")
        else:
            izlenecek_kampanya = st.selectbox("Raporunu görmek istediğiniz kampanyayı seçin:", mevcut_kampanyalar_rapor, key="rapor_sec")
            
            conn = sqlite3.connect('pr_yonetim.db')
            query = "SELECT tarih as 'Tarih', sayfa_adi as 'Sayfa', video_linki as 'Video Linki', ucret as 'Ücret (TL)' FROM pr_kayitlar WHERE kampanya_adi = ?"
            df = pd.read_sql_query(query, conn, params=(izlenecek_kampanya,))
            conn.close()
            
            if not df.empty:
                toplam_borc = df['Ücret (TL)'].sum()
                toplam_paylasim = len(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="🎥 Toplam Paylaşım Sayısı", value=f"{toplam_paylasim} Video")
                with col2:
                    st.metric(label="💰 Bu Kampanya İçin Toplam Borç", value=f"{toplam_borc:,.2f} TL")
                
                st.markdown("---")
                st.write("📋 **Paylaşılan Linklerin Detaylı Listesi:**")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Bu kampanya için henüz hiçbir sayfa link yüklemedi.")

    # --- SEKME 3: KAMPANYA YÖNETİMİ (EKLEME & SİLME) ---
    with tab_campaign_yonetimi:
        col_ekle, col_sil = st.columns(2)
        
        with col_ekle:
            st.subheader("➕ Yeni Kampanya Başlat")
            yeni_sarki = st.text_input("Şarkıcı ve Kampanya Adı (Örn: RECO - Hatıran Var):")
            if st.button("🚀 Kampanyayı Aç"):
                if yeni_sarki:
                    kampanya_ekle(yeni_sarki)
                    st.success(f"🔥 '{yeni_sarki}' başarıyla açıldı!")
                    st.rerun()
                else:
                    st.error("Boş bırakılamaz!")
                    
        with col_sil:
            st.subheader("🗑️ Biten Kampanyayı Sil")
            silinecek_kampanyalar = kampanyalari_getir()
            
            if not silinecek_kampanyalar:
                st.info("Silinecek kampanya yok.")
            else:
                silinecek_secim = st.selectbox("Silmek istediğiniz kampanyayı seçin:", silinecek_kampanyalar, key="sil_sec")
                st.warning("⚠️ DİKKAT: Kampanyayı sildiğinizde bu şarkıya ait gelen tüm linkler ve borç kayıtları kalıcı olarak yok edilir!")
                
                if st.button("❌ Kampanyayı ve Tüm Kayıtları Sil"):
                    kampanya_sil(silinecek_secim)
                    st.success(f"🗑️ '{silinecek_secim}' ve tüm verileri başarıyla silindi!")
                    st.rerun()
