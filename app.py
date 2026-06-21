import streamlit as st
import pandas as pd
import datetime
import time
import requests

# --- SAYFA AYARLARI & GÖRSEL TEMA (AGRESİF KIRMIZI & SİYAH CSS) ---
st.set_page_config(page_title="PR Kampanya & Borç Otomasyonu", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #090b0f !important; color: #f3f4f6 !important; }
    div[data-testid="stForm"] { background-color: #121620 !important; border: 2px solid #dc2626 !important; border-radius: 12px !important; padding: 20px !important; box-shadow: 0 10px 25px rgba(220, 38, 38, 0.2); }
    .stButton>button, div[data-testid="stDownloadButton"]>button { background: linear-gradient(90deg, #991b1b 0%, #dc2626 100%) !important; color: #ffffff !important; border-radius: 8px !important; border: none !important; font-weight: bold !important; font-size: 15px !important; transition: all 0.3s ease; }
    .stButton>button:hover, div[data-testid="stDownloadButton"]>button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); color: #ffffff !important; }
    input, select, textarea, div[role="listbox"] { background-color: #1b202e !important; color: #f3f4f6 !important; border: 1px solid #4b5563 !important; }
    input:focus, select:focus, textarea:focus { border-color: #dc2626 !important; box-shadow: 0 0 0 1px #dc2626 !important; }
    h1, h2, h3 { color: #dc2626 !important; font-family: 'Segoe UI', sans-serif; text-shadow: 0px 2px 8px rgba(220, 38, 38, 0.3); }
    label { color: #e5e7eb !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { color: #dc2626 !important; }
    button[data-baseweb="tab"] { color: #9ca3af !important; }
    button[aria-selected="true"] { color: #dc2626 !important; border-bottom-color: #dc2626 !important; }
    </style>
    """, unsafe_allow_html=True)

PATRON_SIFRESI = "1907"

# --- SUPABASE HTTP REST API BAĞLANTI AYARLARI ---
SUPABASE_URL = "https://lensqmqygwkhaugogvws.supabase.co"
SUPABASE_KEY = "sb_publishable_d5Ak2igKELmkIG43PGdAQw_CtyKoIRW"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- APİ TABANLI VERİ TABANI FONKSİYONLARI ---
def kampanyalari_getir(sadece_aktif=False):
    try:
        url = f"{SUPABASE_URL}/rest/v1/kampanyalar?select=kampanya_adi,aktiflik"
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            df = pd.DataFrame(r.json())
            if df.empty: return []
            if sadece_aktif:
                return df[df["aktiflik"].astype(int) == 1]["kampanya_adi"].tolist()
            return df["kampanya_adi"].tolist()
        return []
    except:
        return []

def kayitlari_getir():
    try:
        url = f"{SUPABASE_URL}/rest/v1/pr_kayitlar?select=*"
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        return pd.DataFrame(columns=["id", "tarih", "kampanya_adi", "sayfa_adi", "video_linki", "ucret", "durum"])
    except:
        return pd.DataFrame(columns=["id", "tarih", "kampanya_adi", "sayfa_adi", "video_linki", "ucret", "durum"])

def kampanya_ekle(isim):
    try:
        url = f"{SUPABASE_URL}/rest/v1/kampanyalar"
        data = {"kampanya_adi": isim.strip(), "aktiflik": 1}
        requests.post(url, headers=HEADERS, json=data)
    except:
        pass

def kampanya_aktiflik_set(isim, durum_kodu):
    try:
        url = f"{SUPABASE_URL}/rest/v1/kampanyalar?kampanya_adi=eq.{isim}"
        data = {"aktiflik": int(durum_kodu)}
        requests.patch(url, headers=HEADERS, json=data)
    except:
        pass

def kampanya_sil(isim):
    try:
        url_k = f"{SUPABASE_URL}/rest/v1/kampanyalar?kampanya_adi=eq.{isim}"
        requests.delete(url_k, headers=HEADERS)
        url_p = f"{SUPABASE_URL}/rest/v1/pr_kayitlar?kampanya_adi=eq.{isim}"
        requests.delete(url_p, headers=HEADERS)
    except:
        pass

def daha_once_gonderdi_mi(campaign, sayfa):
    try:
        url = f"{SUPABASE_URL}/rest/v1/pr_kayitlar?kampanya_adi=eq.{campaign}&sayfa_adi=ilike.{sayfa.strip()}&select=video_linki"
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

def link_kaydet(campaign, sayfa, link, ucret):
    try:
        url = f"{SUPABASE_URL}/rest/v1/pr_kayitlar"
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        data = {
            "tarih": tarih, "kampanya_adi": campaign, "sayfa_adi": sayfa.strip(), 
            "video_linki": link.strip(), "ucret": float(ucret), "durum": "Bekliyor"
        }
        requests.post(url, headers=HEADERS, json=data)
    except:
        pass

def link_guncelle_sayfa(campaign, sayfa, yeni_link):
    try:
        url = f"{SUPABASE_URL}/rest/v1/pr_kayitlar?kampanya_adi=eq.{campaign}&sayfa_adi=ilike.{sayfa.strip()}"
        data = {"video_linki": yeni_link.strip()}
        requests.patch(url, headers=HEADERS, json=data)
    except:
        pass

def odeme_durumu_degistir(kayit_id, yeni_durum):
    try:
        url = f"{SUPABASE_URL}/rest/v1/pr_kayitlar?id=eq.{int(kayit_id)}"
        data = {"durum": yeni_durum}
        requests.patch(url, headers=HEADERS, json=data)
    except:
        pass

def sayfa_tum_borclari_kapat(sayfa_ismi):
    try:
        url = f"{SUPABASE_URL}/rest/v1/pr_kayitlar?sayfa_adi=ilike.{sayfa_ismi.strip()}&durum=eq.Bekliyor"
        data = {"durum": "Ödendi"}
        requests.patch(url, headers=HEADERS, json=data)
    except:
        pass

def kayit_sil(kayit_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/pr_kayitlar?id=eq.{int(kayit_id)}"
        requests.delete(url, headers=HEADERS)
    except:
        pass

# --- ARAYÜZ BAŞLIĞI ---
st.title("🚨 BULUT KORUMALI PR KAMPANYA & TİKTOK LYRICS TAKİP SİSTEMİ 🔴")

st.sidebar.markdown("### 🔒 Yönetim Girişi")
girilen_sifre = st.sidebar.text_input("Şifre girin:", type="password", placeholder="••••")
is_patron = (girilen_sifre == PATRON_SIFRESI)

if is_patron:
    tab_link_ekle, tab_patron_paneli, tab_kampanya_yonetimi = st.tabs(["📥 Lyrics İşlemleri", "📊 Patron Rapor Odası (GİZLİ)", "⚙️ Kampanya Yönetimi"])
else:
    tab_link_ekle = st.tabs(["📥 Lyrics İşlemleri"])[0]

# --- SEKME 1: LYRICS İŞLEMLERİ ---
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
                        if daha_once_gonderdi_mi(secilen_kampanya, sayfa_adi):
                            st.error(f"❌ UYARI: {sayfa_adi} bura için zaten kayıt girmiş!")
                        else:
                            link_kaydet(secilen_kampanya, sayfa_adi, video_linki, calisilan_ucret)
                            st.success("🎉 BAŞARILI! Bilgiler buluta kaydedildi.")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("⚠️ Lütfen tüm alanları eksiksiz doldurun!")
                        
        with col_guncelle:
            st.subheader("✏️ Yanlış Girilen Linki Düzenle")
            g_kampanya = st.selectbox("Hangi Şarkının Linkini Düzelteceksiniz?", mevcut_kampanyalar_hepsi, key="g_kamp_sec")
            g_sayfa = st.text_input("Sisteme Girdiğiniz Sayfa Adınız:", placeholder="@lyrics_sayfam", key="g_sayfa_ad")
            if g_sayfa:
                eski = daha_once_gonderdi_mi(g_kampanya, g_sayfa)
                if eski:
                    st.warning(f"📋 Şu anki kayıtlı linkiniz:\n{eski[0]['video_linki']}")
                    yeni_link_girdisi = st.text_input("👉 Yeni TikTok Linkinizi Yapıştırın:", placeholder="https://vm.tiktok.com/...", key="g_yeni_link")
                    if st.button("💾 Linki Güncelle ve Kaydet"):
                        if yeni_link_girdisi:
                            link_guncelle_sayfa(g_kampanya, g_sayfa, yeni_link_girdisi)
                            st.success("✅ Linkiniz başarıyla güncellendi!")
                            time.sleep(1)
                            st.rerun()
                else:
                    st.error("🔍 Geçmiş bir kayıt bulunamadı.")

# --- SEKME 2 & 3: PATRON GİZLİ ALANLARI ---
if is_patron:
    df_genel = kayitlari_getir()
    
    with tab_patron_paneli:
        st.subheader("👑 Şirket Genel PR Bilançosu (Tüm İşlerin Toplamı)")
        if not df_genel.empty:
            genel_paylasim = len(df_genel)
            genel_borc = df_genel[df_genel['durum'] == 'Bekliyor']['ucret'].astype(float).sum()
            genel_odenen = df_genel[df_genel['durum'] == 'Ödendi']['ucret'].astype(float).sum()
            
            g1, g2, g3 = st.columns(3)
            with g1: st.metric(label="🎥 SİSTEMDEKİ TOPLAM PAYLAŞIM", value=f"{genel_paylasim} Video")
            with g2: st.metric(label="🚨 PATRONA ATILACAK TOPLAM BORÇ", value=f"{genel_borc:,.2f} TL")
            with g3: st.metric(label="✅ KAPATILAN TOPLAM ÖDEME", value=f"{genel_odenen:,.2f} TL")
            
            st.markdown("📊 **Kampanya Bazlı Borç Dağılım Raporu:**")
            ozet_liste = []
            for k in mevcut_kampanyalar_hepsi:
                k_df = df_genel[df_genel['kampanya_adi'] == k]
                k_borc = k_df[k_df['durum'] == 'Bekliyor']['ucret'].astype(float).sum()
                k_odenen = k_df[k_df['durum'] == 'Ödendi']['ucret'].astype(float).sum()
                ozet_liste.append({"Kampanya / Sanatçı Adı": k, "Toplam Video": len(k_df), "Kalan Borç (TL)": k_borc, "Ödenen Miktar (TL)": k_odenen})
            st.dataframe(pd.DataFrame(ozet_liste), use_container_width=True)
        else:
            st.info("Sistemde henüz hiçbir finansal kayıt yok.")
            
        st.markdown("---")
        st.subheader("👤 Sayfa Bazlı Toplu Hesap ve Borç Kapatma")
        if not df_genel.empty:
            mevcut_sayfalar = df_genel["sayfa_adi"].unique().tolist()
            secilen_toplu_sayfa = st.selectbox("Hesabını kapatmak istediğiniz LYRICS SAYFASINI seçin:", mevcut_sayfalar, key="toplu_sayfa_sec")
            if secilen_toplu_sayfa:
                sayfa_df = df_genel[df_genel['sayfa_adi'] == secilen_toplu_sayfa]
                s1, s2, s3 = st.columns(3)
                with s1: st.metric(label=f"🎥 Toplam Video", value=f"{len(sayfa_df)} Adet")
                with s2: st.metric(label="🔴 BU SAYFAYA TOPLAM BORÇ", value=f"{sayfa_df[sayfa_df['durum'] == 'Bekliyor']['ucret'].astype(float).sum():,.2f} TL")
                with s3: st.metric(label="🟢 SAYFAYA ÖDENEN TOPLAM", value=f"{sayfa_df[sayfa_df['durum'] == 'Ödendi']['ucret'].astype(float).sum():,.2f} TL")
                
                bekleyen_sayfa_df = sayfa_df[sayfa_df['durum'] == 'Bekliyor'][['tarih', 'kampanya_adi', 'video_linki', 'ucret']]
                if not bekleyen_sayfa_df.empty:
                    st.dataframe(bekleyen_sayfa_df, use_container_width=True)
                    if st.button(f"🚀 {secilen_toplu_sayfa} Sayfasının TÜM BORÇLARINI TEK TIKLA KAPAT"):
                        sayfa_tum_borclari_kapat(secilen_toplu_sayfa)
                        st.success("Tüm borçlar sıfırlandı!")
                        time.sleep(1)
                        st.rerun()
                        
        st.markdown("---")
        st.subheader("🔍 Şarkı Bazlı Detaylı Rapor ve İşlemler")
        if mevcut_kampanyalar_hepsi:
            izlenecek_campaign = st.selectbox("Raporunu görmek istediğiniz kampanyayı seçin:", mevcut_kampanyalar_hepsi, key="rapor_sec")
            df_sarki = df_genel[df_genel['kampanya_adi'] == izlenecek_campaign]
            if not df_sarki.empty:
                st.dataframe(df_sarki[["tarih", "sayfa_adi", "video_linki", "ucret", "durum"]], use_container_width=True)
                st.text_area("Sanatçı Link Listesi:", value="\n".join(df_sarki['video_linki'].tolist()), height=150)
                
                df_sarki['secim_metni_odeme'] = df_sarki['sayfa_adi'] + " | " + df_sarki['ucret'].astype(str) + " TL [" + df_sarki['durum'] + "]"
                secili_odeme_row = st.selectbox("Ödemesini değiştirmek istediğiniz sayfayı seçin:", df_sarki['secim_metni_odeme'].tolist(), key="odeme_satir_sec")
                if secili_odeme_row:
                    secili_id = int(df_sarki[df_sarki['secim_metni_odeme'] == secili_odeme_row]['id'].values[0])
                    curr_status = df_sarki[df_sarki['id'] == secili_id]['durum'].values[0]
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("Durumu Değiştir (Ödendi/Bekliyor)"):
                            odeme_durumu_degistir(secili_id, 'Ödendi' if curr_status == 'Bekliyor' else 'Bekliyor')
                            st.success("Durum güncellendi!")
                            time.sleep(1)
                            st.rerun()
                    with col_b2:
                        if st.button("🗑️ Bu Kaydı Sistemden Tamamen Sil"):
                            kayit_sil(secili_id)
                            st.success("Kayıt silindi!")
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
                    st.success(f"'{yeni_sarki}' başarıyla açıldı!")
                    time.sleep(1)
                    st.rerun()
        with col_durum_degis:
            st.subheader("🔒 Girişleri Kapat / Dondur")
            try:
                url = f"{SUPABASE_URL}/rest/v1/kampanyalar?select=*"
                res_detay = requests.get(url, headers=HEADERS)
                detayli_liste = res_detay.json()
            except:
                detayli_liste = []
            if detayli_liste and isinstance(detayli_liste, list):
                formatli_liste = [f"{r['kampanya_adi']} - [{'GİRİŞE AÇIK' if int(r['aktiflik'])==1 else 'DONDURULDU'}]" for r in detayli_liste]
                secilen_islem_kampanyasi = st.selectbox("Kampanya Seçin:", formatli_liste, key="durum_islem_sec")
                if secilen_islem_kampanyasi:
                    gercek_kamp_ismi = secilen_islem_kampanyasi.split(" - [")[0]
                    mevcut_aktiflik = int([r['aktiflik'] for r in detayli_liste if r['kampanya_adi'] == gercek_kamp_ismi][0])
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        if st.button("🔄 Durumu Değiştir (Aç/Dondur)"):
                            kampanya_aktiflik_set(gercek_kamp_ismi, 0 if mevcut_aktiflik == 1 else 1)
                            st.success("Durum güncellendi!")
                            time.sleep(1)
                            st.rerun()
                    with c_b2:
                        if st.button("❌ Kampanyayı Tamamen Sil"):
                            kampanya_sil(gercek_kamp_ismi)
                            st.success("Silindi!")
                            time.sleep(1)
                            st.rerun()
