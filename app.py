import streamlit as st
import sqlite3
import pandas as pd
import datetime
import time

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

def daha_once_gonderdi_mi(campaign, sayfa):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("SELECT video_linki FROM pr_kayitlar WHERE kampanya_adi = ? AND LOWER(TRIM(sayfa_adi)) = LOWER(TRIM(?))", (campaign, sayfa))
    result = c.fetchone()
    conn.close()
    return result

def link_kaydet(campaign, sayfa, link, ucret):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO pr_kayitlar (tarih, kampanya_adi, sayfa_adi, video_linki, ucret) VALUES (?, ?, ?, ?, ?)",
              (tarih, campaign, sayfa.strip(), link.strip(), ucret))
    conn.commit()
    conn.close()

def link_guncelle_sayfa(campaign, sayfa, yeni_link):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("UPDATE pr_kayitlar SET video_linki = ? WHERE kampanya_adi = ? AND LOWER(TRIM(sayfa_adi)) = LOWER(TRIM(?))", 
              (yeni_link.strip(), campaign, sayfa.strip()))
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
        "📥 Lyrics İşlemleri", "📊 Patron Rapor Odası (GİZLİ)", "⚙️ Kampanya Yönetimi (GİZLİ)"
    ])
else:
    tab_link_ekle = st.tabs(["📥 Lyrics İşlemleri"])[0]

# --- SEKME 1: SAYFALARIN GÖRECEĞİ ALAN (HERKESE AÇIK) ---
with tab_link_ekle:
    st.error("🚨 DİKKAT: Lütfen formu doldurmadan önce doğru sanatçı/şarkıyı seçtiğinizden emin olun!")
    mevcut_kampanyalar = kampanyalari_getir()
    
    if not mevcut_kampanyalar:
        st.warning("Henüz aktif bir PR kampanyası bulunmuyor.")
    else:
        col_form, col_guncelle = st.columns(2)
        
        with col_form:
            st.subheader("🔗 Yeni Video Bildirim Formu")
            with st.form("sayfa_giriş_formu", clear_on_submit=False):
                secilen_kampanya = st.selectbox("🎯 Reklamını Yaptığınız Şarkıyı Seçin:", mevcut_kampanyalar, key="yeni_kamp_sec")
                sayfa_adi = st.text_input("TikTok Sayfa Adınız:", placeholder="@lyrics_sayfam", key="yeni_sayfa_ad")
                video_linki = st.text_input("Paylaşılan Video Linki:", placeholder="https://vm.tiktok.com/...", key="yeni_link_ad")
                calisilan_ucret = st.number_input("Anlaşılan Ücret (TL):", min_value=0.0, step=50.0, value=0.0)
                
                submit_butonu = st.form_submit_button("🚀 Bilgileri Gönder ve Kaydet")
                
                if submit_butonu:
                    if sayfa_adi and video_linki and calisilan_ucret > 0:
                        eski_kayit = daha_once_gonderdi_mi(secilen_kampanya, sayfa_adi)
                        if eski_kayit:
                            st.error(f"❌ UYARI: {sayfa_adi} sayfası bu şarkı için zaten link gönderdi! Yanlış link attıysanız sağ taraftaki 'Link Değiştirme' alanını kullanın.")
                        else:
                            link_kaydet(secilen_kampanya, sayfa_adi, video_linki, calisilan_ucret)
                            st.success("🎉 BAŞARILI! Bilgileriniz sisteme kaydedildi. Emeğinize sağlık!")
                            st.balloons()
                            time.sleep(3)
                            st.rerun()
                    else:
                        st.error("⚠️ Lütfen tüm alanları eksiksiz doldurun!")
                        
        with col_guncelle:
            st.subheader("✏️ Yanlış Girilen Linki Düzenle")
            st.info("Daha önce gönderdiğiniz hatalı bir linki buradan güncelleyebilirsiniz.")
            
            g_kampanya = st.selectbox("Hangi Şarkının Linkini Düzelteceksiniz?", mevcut_kampanyalar, key="g_kamp_sec")
            g_sayfa = st.text_input("Sisteme Girdiğiniz Sayfa Adınız:", placeholder="@lyrics_sayfam", key="g_sayfa_ad")
            
            if g_sayfa:
                mevcut_link_verisi = daha_once_gonderdi_mi(g_kampanya, g_sayfa)
                if mevcut_link_verisi:
                    st.warning(f"📋 Şu anki kayıtlı linkiniz:\n{mevcut_link_verisi[0]}")
                    yeni_link_girdisi = st.text_input("👉 Yeni (Doğru) TikTok Linkinizi Yapıştırın:", placeholder="https://vm.tiktok.com/...", key="g_yeni_link")
                    
                    if st.button("💾 Linki Güncelle ve Kaydet"):
                        if yeni_link_girdisi:
                            link_guncelle_sayfa(g_kampanya, g_sayfa, yeni_link_girdisi)
                            st.success("✅ Linkiniz başarıyla güncellendi! Mehmet Ali'nin paneline doğru link iletildi.")
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error("Lütfen yeni linki boş bırakmayın!")
                else:
                    st.error("🔍 Bu sayfa adına ve şarkıya ait geçmiş bir kayıt bulunamadı. Lütfen bilgileri kontrol edin.")

# --- GIZLI ALANLAR ---
if is_patron:
    # --- SEKME 2: PATRON RAPOR ODASI ---
    with tab_patron_paneli:
        st.subheader("📊 Canlı PR Raporları ve Toplam Borç Durumu")
        mevcut_kampanyalar_rapor = kampanyalari_getir()
        
        if not mevcut_kampanyalar_rapor:
            st.info("Gösterilecek aktif bir kampanya yok.")
        else:
            izlenecek_campaign = st.selectbox("Raporunu görmek istediğiniz kampanyayı seçin:", mevcut_kampanyalar_rapor, key="rapor_sec")
            
            conn = sqlite3.connect('pr_yonetim.db')
            query = "SELECT id, tarih as 'Tarih', sayfa_adi as 'Sayfa', video_linki as 'Video Linki', ucret as 'Ücret (TL)' FROM pr_kayitlar WHERE kampanya_adi = ?"
            df = pd.read_sql_query(query, conn, params=(izlenecek_campaign,))
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
                st.dataframe(df.drop(columns=['id']), use_container_width=True)
                
                # --- MEKATRONIK DÜZENLEME PANELİ ---
                st.markdown("---")
                st.subheader("🛠️ Yanlış Atılan Linki Düzeltme Paneli (Patron)")
                
                df['secim_metni'] = df['Sayfa'] + " | " + df['Ücret (TL)'].astype(str) + " TL (" + df['Tarih'] + ")"
                duzenlenecek_row = st.selectbox("Yanlış girilen kaydı listeden seçin:", df['secim_metni'].tolist())
                
                if duzenlenecek_row:
                    secili_id = int(df[df['secim_metni'] == duzenlenecek_row]['id'].values[0])
                    
                    col_tasit, col_silme = st.columns(2)
                    with col_tasit:
                        hedef_kampanya = st.selectbox("Bu kaydı hangi DOĞRU kampanyaya taşımak istiyorsunuz?", mevcut_kampanyalar_rapor, key="hedef_kamp")
                        if st.button("🔄 Seçilen Kaydı Bu Kampanyaya Taşı"):
                            kayit_guncelle(secili_id, hedef_kampanya)
                            st.success("✅ Kayıt başarıyla doğru kampanyaya taşındı!")
                            st.rerun()
                    with col_silme:
                        st.write(" ")
                        st.write(" ")
                        if st.button("🗑️ Seçilen Kaydı Tamamen Sil"):
                            kayit_sil(secili_id)
                            st.success("🗑️ Kayıt sistemden tamamen silindi!")
                            st.rerun()
            else:
                st.info("Bu kampanya için henüz hiçbir sayfa link yüklemedi.")

    # --- SEKME 3: KAMPANYA YÖNETİMİ ---
    with tab_kampanya_yonetimi:
        col_ekle, col_sil = st.columns(2)
        
        with col_ekle:
            st.subheader("➕ Yeni Kampanya Başlat")
            yeni_sarki = st.text_input("Şarkıcı ve Kampanya Adı:")
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
                st.warning("⚠️ DİKKAT: Kampanyayı sildiğinizde her şey kalıcı olarak yok edilir!")
                
                if st.button("❌ Kampanyayı ve Tüm Kayıtları Sil"):
                    kampanya_sil(silinecek_secim)
                    st.success(f"🗑️ '{silinecek_secim}' başarıyla silindi!")
                    st.rerun()
