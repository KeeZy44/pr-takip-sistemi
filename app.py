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
    
    c.execute("PRAGMA table_info(pr_kayitlar)")
    sutunlar = [row[1] for row in c.fetchall()]
    if 'durum' not in sutunlar:
        c.execute("ALTER TABLE pr_kayitlar ADD COLUMN durum TEXT DEFAULT 'Bekliyor'")
        
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
    c.execute("INSERT INTO pr_kayitlar (tarih, kampanya_adi, sayfa_adi, video_linki, ucret, durum) VALUES (?, ?, ?, ?, ?, 'Bekliyor')",
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

def odeme_durumu_degistir(kayit_id, yeni_durum):
    conn = sqlite3.connect('pr_yonetim.db')
    c = conn.cursor()
    c.execute("UPDATE pr_kayitlar SET durum = ? WHERE id = ?", (yeni_durum, kayit_id))
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
    mevcut_kampanyalar = kampanyalari_getir()
    
    if not mevcut_kampanyalar:
        st.warning("Henüz aktif bir PR kampanyası bulunmuyor.")
    else:
        col_form, col_guncelle = st.columns(2)
        
        with col_form:
            st.subheader("📥 Yeni Video Bildirim Formu")
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
                            st.error(f"❌ UYARI: {sayfa_adi} sayfası bu şarkı için zaten link gönderdi! Hata varsa sağ taraftaki 'Düzenle' alanını kullanın.")
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
            st.info("Daha önce gönderdiğiniz hatalı bir linki buradan anında güncelleyebilirsiniz.")
            
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
                            st.success("✅ Linkiniz başarıyla güncellendi!")
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error("Lütfen yeni linki boş bırakmayın!")
                else:
                    st.error("🔍 Geçmiş bir kayıt bulunamadı. Sayfa adınızı kontrol edin.")

# --- GIZLI ALANLAR (PATRON) ---
if is_patron:
    # --- SEKME 2: PATRON RAPOR ODASI ---
    with tab_patron_paneli:
        
        # ==========================================
        # 🔥 YENİ MEKATRONİK GENEL BİLANÇO MOTORU 🔥
        # ==========================================
        st.subheader("👑 Şirket Genel PR Bilançosu (Tüm İşlerin Toplamı)")
        
        conn = sqlite3.connect('pr_yonetim.db')
        df_genel = pd.read_sql_query("SELECT kampanya_adi, ucret, durum FROM pr_kayitlar", conn)
        conn.close()
        
        if not df_genel.empty:
            genel_paylasim = len(df_genel)
            genel_borc = df_genel[df_genel['durum'] == 'Bekliyor']['ucret'].sum()
            genel_odenen = df_genel[df_genel['durum'] == 'Ödendi']['ucret'].sum()
            
            # Üst Metrik Kutuları
            g1, g2, g3 = st.columns(3)
            with g1:
                st.metric(label="🎥 SİSTEMDEKİ TOPLAM PAYLAŞIM", value=f"{genel_paylasim} Video")
            with g2:
                st.metric(label="🚨 PATRONA ATILACAK TOPLAM BORÇ", value=f"{genel_borc:,.2f} TL")
            with g3:
                st.metric(label="✅ KAPATILAN TOPLAM ÖDEME", value=f"{genel_odenen:,.2f} TL")
            
            # Kampanya bazlı hızlı özet tablosu (Patrona atmak için)
            st.markdown("📊 **Kampanya Bazlı Borç Dağılım Raporu:**")
            
            ozet_liste = []
            conn = sqlite3.connect('pr_yonetim.db')
            c = conn.cursor()
            c.execute("SELECT kampanya_adi FROM kampanyalar")
            tum_kamplar = [r[0] for r in c.fetchall()]
            conn.close()
            
            for k in tum_kamplar:
                k_df = df_genel[df_genel['kampanya_adi'] == k]
                k_borc = k_df[k_df['durum'] == 'Bekliyor']['ucret'].sum()
                k_odenen = k_df[k_df['durum'] == 'Ödendi']['ucret'].sum()
                k_video = len(k_df)
                ozet_liste.append({
                    "Kampanya / Sanatçı Adı": k,
                    "Toplam Video": k_video,
                    "Kalan Borç (TL)": k_borc,
                    "Ödenen Miktar (TL)": k_odenen
                })
            
            ozet_df = pd.DataFrame(ozet_liste)
            st.dataframe(ozet_df, use_container_width=True)
        else:
            st.info("Sistemde henüz hiçbir finansal kayıt yok.")
            
        st.markdown("---")
        
        # ==========================================
        # 🎯 TEKİL KAMPANYA DETAY DETAY RAPOR ALANI 🎯
        # ==========================================
        st.subheader("🔍 Şarkı Bazlı Detaylı Rapor ve İşlemler")
        mevcut_kampanyalar_rapor = kampanyalari_getir()
        
        if not mevcut_kampanyalar_rapor:
            st.info("Gösterilecek aktif bir kampanya yok.")
        else:
            izlenecek_campaign = st.selectbox("Raporunu görmek istediğiniz kampanyayı seçin:", mevcut_kampanyalar_rapor, key="rapor_sec")
            
            conn = sqlite3.connect('pr_yonetim.db')
            query = "SELECT id, tarih as 'Tarih', sayfa_adi as 'Sayfa', video_linki as 'Video Linki', ucret as 'Ücret (TL)', durum as 'Durum' FROM pr_kayitlar WHERE kampanya_adi = ?"
            df = pd.read_sql_query(query, conn, params=(izlenecek_campaign,))
            conn.close()
            
            if not df.empty:
                toplam_paylasim = len(df)
                toplam_borc = df[df['Durum'] == 'Bekliyor']['Ücret (TL)'].sum()
                toplam_odenen = df[df['Durum'] == 'Ödendi']['Ücret (TL)'].sum()
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="🎥 Bu Şarkı Toplam Paylaşım", value=f"{toplam_paylasim} Video")
                with c2:
                    st.metric(label="🔴 Bu Şarkı Kalan Borç", value=f"{toplam_borc:,.2f} TL")
                with c3:
                    st.metric(label="🟢 Bu Şarkı Ödenen Miktar", value=f"{toplam_odenen:,.2f} TL")
                
                st.markdown("---")
                st.write("📋 **Mevcut Kampanya Dağılım Tablosu:**")
                st.dataframe(df.drop(columns=['id']), use_container_width=True)
                
                # --- LİNK KOPYALAMA ALANI ---
                st.markdown(" ")
                linkler_listesi = df['Video Linki'].tolist()
                temiz_link_metni = "\n".join(linkler_listesi)
                
                st.subheader("📋 Sanatçıya Atılacak Toplu Link Listesi")
                st.text_area("Aşağıdaki kutudan tüm linkleri tek tıkla kopyalayabilirsin kral:", value=temiz_link_metni, height=150)
                
                if st.button("📋 TÜM LİNKLERİ KOPYALAMAK İÇİN HAZIRLA"):
                    st.success("✅ Tüm linkler alt alta başarıyla listelendi! Yukarıdaki kutudan kolayca kopyalayabilirsin.")
                
                # --- ÖDEME KAPATMA PANELİ ---
                st.markdown("---")
                st.subheader("💰 Hızlı Ödeme ve Durum Kapatma Sistemi")
                df['secim_metni_odeme'] = df['Sayfa'] + " | " + df['Ücret (TL)'].astype(str) + " TL [" + df['Durum'] + "]"
                secili_odeme_row = st.selectbox("Ödemesini değiştirmek istediğiniz sayfayı seçin:", df['secim_metni_odeme'].tolist(), key="odeme_satir_sec")
                
                if secili_odeme_row:
                    secili_odeme_id = int(df[df['secim_metni_odeme'] == secili_odeme_row]['id'].values[0])
                    current_status = df[df['id'] == secili_odeme_id]['Durum'].values[0]
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if current_status == 'Bekliyor':
                            if st.button("🟢 Ödeme Yapıldı (Borçtan Düş)"):
                                odeme_durumu_degistir(secili_odeme_id, 'Ödendi')
                                st.success("Para ödendi olarak işaretlendi!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            if st.button("🔴 Geri Al / Ödenmedi Yap"):
                                odeme_durumu_degistir(secili_odeme_id, 'Bekliyor')
                                st.success("Durum geri alındı!")
                                time.sleep(1)
                                st.rerun()
                                
                # --- SATIR TAŞIMA VE SİLME ---
                st.markdown("---")
                st.subheader("🛠️ Yanlış Atılan Satırı Taşı veya Tamamen Sil")
                df['secim_metni'] = df['Sayfa'] + " | " + df['Ücret (TL)'].astype(str) + " TL (" + df['Tarih'] + ")"
                duzenlenecek_row = st.selectbox("İşlem yapılacak kaydı seçin:", df['secim_metni'].tolist(), key="duz_satir_sec")
                
                if duzenlenecek_row:
                    secili_id = int(df[df['secim_metni'] == duzenlenecek_row]['id'].values[0])
                    col_tasit, col_silme = st.columns(2)
                    with col_tasit:
                        hedef_campaign = st.selectbox("Bu kaydı hangi DOĞRU şarkıya taşıyacaksınız?", mevcut_kampanyalar_rapor, key="hedef_kamp")
                        if st.button("🔄 Seçilen Kaydı Bu Kampanyaya Taşı"):
                            kayit_guncelle(secili_id, hedef_campaign)
                            st.success("Kayıt doğru şarkıya taşındı!")
                            time.sleep(1)
                            st.rerun()
                    with col_silme:
                        st.write(" ")
                        st.write(" ")
                        if st.button("🗑️ Seçilen Kaydı Sistemden Kalıcı Olarak Sil"):
                            kayit_sil(secili_id)
                            st.success("Kayıt silindi!")
                            time.sleep(1)
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
                    st.success(f"'{yeni_sarki}' başarıyla açıldı!")
                    time.sleep(1)
                    st.rerun()
        with col_sil:
            st.subheader("🗑️ Biten Kampanyayı Sil")
            silinecek_kampanyalar = kampanyalari_getir()
            if not silinecek_kampanyalar:
                st.info("Silinecek kampanya yok.")
            else:
                silinecek_secim = st.selectbox("Silmek istediğiniz kampanyayı seçin:", silinecek_kampanyalar, key="sil_sec")
                if st.button("❌ Kampanyayı ve Tüm Kayıtları Kalıcı Sil"):
                    kampanya_sil(silinecek_secim)
                    st.success(f"🗑️ '{silinecek_secim}' başarıyla silindi!")
                    time.sleep(1)
                    st.rerun()
