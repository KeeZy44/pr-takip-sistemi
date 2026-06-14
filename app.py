import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Sayfa Ayarları (Mobilde jilet gibi görünmesi için geniş ekran)
st.set_page_config(page_title="PR Kampanya & Borç Otomasyonu", layout="wide")

# --- VERİTABANI ALTYAPISI ---
def veritabanini_hazirla():
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    # Kampanyalar tablosu (Şarkıcılar için)
    c.execute('''CREATE TABLE IF NOT EXISTS kampanyalar (kampanya_adi TEXT PRIMARY KEY)''')
    # Gelen video linkleri ve borç tablosu
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

# --- VERİTABANI YARDIMCI FONKSİYONLARI ---
def kampanya_ekle(isim):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO kampanyalar VALUES (?)", (isim.strip(),))
        conn.commit()
    except:
        pass
    conn.close()

def kampanyalari_getir():
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("SELECT kampanya_adi FROM kampanyalar")
    liste = [row[0] for row in c.fetchall()]
    conn.close()
    return liste

def link_kaydet(kampanya, sayfa, link, ucret):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO pr_kayitlar (tarih, kampanya_adi, sayfa_adi, video_linki, ucret) VALUES (?, ?, ?, ?, ?)",
              (tarih, kampanya, sayfa, link, ucret))
    conn.commit()
    conn.close()

# --- ARAYÜZ BAŞLANGICI ---
st.title("🎵 PR Kampanya & TikTok Lyrics Takip Merkezi")
st.markdown("WhatsApp Karmaşasına Son! Linkleri Topla, Kampanya Bazlı Toplam Borcunu Anlık Gör.")

# Sekmeler: Birisi Sayfaların Link Atacağı Yer, Diğeri Senin Rapor Ekranın
tab_link_ekle, tab_patron_paneli, tab_kampanya_yonetimi = st.tabs([
    "📥 Lyrics Sayfa Girişi", "📊 Patron Rapor Odası", "⚙️ Kampanya Oluştur"
])

# --- SEKME 1: LYRICS SAYFALARININ KULLANACAĞI ALAN ---
with tab_link_ekle:
    st.subheader("🔗 Video Linki ve Ücret Bildirim Formu")
    st.write("Anlaştığımız şarkıyı seçip, paylaştığınız video linkini ve ücreti girerek kaydedin.")
    
    mevcut_kampanyalar = kampanyalari_getir()
    
    if not mevcut_kampanyalar:
        st.warning("Henüz aktif bir PR kampanyası bulunmuyor. Önce 'Kampanya Oluştur' sekmesinden şarkıcı ekleyin.")
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

# --- SEKME 2: SENİN ÖZEL RAPOR VE BORÇ EKRANIN ---
with tab_patron_paneli:
    st.subheader("📊 Canlı PR Raporları ve Toplam Borç Durumu")
    
    mevcut_kampanyalar_rapor = kampanyalari_getir()
    
    if not mevcut_kampanyalar_rapor:
        st.info("Gösterilecek veri yok.")
    else:
        izlenecek_kampanya = st.selectbox("Raporunu görmek istediğiniz kampanyayı seçin:", mevcut_kampanyalar_rapor, key="rapor_sec")
        
        # Verileri Çek
        conn = sqlite3.connect('pr_yonetim.db')
        query = "SELECT tarih as 'Tarih', sayfa_adi as 'Sayfa', video_linki as 'Video Linki', ucret as 'Ücret (TL)' FROM pr_kayitlar WHERE kampanya_adi = ?"
        df = pd.read_sql_query(query, conn, params=(izlenecek_kampanya,))
        conn.close()
        
        if not df.empty:
            # Hesaplamalar
            toplam_borc = df['Ücret (TL)'].sum()
            toplam_paylasim = len(df)
            
            # Üst tarafta büyük metrikler (Telefon ekranında harika durur)
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="🎥 Toplam Paylaşım Sayısı", value=f"{toplam_paylasim} Video")
            with col2:
                st.metric(label="💰 Bu Kampanya İçin Toplam Borç", value=f"{toplam_borc:,.2f} TL")
            
            st.markdown("---")
            st.write("📋 **Paylaşılan Linklerin Detaylı Listesi:**")
            # Linkleri tıklanabilir tablo yapmak için veri çerçevesini gösteriyoruz
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Bu kampanya için henüz hiçbir sayfa link yüklemedi.")

# --- SEKME 3: YENİ ŞARKICI / KAMPANYA EKLEME ---
with tab_kampanya_yonetimi:
    st.subheader("⚙️ Yeni PR Kampanyası Başlat")
    yeni_sarki = st.text_input("Şarkıcı ve Kampanya Adı (Örn: RECO - Hatıran Var):")
    
    if st.button("➕ Kampanyayı Sisteme Tanımla"):
        if yeni_sarki:
            kampanya_ekle(yeni_sarki)
            st.success(f"🔥 '{yeni_sarki}' kampanyası başarıyla başlatıldı! Artık sayfalar bu ismi seçebilir.")
            st.rerun()
        else:
            st.error("Lütfen boş bırakmayın!")
