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
        border: 2px solid #dc2626 !important;
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
    /* Seçim Kutuları ve Metin Alanları */
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
        border-bottom-color: #dc2626 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PATRON GİRİŞ ŞİFRESİ ---
PATRON_SIFRESI = "1907"

# --- ASLA SİLİNMEYECEK SUNUCU GÜVENLİ BÖLGE DOSYA YOLU ---
DB_PATH = '/tmp/pr_yonetim_sabit.db'

# --- VERİTABANI ALTYAPISI ---
def veritabanini_hazirla():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kampanyalar (kampanya_adi TEXT PRIMARY KEY, aktiflik INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pr_kayitlar 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tarih TEXT, 
                  kampanya_adi TEXT, 
                  sayfa_adi TEXT, 
                  video_linki TEXT, 
                  ucret REAL,
                  durum TEXT DEFAULT 'Bekliyor')''')
    conn.commit()
    conn.close()

veritabanini_hazirla()

# --- VERİ TABANI FONKSİYONLARI ---
def kampanya_ekle(isim):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO kampanyalar (kampanya_adi, aktiflik) VALUES (?, 1)", (isim.strip(),))
        conn.commit()
    except:
        pass
    conn.close()

def kampanya_aktiflik_set(isim, durum_kodu):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE kampanyalar SET aktiflik = ? WHERE kampanya_adi = ?", (durum_kodu, isim))
    conn.commit()
    conn.close()

def kampanya_sil(isim):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM kampanyalar WHERE kampanya_adi = ?", (isim,))
    c.execute("DELETE FROM pr_kayitlar WHERE kampanya_adi = ?", (isim,))
    conn.commit()
    conn.close()

def kampanyalari_getir(sadece_aktif=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if sadece_aktif:
        c.execute("SELECT kampanya_adi FROM kampanyalar WHERE aktiflik = 1")
    else:
        c.execute("SELECT kampanya_adi FROM kampanyalar")
    liste = [row[0] for row in c.fetchall()]
    conn.close()
    return liste

def kampanya_detayli_getir():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT kampanya_adi, aktiflik FROM kampanyalar")
    liste = c.fetchall()
    conn.close()
    return liste

def sayfaları_getir():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT sayfa_adi FROM pr_kayitlar")
    liste = [row[0] for row in c.fetchall()]
    conn.close()
    return liste

def daha_once_gonderdi_mi(campaign, sayfa):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT video_linki FROM pr_kayitlar WHERE kampanya_adi = ? AND LOWER(TRIM(sayfa_adi)) = LOWER(TRIM(?))", (campaign, sayfa))
    result = c.fetchone()
    conn.close()
    return result

def link_kaydet(campaign, sayfa, link, ucret):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO pr_kayitlar (tarih, kampanya_adi, sayfa_adi, video_linki, ucret, durum) VALUES (?, ?, ?, ?, ?, 'Bekliyor')",
              (tarih, campaign, sayfa.strip(), link.strip(), ucret))
    conn.commit()
    conn.close()

def link_guncelle_sayfa(campaign, sayfa, yeni_link):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE pr_kayitlar SET video_linki = ? WHERE kampanya_adi = ? AND LOWER(TRIM(sayfa_adi)) = LOWER(TRIM(?))", 
              (yeni_link.strip(), campaign, sayfa.strip()))
    conn.commit()
    conn.close()

def odeme_durumu_degistir(kayit_id, yeni_durum):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE pr_kayitlar SET durum = ? WHERE id = ?", (yeni_durum, kayit_id))
    conn.commit()
    conn.close()

def sayfa_tum_borclari_kapat(sayfa_ismi):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE pr_kayitlar SET durum = 'Ödendi' WHERE sayfa_adi = ? AND durum = 'Bekliyor'", (sayfa_ismi,))
    conn.commit()
    conn.close()

def kayit_guncelle(kayit_id, yeni_kampanya):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE pr_kayitlar SET kampanya_adi = ? WHERE id = ?", (yeni_kampanya, kayit_id))
    conn.commit()
    conn.close()

def kayit_sil(kayit_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM pr_kayitlar WHERE id = ?", (kayit_id,))
    conn.commit()
    conn.close()

# --- ARAYÜZ BAŞLIĞI ---
st.title("🚨 PR KAMPANYA & TİKTOK LYRICS TAKİP SİSTEMİ 🔴")

st.sidebar.markdown("### 🔒 Yönetim Girişi")
girilen_sifre = st.sidebar.text_input("Şifre girin:", type="password", placeholder="••••")

is_patron = (girilen_sifre == PATRON_SIFRESI)

if is_patron:
    tab_link_ekle, tab_patron_paneli, tab_kampanya_yonetimi = st.tabs([
        "📥 Lyrics İşlemleri", "📊 Patron Rapor Odası (GİZLİ)", "⚙️ Kampanya Yönetimi"
    ])
else:
    tab_link_ekle = st.tabs(["📥 Lyrics İşlemleri"])[0]

# --- SEKME 1: LYRICS SAYFALARI ALANI ---
with tab_link_ekle:
    st.error("🚨 DİKKAT: Lütfen formu doldurmadan önce en üstteki kutudan DOĞRU SANATÇI / ŞARKIYI seçtiğinizden emin olun!")
    mevcut_kampanyalar_aktif = kampanyalari_getir(sadece_aktif=True)
    mevcut_kampanyalar_hepsi = kampanyalari_getir(sadece_aktif=False)
    
    if not mevcut_kampanyalar_aktif:
        st.warning("Henüz aktif ve girişlere açık bir PR kampanyası bulunmuyor.")
    else:
        col_form, col_guncelle = st.columns(2)
        
        with col_form:
            st.subheader("📥 Yeni Video Bildirim Formu")
            with st.form("sayfa_giriş_formu", clear_on_submit=False):
                secilen_kampanya = st.selectbox("🎯 Reklamını Yaptığınız Şarkıyı Seçin:", mevcut_kampanyalar_aktif, key="yeni_kamp_sec")
                sayfa_adi = st.text_input("TikTok Sayfa Adınız:", placeholder="@lyrics_sayfam", key="yeni_sayfa_ad")
                video_linki = st.text_input("Paylaşılan Video Linki:", placeholder="https://vm.tiktok.com/...", key="yeni_link_ad")
                calisilan_ucret = st.number_input("Anlaşılan Ücret (TL):", min_value=0.0, step=50.0, value=0.0)
                
                submit_butonu = st.form_submit_button("🚀 Bilgileri Gönder ve Kaydet")
                
                if submit_butonu:
                    if sayfa_adi and video_linki and calisilan_ucret > 0:
                        eski_kayit = daha_once_gonderdi_mi(secilen_kampanya, sayfa_adi)
                        if eski_kayit:
                            st.error(f"❌ UYARI: {sayfa_adi} sayfası bu şarkı için zaten link gönderdi! Hata varsa sağ taraftaki 'Düzenle' alanını kullanın.")
                        else:
                            link_kaydet(secilen_kampanya, sayfa_adi, video_linki, calisilan_ucret)
                            st.success("🎉 BAŞARILI! Bilgileriniz sisteme kaydedildi. Emeğinize sağlık!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("⚠️ Lütfen tüm alanları eksiksiz doldurun!")
                        
        with col_guncelle:
            st.subheader("✏️ Yanlış Girilen Linki Düzenle")
            st.info("Daha önce gönderdiğiniz hatalı bir linki buradan anında güncelleyebilirsiniz.")
            
            g_kampanya = st.selectbox("Hangi Şarkının Linkini Düzelteceksiniz?", mevcut_kampanyalar_hepsi, key="g_kamp_sec")
            g_sayfa = st.text_input("Sisteme Girdiğiniz Sayfa Adınız:", placeholder="@lyrics_sayfam", key="g_sayfa_ad")
            
            if g_sayfa:
                mevcut_link_verisi = daha_once_gonderdi_mi(g_kampanya, g_sayfa)
                if mevcut_link_verisi:
                    st.warning(f"📋 Şu anki kayıtlı linkiniz:\n{mevcut_link_verisi[0]}")
                    yeni_link_girdisi = st.text_input("👉 Yeni (Doğru) TikTok Linkinizi Yapıştırın:", placeholder="https://vm.tiktok.com/...", key="g_yeni_link")
                    
                    if st.button("💾 Linki Güncelle ve Kaydet"):
                        if yeni_link_girdisi:
                            link_guncelle_sayfa(g_kampanya, g_sayfa, yeni_link_girdisi)
                            st.success("✅ Linkiniz başarıyla güncellendi!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Lütfen yeni linki boş bırakmayın!")
                else:
                    st.error("🔍 Geçmiş bir kayıt bulunamadı. Sayfa adınızı kontrol edin.")

# --- GIZLI ALANLAR (PATRON) ---
if is_patron:
    with tab_patron_paneli:
        st.subheader("👑 Şirket Genel PR Bilançosu (Tüm İşlerin Toplamı)")
        
        conn = sqlite3.connect(DB_PATH)
        df_genel = pd.read_sql_query("SELECT kampanya_adi, sayfa_adi, ucret, durum, tarih, video_linki FROM pr_kayitlar", conn)
        conn.close()
        
        if not df_genel.empty:
            genel_paylasim = len(df_genel)
            genel_borc = df_genel[df_genel['durum'] == 'Bekliyor']['ucret'].sum()
            genel_odenen = df_genel[df_genel['durum'] == 'Ödendi']['ucret'].sum()
            
            g1, g2, g3 = st.columns(3)
            with g1: st.metric(label="🎥 SİSTEMDEKİ TOPLAM PAYLAŞIM", value=f"{genel_paylasim} Video")
            with g2: st.metric(label="🚨 PATRONA ATILACAK TOPLAM BORÇ", value=f"{genel_borc:,.2f} TL")
            with g3: st.metric(label="✅ KAPATILAN TOPLAM ÖDEME", value=f"{genel_odenen:,.2f} TL")
            
            st.markdown("📊 **Kampanya Bazlı Borç Dağılım Raporu:**")
            
            ozet_liste = []
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT kampanya_adi FROM kampanyalar")
            tum_kamplar = [r[0] for r in c.fetchall()]
            conn.close()
            
            for k in tum_kamplar:
                k_df = df_genel[df_genel['kampanya_adi'] == k]
                k_borc = k_df[k_df['durum'] == 'Bekliyor']['ucret'].sum()
                k_odenen = k_df[k_df['durum'] == 'Ödendi']['ucret'].sum()
                ozet_liste.append({"Kampanya / Sanatçı Adı": k, "Toplam Video": len(k_df), "Kalan Borç (TL)": k_borc, "Ödenen Miktar (TL)": k_odenen})
            
            st.dataframe(pd.DataFrame(ozet_liste), use_container_width=True)
        else:
            st.info("Sistemde henüz hiçbir finansal kayıt yok.")
            
        st.markdown("---")
        st.subheader("👤 Sayfa Bazlı Toplu Hesap ve Borç Kapatma")
        mevcut_sayfalar = sayfaları_getir()
        
        if mevcut_sayfalar:
            secilen_toplu_sayfa = st.selectbox("Hesabını kapatmak istediğiniz LYRICS SAYFASINI seçin:", mevcut_sayfalar, key="toplu_sayfa_sec")
            if secilen_toplu_sayfa and not df_genel.empty:
                sayfa_df = df_genel[df_genel['sayfa_adi'] == secilen_toplu_sayfa]
                s1, s2, s3 = st.columns(3)
                with s1: st.metric(label=f"🎥 Toplam Video", value=f"{len(sayfa_df)} Adet")
                with s2: st.metric(label="🔴 BU SAYFAYA TOPLAM BORÇ", value=f"{sayfa_df[sayfa_df['durum'] == 'Bekliyor']['ucret'].sum():,.2f} TL")
                with s3: st.metric(label="🟢 SAYFAYA ÖDENEN TOPLAM", value=f"{sayfa_df[sayfa_df['durum'] == 'Ödendi']['ucret'].sum():,.2f} TL")
                
                bekleyen_sayfa_df = sayfa_df[sayfa_df['durum'] == 'Bekliyor'][['tarih', 'kampanya_adi', 'video_linki', 'ucret']]
                if not bekleyen_sayfa_df.empty:
                    st.dataframe(bekleyen_sayfa_df, use_container_width=True)
                    if st.button(f"🚀 Tüm Borçları Kapat"):
                        sayfa_tum_borclari_kapat(secilen_toplu_sayfa)
                        st.success("Tüm borçlar sıfırlandı!")
                        time.sleep(1)
                        st.rerun()
                    
        st.markdown("---")
        st.subheader("🔍 Şarkı Bazlı Detaylı Rapor ve İşlemler")
        if mevcut_kampanyalar_hepsi:
            izlenecek_campaign = st.selectbox("Raporunu görmek istediğiniz kampanyayı seçin:", mevcut_kampanyalar_hepsi, key="rapor_sec")
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT id, tarih as 'Tarih', sayfa_adi as 'Sayfa', video_linki as 'Video Linki', ucret as 'Ücret (TL)', durum as 'Durum' FROM pr_kayitlar WHERE kampanya_adi = ?", conn, params=(izlenecek_campaign,))
            conn.close()
            
            if not df.empty:
                st.dataframe(df.drop(columns=['id']), use_container_width=True)
                st.text_area("Sanatçı Link Listesi:", value="\n".join(df['Video Linki'].tolist()), height=150)
                
                df['secim_metni_odeme'] = df['Sayfa'] + " | " + df['Ücret (TL)'].astype(str) + " TL [" + df['Durum'] + "]"
                secili_odeme_row = st.selectbox("Ödemesini değiştirmek istediğiniz sayfayı seçin:", df['secim_metni_odeme'].tolist(), key="odeme_satir_sec")
                
                if secili_odeme_row:
                    secili_odeme_id = int(df[df['secim_metni_odeme'] == secili_odeme_row]['id'].values[0])
                    current_status = df[df['id'] == secili_odeme_id]['Durum'].values[0]
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("Durumu Değiştir (Ödendi/Bekliyor)", key="dur_btn"):
                            odeme_durumu_degistir(secili_odeme_id, 'Ödendi' if current_status == 'Bekliyor' else 'Bekliyor')
                            st.success("Güncellendi!")
                            time.sleep(1)
                            st.rerun()
                    with col_b2:
                        if st.button("🗑️ Bu Kaydı Tamamen Sil", key="sil_btn"):
                            kayit_sil(secili_odeme_id)
                            st.success("Silindi!")
                            time.sleep(1)
                            st.rerun()

    with tab_kampanya_yonetimi:
        col_ekle, col_durum_degis = st.columns(2)
        with col_ekle:
            st.subheader("➕ Yeni Kampanya Başlat")
            yeni_sarki = st.text_input("Şarkıcı ve Kampanya Adı:")
            if st.button("🚀 Kampanyayı Aç"):
                if yeni_sarki:
                    kampanya_ekle(yeni_sarki)
                    st.success("Kampanya açıldı!")
                    time.sleep(1)
                    st.rerun()
                    
        with col_durum_degis:
            st.subheader("🔒 Girişleri Kapat / Dondur")
            detayli_liste = kampanya_detayli_getir()
            if detayli_liste:
                formatli_liste = [f"{r[0]} - [{'GİRİŞE AÇIK' if r[1]==1 else 'DONDURULDU'}]" for r in detayli_liste]
                secilen_islem_kampanyasi = st.selectbox("Kampanya Seçin:", formatli_liste, key="durum_islem_sec")
                
                if secilen_islem_kampanyasi:
                    gercek_kamp_ismi = secilen_islem_kampanyasi.split(" - [")[0]
                    mevcut_aktiflik = [r[1] for r in detayli_liste if r[0] == gercek_kamp_ismi][0]
                    
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        if st.button("🔄 Durumu Değiştir (Aç/Dondur)", key="fl_btn"):
                            kampanya_aktiflik_set(gercek_kamp_ismi, 0 if mevcut_aktiflik == 1 else 1)
                            st.success("Durum güncellendi!")
                            time.sleep(1)
                            st.rerun()
                    with c_b2:
                        if st.button("❌ Kampanyayı Tamamen Sil", key="kp_sil_btn"):
                            kampanya_sil(gercek_kamp_ismi)
                            st.success("Silindi!")
                            time.sleep(1)
                            st.rerun()
