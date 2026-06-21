import streamlit as st
from streamlit_gsheets import GSheetsConnection
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

PATRON_SIFRESI = "1907"

# --- GOOGLE SHEETS BAĞLANTISI ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Sayfaları canlı oku
    try:
        df_kampanyalar = conn.read(worksheet="Kampanyalar", ttl=0)
        df_kampanyalar = df_kampanyalar.dropna(how='all')
    except:
        df_kampanyalar = pd.DataFrame(columns=["kampanya_adi", "aktiflik"])
        conn.update(worksheet="Kampanyalar", data=df_kampanyalar)
        
    try:
        df_kayitlar = conn.read(worksheet="Kayitlar", ttl=0)
        df_kayitlar = df_kayitlar.dropna(how='all')
    except:
        df_kayitlar = pd.DataFrame(columns=["id", "tarih", "kampanya_adi", "sayfa_adi", "video_linki", "ucret", "durum"])
        conn.update(worksheet="Kayitlar", data=df_kayitlar)
except Exception as e:
    st.error(f"Google Sheets Bağlantı Hatası! Lütfen Secrets alanını kontrol edin. Hata: {e}")
    st.stop()

# --- YARDIMCI FONKSİYONLAR ---
def kampanyalari_getir(sadece_aktif=False):
    if df_kampanyalar.empty: return []
    if sadece_aktif:
        return df_kampanyalar[df_kampanyalar["aktiflik"].astype(int) == 1]["kampanya_adi"].tolist()
    return df_kampanyalar["kampanya_adi"].tolist()

def sayfaları_getir():
    if df_kayitlar.empty: return []
    return df_kayitlar["sayfa_adi"].dropna().unique().tolist()

# --- ARAYÜZ BAŞLIĞI ---
st.title("🚨 G-DRIVE KORUMALI PR KAMPANYA TAKİP SİSTEMİ 🔴")

st.sidebar.markdown("### 📊 Sistem Güvencesi")
st.sidebar.success("Verileriniz Doğrudan Google Drive Hesabınızda Depolanıyor!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 Yönetim Girişi")
girilen_sifre = st.sidebar.text_input("Şifre girin:", type="password", placeholder="••••")

is_patron = (girilen_sifre == PATRON_SIFRESI)

if is_patron:
    tab_link_ekle, tab_patron_paneli, tab_kampanya_yonetimi = st.tabs([
        "📥 Lyrics İşlemleri", "📊 Patron Rapor Odası (GİZLİ)", "⚙️ Kampanya Yönetimi"
    ])
else:
    tab_link_ekle = st.tabs(["📥 Lyrics İşlemleri"])[0]

# --- SEKME 1: LYRICS İŞLEMLERİ ---
with tab_link_ekle:
    st.error("🚨 DİKKAT: Lütfen formu doldurmadan önce DOĞRU ŞARKIYI seçtiğinizden emin olun!")
    mevcut_kampanyalar_aktif = kampanyalari_getir(sadece_aktif=True)
    mevcut_kampanyalar_hepsi = kampanyalari_getir(sadece_aktif=False)
    
    if not mevcut_kampanyalar_aktif:
        st.warning("Henüz aktif bir PR kampanyası bulunmuyor.")
    else:
        col_form, col_guncelle = st.columns(2)
        
        with col_form:
            st.subheader("📥 Yeni Video Bildirim Formu")
            with st.form("sayfa_giriş_formu", clear_on_submit=False):
                secilen_kampanya = st.selectbox("🎯 Reklamını Yaptığınız Şarkıyı Seçin:", mevcut_kampanyalar_aktif)
                sayfa_adi = st.text_input("TikTok Sayfa Adınız:", placeholder="@lyrics_sayfam")
                video_linki = st.text_input("Paylaşılan Video Linki:", placeholder="https://vm.tiktok.com/...")
                calisilan_ucret = st.number_input("Anlaşılan Ücret (TL):", min_value=0.0, step=50.0, value=0.0)
                
                submit_butonu = st.form_submit_button("🚀 Bilgileri Gönder ve Kaydet")
                
                if submit_butonu:
                    if sayfa_adi and video_linki and calisilan_ucret > 0:
                        var_mi = False
                        if not df_kayitlar.empty:
                            check = df_kayitlar[(df_kayitlar["kampanya_adi"] == secilen_kampanya) & (df_kayitlar["sayfa_adi"].str.lower().str.strip() == sayfa_adi.lower().strip())]
                            if not check.empty: var_mi = True
                        
                        if var_mi:
                            st.error(f"❌ UYARI: {sayfa_adi} bu şarkı için zaten kayıt girmiş!")
                        else:
                            yeni_id = len(df_kayitlar) + 1
                            yeni_satir = pd.DataFrame([{
                                "id": yeni_id,
                                "tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "kampanya_adi": secilen_kampanya,
                                "sayfa_adi": sayfa_adi.strip(),
                                "video_linki": video_linki.strip(),
                                "ucret": calisilan_ucret,
                                "durum": "Bekliyor"
                            }])
                            df_yeni = pd.concat([df_kayitlar, yeni_satir], ignore_index=True)
                            conn.update(worksheet="Kayitlar", data=df_yeni)
                            st.success("🎉 Başarıyla Google Drive'a kaydedildi!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("⚠️ Lütfen tüm alanları doldurun!")

        with col_guncelle:
            st.subheader("✏️ Yanlış Girilen Linki Düzenle")
            g_kampanya = st.selectbox("Hangi Şarkının Linkini Düzelteceksiniz?", mevcut_kampanyalar_hepsi, key="g_k")
            g_sayfa = st.text_input("Sisteme Girdiğiniz Sayfa Adınız:", placeholder="@lyrics_sayfam", key="g_s")
            
            if g_sayfa and not df_kayitlar.empty:
                filtre = df_kayitlar[(df_kayitlar["kampanya_adi"] == g_kampanya) & (df_kayitlar["sayfa_adi"].str.lower().str.strip() == g_sayfa.lower().strip())]
                if not filtre.empty:
                    st.warning(f"📋 Mevcut Link: {filtre.iloc[0]['video_linki']}")
                    yeni_link = st.text_input("👉 Yeni Doğru Linki Girin:", key="g_yl")
                    if st.button("💾 Güncelle"):
                        if yeni_link:
                            df_kayitlar.loc[(df_kayitlar["kampanya_adi"] == g_kampanya) & (df_kayitlar["sayfa_adi"].str.lower().str.strip() == g_sayfa.lower().strip()), "video_linki"] = yeni_link.strip()
                            conn.update(worksheet="Kayitlar", data=df_kayitlar)
                            st.success("Link güncellendi!")
                            time.sleep(1)
                            st.rerun()
                else:
                    st.error("Kayıt bulunamadı.")

# --- PATRON GİZLİ ALANLARI ---
if is_patron:
    with tab_patron_paneli:
        st.subheader("👑 Şirket Genel PR Bilançosu")
        
        if not df_kayitlar.empty:
            genel_paylasim = len(df_kayitlar)
            genel_borc = df_kayitlar[df_kayitlar['durum'] == 'Bekliyor']['ucret'].astype(float).sum()
            genel_odenen = df_kayitlar[df_kayitlar['durum'] == 'Ödendi']['ucret'].astype(float).sum()
            
            g1, g2, g3 = st.columns(3)
            with g1: st.metric(label="🎥 TOPLAM PAYLAŞIM", value=f"{genel_paylasim} Video")
            with g2: st.metric(label="🚨 PATRONA ATILACAK BORÇ", value=f"{genel_borc:,.2f} TL")
            with g3: st.metric(label="✅ KAPATILAN ÖDEME", value=f"{genel_odenen:,.2f} TL")
            
            st.markdown("---")
            st.subheader("👤 Sayfa Bazlı Toplu Borç Kapatma")
            mevcut_sayfalar = sayfaları_getir()
            if mevcut_sayfalar:
                sec_sayfa = st.selectbox("Hesap Kapatılacak Sayfa:", mevcut_sayfalar)
                sayfa_df = df_kayitlar[df_kayitlar['sayfa_adi'] == sec_sayfa]
                st.metric(label="🔴 TOPLAM BORCU", value=f"{sayfa_df[sayfa_df['durum'] == 'Bekliyor']['ucret'].astype(float).sum():,.2f} TL")
                if st.button("🚀 Bu Sayfanın Tüm Borçlarını Sıfırla"):
                    df_kayitlar.loc[(df_kayitlar['sayfa_adi'] == sec_sayfa) & (df_kayitlar['durum'] == 'Bekliyor'), 'durum'] = 'Ödendi'
                    conn.update(worksheet="Kayitlar", data=df_kayitlar)
                    st.success("Borçlar kapatıldı!")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("---")
            st.subheader("🔍 Şarkı Bazlı Detaylı Rapor")
            if mevcut_kampanyalar_hepsi:
                iz_kamp = st.selectbox("Raporlanacak Şarkı:", mevcut_kampanyalar_hepsi, key="iz_k")
                sub_df = df_kayitlar[df_kayitlar['kampanya_adi'] == iz_kamp]
                if not sub_df.empty:
                    st.dataframe(sub_df[["tarih", "sayfa_adi", "video_linki", "ucret", "durum"]], use_container_width=True)
                    st.text_area("Link Listesi:", value="\n".join(sub_df['video_linki'].tolist()), height=150)
                    
                    sub_df['secim_metni'] = sub_df['sayfa_adi'] + " | " + sub_df['ucret'].astype(str) + " TL [" + sub_df['durum'] + "]"
                    secili_satir = st.selectbox("Tekil İşlem Yapılacak Kayıt:", sub_df['secim_metni'].tolist())
                    if secili_satir:
                        target_id = sub_df[sub_df['secim_metni'] == secili_satir].iloc[0]['id']
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("Durumu Değiştir (Ödendi/Bekliyor)"):
                                curr = df_kayitlar.loc[df_kayitlar['id'] == target_id, 'durum'].values[0]
                                df_kayitlar.loc[df_kayitlar['id'] == target_id, 'durum'] = 'Ödendi' if curr == 'Bekliyor' else 'Bekliyor'
                                conn.update(worksheet="Kayitlar", data=df_kayitlar)
                                st.success("Durum güncellendi!")
                                time.sleep(1)
                                st.rerun()
                        with col_b2:
                            if st.button("🗑️ Bu Satırı Tamamen Sil"):
                                df_kayitlar = df_kayitlar[df_kayitlar['id'] != target_id]
                                conn.update(worksheet="Kayitlar", data=df_kayitlar)
                                st.success("Satır silindi!")
                                time.sleep(1)
                                st.rerun()
        else:
            st.info("Kayıtlı veri yok.")

    with tab_kampanya_yonetimi:
        col_e, col_d = st.columns(2)
        with col_e:
            st.subheader("➕ Yeni Kampanya Başlat")
            y_sarki = st.text_input("Şarkı / Sanatçı İsmi:")
            if st.button("🚀 Kampanyayı Aç"):
                if y_sarki:
                    yeni_k_satir = pd.DataFrame([{"kampanya_adi": y_sarki.strip(), "aktiflik": 1}])
                    df_kampanyalar = pd.concat([df_kampanyalar, yeni_k_satir], ignore_index=True)
                    conn.update(worksheet="Kampanyalar", data=df_kampanyalar)
                    st.success("Kampanya açıldı!")
                    time.sleep(1)
                    st.rerun()
        with col_d:
            st.subheader("⚙️ Kampanya Durum Yönetimi & Tamamen Silme")
            if not df_kampanyalar.empty:
                df_kampanyalar['formatli'] = df_kampanyalar['kampanya_adi'] + " - " + df_kampanyalar['aktiflik'].apply(lambda x: "[AÇIK]" if int(x)==1 else "[DONDURULDU]")
                sec_islem = st.selectbox("İşlem Yapılacak Kampanya:", df_kampanyalar['formatli'].tolist())
                if sec_islem:
                    gercek_isim = sec_islem.split(" - ")[0]
                    curr_aktif = int(df_kampanyalar[df_kampanyalar['kampanya_adi'] == gercek_isim].iloc[0]['aktiflik'])
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("🔄 Durumu Tersine Çevir (Aç/Dondur)"):
                            df_kampanyalar.loc[df_kampanyalar['kampanya_adi'] == gercek_isim, 'aktiflik'] = 0 if curr_aktif == 1 else 1
                            conn.update(worksheet="Kampanyalar", data=df_kampanyalar)
                            st.success("Kampanya durumu güncellendi!")
                            time.sleep(1)
                            st.rerun()
                    with c2:
                        if st.button("🗑️ Kampanyayı ve TÜM Bağlı Kayıtları Kalıcı Sil"):
                            df_kampanyalar = df_kampanyalar[df_kampanyalar['kampanya_adi'] != gercek_isim]
                            if not df_kayitlar.empty:
                                df_kayitlar = df_kayitlar[df_kayitlar['kampanya_adi'] != gercek_isim]
                            conn.update(worksheet="Kampanyalar", data=df_kampanyalar)
                            conn.update(worksheet="Kayitlar", data=df_kayitlar)
                            st.success("Her şey kalıcı olarak silindi!")
                            time.sleep(1)
                            st.rerun()
