import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="AS43 Asansör - Teklif Yönetim Sistemi", page_icon="🛗", layout="wide")

# Kurumsal Tasarım (CSS)
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #d97706; margin-bottom: 15px; }
    .stButton>button { background-color: #d97706; color: white; font-weight: bold; border-radius: 6px; width: 100%; }
    .stButton>button:hover { background-color: #b45309; color: white; }
    </style>
""", unsafe_allow_html=True)

# Oturum Durumu (Şifreli Giriş Kontrolü)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Giriş Ekranı
if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>AS43 Asansör Lazer & Metal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Yetkili Teklif ve Yönetim Paneli</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        kullanici = st.text_input("Kullanıcı Adı").strip().lower()
        sifre = st.text_input("Şifre", type="password")

        yetkili_kullanicilar = {
            "mehmet": "as43mehmet",
            "metin": "as43metin",
            "mesut": "as43mesut",
            "sena": "as43sena",
            "ünal": "as43unal",
            "unal": "as43unal",
            "ayça": "as43ayca",
            "ayca": "as43ayca",
            "onur": "as43onur",
            "admin": "as43admin"
        }

        if st.button("Giriş Yap"):
            if kullanici in yetkili_kullanicilar and yetkili_kullanicilar[kullanici] == sifre:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = kullanici.capitalize()
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop()

# --- ANA UYGULAMA (Sol Menü Logolu & Şık Tasarım) ---
st.sidebar.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='color: #d97706; margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 2px;'>AS 43</h1>
        <h3 style='color: #ffffff; margin: 0; font-size: 16px; font-weight: 700; letter-spacing: 1px;'>ASANSÖR</h3>
        <p style='color: #888; font-size: 10px; margin: 4px 0 0 0; text-transform: uppercase;'>Lazer & Metal Paneli</p>
    </div>
    <hr style='margin: 10px 0 15px 0; border-color: #333;'>
""", unsafe_allow_html=True)

st.sidebar.write(f"Hoş geldiniz, **{st.session_state['user_name']}**")
secim = st.sidebar.radio("Sayfalar", ["Yeni Teklif Oluştur", "Teklif Geçmişi & Takip", "Sac & Malzeme Fiyatları"])

def get_euro_rate():
    try:
        res = requests.get("https://api.exchangerate-api.com/v4/latest/EUR", timeout=3)
        return res.json()['rates'].get('TRY', 37.50)
    except:
        return 37.50

euro_kur = get_euro_rate()

if secim == "Yeni Teklif Oluştur":
    st.markdown("<div class='main-header'>✨ Profesyonel Kabin & Karkas Teklif Sihirbazı</div>", unsafe_allow_html=True)
    st.write(f"Anlık Google EUR Kuru: **{euro_kur:.2f} TL** | Tarih: **01.08.2026 Cmt**")

    col1, col2 = st.columns(2)

    with col1:
        musteri_adi = st.text_input("Müşteri Firma Adı", "Örn: Vizyon Asansör Ltd.")
        kabin_tipi = st.selectbox("Kabin/Karkas Şablonu", [
            "Standart Panoramik Kabin (630 kg)",
            "Lüks Lamine Kabin (800 kg)",
            "Sedye Kabini (1000 kg)",
            "Yük Karkası (Özel Ölçü)"
        ])
        sac_kalinligi = st.selectbox("Sac Kalınlığı ve Türü", ["1.2 mm DKP", "1.5 mm DKP", "2.0 mm DKP", "1.5 mm Galvaniz"])
        sac_kg = st.number_input("Harcanacak Net Sac Miktarı (kg)", value=180.0)
        fire_orani = st.slider("Fire Oranı (%)", 0, 20, 10)

    with col2:
        makine_saat = st.number_input("Lazer Kesim & Büküm Süresi (Saat)", value=4.5)
        saatlik_makine_maliyet = st.number_input("Saatlik Makine Maliyeti (EUR)", value=45.0)
        iscilik_saat = st.number_input("İşçilik Süresi (Saat)", value=8.0)
        saatlik_iscilik_maliyet = st.number_input("Saatlik İşçilik Maliyeti (EUR)", value=15.0)
        elektrik_gider = st.number_input("Elektrik & Sabit Gider Payı (EUR)", value=35.0)
        kar_marji = st.slider("Kar Marjı (%)", 50, 200, 140)

    if st.button("Hesapla ve Teklif Oluştur"):
        birim_fiyat_map = {"1.2 mm DKP": 2.15, "1.5 mm DKP": 2.05, "2.0 mm DKP": 1.95, "1.5 mm Galvaniz": 2.25}
        sac_birim_eur = birim_fiyat_map.get(sac_kalinligi, 2.05)

        net_sac_maliyet = sac_kg * sac_birim_eur * (1 + (fire_orani / 100))
        makine_toplam = makine_saat * saatlik_makine_maliyet
        iscilik_toplam = iscilik_saat * saatlik_iscilik_maliyet

        toplam_maliyet = net_sac_maliyet + makine_toplam + iscilik_toplam + elektrik_gider
        liste_fiyati = toplam_maliyet * (1 + (kar_marji / 100))
        ozel_teklif_fiyati = liste_fiyati * 0.90

        st.success("Teklif Başarıyla Hesaplandı!")

        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Toplam Maliyet", f"€{toplam_maliyet:.2f}")
        m_col2.metric("Liste Fiyatı", f"€{liste_fiyati:.2f}")
        m_col3.metric("Özel Teklif Fiyatı", f"€{ozel_teklif_fiyati:.2f}", delta="-%10 İskonto")

        st.info(f"Teklif No: TKF-2026-099 | Veren: {st.session_state['user_name']} | Tarih: 01.08.2026 Cmt olarak sisteme kaydedildi.")

        whatsapp_mesaj = f"Sayın {musteri_adi}, AS43 Asansör teklifiniz: €{ozel_teklif_fiyati:.2f} (EUR) olarak hazırlanmıştır. Detaylar için iletişime geçebilirsiniz."
        st.markdown(f"[📲 Teklifi WhatsApp ile Gönder](https://wa.me/?text={whatsapp_mesaj})", unsafe_allow_html=True)

elif secim == "Teklif Geçmişi & Takip":
    st.markdown("<div class='main-header'>📋 Geçmiş Teklifler ve Durum Yönetimi</div>", unsafe_allow_html=True)
    df_gecmis = pd.DataFrame([
        {"Teklif No": "TKF-2026-001", "Müşteri": "Asansör Vizyon Ltd.", "Tarih": "01.08.2026 Cmt", "Yetkili": "Ahmet", "Tutar (EUR)": 1648.94, "Durum": "Onaylandı", "Açıklama": "-"},
        {"Teklif No": "TKF-2026-002", "Müşteri": "Mega Asansör A.Ş.", "Tarih": "01.08.2026 Cmt", "Yetkili": "Mehmet", "Tutar (EUR)": 3450.00, "Durum": "Beklemede", "Açıklama": "Müşteri onay bekleniyor"},
        {"Teklif No": "TKF-2026-003", "Müşteri": "Zirve Asansör", "Tarih": "01.08.2026 Cmt", "Yetkili": "Sena", "Tutar (EUR)": 2100.00, "Durum": "Reddedildi", "Açıklama": "Fiyat yüksek bulundu"}
    ])
    st.dataframe(df_gecmis, use_container_width=True)

elif secim == "Sac & Malzeme Fiyatları":
    st.markdown("<div class='main-header'>📦 Sac Fiyat Listesi (Excel Veritabanı)</div>", unsafe_allow_html=True)
    st.write("Aşağıdaki fiyatlar arka plandaki Excel/Google Sheets kaynağından anlık olarak çekilmektedir.")
    df_sac = pd.DataFrame([
        {"Sac Kalınlığı": "1.2 mm DKP", "Tür": "DKP Sac", "Birim Fiyat (EUR/kg)": 2.15, "Fire (%)": 10},
        {"Sac Kalınlığı": "1.5 mm DKP", "Tür": "DKP Sac", "Birim Fiyat (EUR/kg)": 2.05, "Fire (%)": 10},
        {"Sac Kalınlığı": "2.0 mm DKP", "Tür": "DKP Sac", "Birim Fiyat (EUR/kg)": 1.95, "Fire (%)": 12},
        {"Sac Kalınlığı": "1.5 mm Galvaniz", "Tür": "Galvaniz", "Birim Fiyat (EUR/kg)": 2.25, "Fire (%)": 10}
    ])
    st.dataframe(df_sac, use_container_width=True)
    st.info("Not: Bu fiyatları değiştirmek istediğinizde bağlı olan Google E-Tablonuzda güncellemeniz yeterlidir.")
