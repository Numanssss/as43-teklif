# --- 0.DEV0 GEÇERSİZ SÜRÜM HATASINI ÇÖZEN GLOBAL MONKEYPATCH ---
try:
    import packaging.version
    original_init = packaging.version.Version.__init__
    def patched_init(self, version):
        try:
            original_init(self, version)
        except Exception:
            original_init(self, "0.0.0")
    packaging.version.Version.__init__ = patched_init
except Exception:
    pass

import streamlit as st
import pandas as pd
import os
import datetime
import urllib.request
import urllib.parse
import json
import hashlib

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="AS43 Grup | Metal & Asansör ERP", layout="wide", page_icon="💠")

# --- KURUMSAL BRANDING & PREMIUM CSS (Koyu Tema & Glowing Efektler - Turuncu/Kehribar Tonları) ---
st.markdown("""
    <style>
    /* Global sayfa arka planı */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Üst Kurumsal Çizgi (Premium Turuncu) */
    header[data-testid="stHeader"] {
        border-top: 6px solid #F59E0B;
        background-color: #0f172a;
    }
    
    /* Başlık stili */
    .main-title {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Montserrat', sans-serif;
        text-align: center;
        font-weight: 850;
        font-size: 2.3rem;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        color: #94a3b8;
        font-family: 'Montserrat', sans-serif;
        text-align: center;
        font-size: 0.95rem;
        margin-bottom: 1.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Gelişmiş Bilgi Kartları (KPI Cards) */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.3rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -3px rgba(245, 158, 11, 0.25);
        border-color: #F59E0B;
    }
    .metric-val {
        font-size: 2.0rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    /* Stok Kart Stilleri */
    .stock-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        margin-bottom: 1rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stock-card:hover {
        border-color: #F59E0B;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
    }
    
    /* Teklif Sihirbazı Fiyat Özet Kartı (Turuncu Glow) */
    .quote-result-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #F59E0B;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
    }
    
    /* Koyu Temaya Özel Transparent Logo Taşıyıcı */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        margin-bottom: 10px;
    }
    .logo-img {
        max-width: 240px;
        filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.4)) brightness(1.0);
        background-color: transparent;
    }
    
    /* Özelleştirilmiş Buton Stili (Turuncu Gradyan) */
    div.stButton > button { 
        background: linear-gradient(135deg, #B45309 0%, #F59E0B 100%) !important; 
        color: white !important; 
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.8rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.3) !important;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px -3px rgba(245, 158, 11, 0.5) !important;
    }
    
    /* Durum Etiketleri */
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 0.85rem;
        display: inline-block;
        text-align: center;
    }
    .badge-onay { background-color: #15803d; color: #f8fafc; }
    .badge-bekle { background-color: #a16207; color: #f8fafc; }
    .badge-red { background-color: #b91c1c; color: #f8fafc; }
    
    .badge-odeme-alindi { background-color: #1d4ed8; color: #f8fafc; }
    .badge-odeme-bekliyor { background-color: #4b5563; color: #f8fafc; }
    .badge-odeme-gecikti { background-color: #b91c1c; color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ TABANI DOSYA YOLLARI ---
FILE_ASANSOR = "asansor_verileri.csv"
FILE_STOK = "metal_stok.csv"
FILE_GIDERLER = "metal_giderler.csv"
FILE_GELIRLER = "metal_gelirler.csv"
FILE_SAC_FIYATLARI = "sac_fiyatlari.csv"
FILE_TEKLIFLER = "teklifler.csv"
FILE_SMTP_AYARLARI = "smtp_ayarlari.json"

def generate_pdf(teklif_no, hazirlayan, musteri_adi, sablon, secilen_sac, sac_kalinligi, net_agirlik, fire_orani, hammadde_maliyeti_eur, lazer_suresi, lazer_maliyeti_eur, bukum_suresi, bukum_maliyeti_eur, iscilik_suresi, iscilik_maliyeti_eur, sabit_gider_payi, sabit_gider_maliyeti_eur, toplam_maliyet_eur, liste_fiyati_eur, liste_fiyati_try, active_rate, iskonto_orani, iskonto_tutari_eur, kdv_orani, kdv_tutari_eur, genel_toplam_eur):
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
                        if os.path.exists("logo.png"):
            self.set_fill_color(30, 41, 59)
            self.rect(10, 8, 32, 14, 'F')
            self.image("logo.png", 11, 9, 30)
            self.set_x(45)
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(217, 119, 6)
            self.cell(0, 8, 'AS43 GRUP LAZER & METAL ERP', ln=True, align='L')
            self.set_x(45)
            self.set_font('Helvetica', '', 9)
            self.set_text_color(100, 116, 139)
            self.cell(0, 5, 'Teklif & Operasyon Hizmetleri Detay Formu', ln=True, align='L')
                        else:
            self.set_font('Helvetica', 'B', 15)
            self.set_text_color(217, 119, 6)
            self.cell(0, 10, 'AS43 GRUP LAZER & METAL ERP', ln=True, align='C')
            
        self.set_draw_color(217, 119, 6)
        self.line(10, 27, 200, 27)
        self.ln(8)
            
                        def footer(self):
            self.set_y(-25)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(148, 163, 184)
            self.cell(0, 10, f'Sayfa {self.page_no()}/{{nb}} | AS43 ERP Raporlama Hizmeti', align='C')

    def clean(t):
        if not t: return ""
        t = str(t)
        replacements = {
            'ı': 'i', 'İ': 'I', 'ş': 's', 'Ş': 'S',
            'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U',
            'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C',
            '€': 'EUR'
        }
        for k, v in replacements.items():
            t = t.replace(k, v)
        return t

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Sağ Üst Köşe: Teklif No ve Hazırlayan Bilgisi
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, f"Teklif No: {clean(teklif_no)}", ln=True, align='R')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, f"Hazirlayan: {clean(hazirlayan)}", ln=True, align='R')
    pdf.cell(0, 5, f"Tarih: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True, align='R')
    pdf.ln(3)
    
    # Müşteri Bilgileri
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(217, 119, 6)
    pdf.cell(0, 8, "MUSTERI VE HESAP BILGILERI", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.ln(2)
    
    pdf.cell(50, 6, "Musteri Adi:", 0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 6, clean(musteri_adi), 0, 1)
    pdf.set_font('Helvetica', '', 10)
    
    pdf.cell(50, 6, "Urun Sablonu:", 0)
    pdf.cell(0, 6, clean(sablon), 0, 1)
    
    pdf.cell(50, 6, "Sac Malzeme Tipi:", 0)
    pdf.cell(0, 6, f"{clean(secilen_sac)} ({sac_kalinligi} mm)", 0, 1)
    
    pdf.cell(50, 6, "Net Agirlik:", 0)
    pdf.cell(0, 6, f"{net_agirlik:.2f} kg (Fire Orani: %{fire_orani:.0f})", 0, 1)
    pdf.ln(4)
    
    # Tablo Detayları
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(217, 119, 6)
    pdf.cell(0, 8, "MALIYET VE OPERASYON DETAYLARI", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    
    pdf.set_fill_color(217, 119, 6)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(85, 7, "  Maliyet Kalemi / Operasyon", 1, 0, 'L', fill=True)
    pdf.cell(50, 7, "Detay", 1, 0, 'C', fill=True)
    pdf.cell(55, 7, "Tutar (EUR)  ", 1, 1, 'R', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 9)
    
    pdf.cell(85, 6, "  Hammadde Maliyeti", 1, 0, 'L')
    pdf.cell(50, 6, f"{net_agirlik:.1f} kg", 1, 0, 'C')
    pdf.cell(55, 6, f"{hammadde_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, "  Lazer Kesim Maliyeti (Birim Dk)", 1, 0, 'L')
    pdf.cell(50, 6, f"{lazer_suresi:.1f} dk", 1, 0, 'C')
    pdf.cell(55, 6, f"{lazer_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, "  Bukum Maliyeti (Birim Dk)", 1, 0, 'L')
    pdf.cell(50, 6, f"{bukum_suresi:.1f} dk", 1, 0, 'C')
    pdf.cell(55, 6, f"{bukum_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, "  Iscilik & Montaj Maliyeti (Birim Dk)", 1, 0, 'L')
    pdf.cell(50, 6, f"{iscilik_suresi:.1f} dk", 1, 0, 'C')
    pdf.cell(55, 6, f"{iscilik_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, f"  Enerji & Sabit Giderler Payi (%{sabit_gider_payi})", 1, 0, 'L')
    pdf.cell(50, 6, "", 1, 0, 'C')
    pdf.cell(55, 6, f"{sabit_gider_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(135, 7, "Toplam Net Maliyet:  ", 1, 0, 'R')
    pdf.cell(55, 7, f"{toplam_maliyet_eur:.2f} EUR  ", 1, 1, 'R')
    
    # İskonto, KDV ve Genel Toplam Hesaplamaları
    pdf.cell(135, 6, f"Liste Satis Fiyati (Brut):  ", 1, 0, 'R')
    pdf.cell(55, 6, f"{liste_fiyati_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(135, 6, f"Uygulanan Iskonto (%{iskonto_orani}):  ", 1, 0, 'R')
    pdf.cell(55, 6, f"- {iskonto_tutari_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(135, 6, f"KDV Dahil Olmayan Ara Toplam:  ", 1, 0, 'R')
    pdf.cell(55, 6, f"{(liste_fiyati_eur - iskonto_tutari_eur):.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(135, 6, f"KDV (%{kdv_orani}):  ", 1, 0, 'R')
    pdf.cell(55, 6, f"{kdv_tutari_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.set_fill_color(254, 243, 199)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(217, 119, 6)
    pdf.cell(135, 9, "GENEL TOPLAM (KDV DAHIL):  ", 1, 0, 'R', fill=True)
    pdf.cell(55, 9, f"{genel_toplam_eur:.2f} EUR  ", 1, 1, 'R', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'I', 8.5)
    pdf.cell(0, 6, f"Euro Kuru: {active_rate:.2f} TRY | TL Karsiligi: {(genel_toplam_eur * active_rate):,.2f} TL", ln=True, align='R')
    pdf.ln(8)
    
    # Kaşe ve İmza Alanı
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(217, 119, 6)
    pdf.cell(0, 6, "KASE VE IMZA ONAY ALANI", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 9)
    y_start = pdf.get_y()
    
    # Firma Kaşe Alanı (Sol)
    pdf.set_xy(15, y_start)
    pdf.cell(80, 5, "AS43 GRUP LAZER & METAL", ln=True, align='C')
    pdf.set_x(15)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(80, 4, "(Firma Kase & Yetkili Imza)", ln=True, align='C')
    pdf.ln(12)
    pdf.set_x(15)
    pdf.cell(80, 4, "____________________________", ln=True, align='C')
    
    # Müşteri Onay Alanı (Sağ)
    pdf.set_xy(110, y_start)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(80, 5, clean(musteri_adi), ln=True, align='C')
    pdf.set_xy(110, pdf.get_y())
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(80, 4, "(Alici Firma Kase & Imza)", ln=True, align='C')
    pdf.ln(12)
    pdf.set_xy(110, pdf.get_y())
    pdf.cell(80, 4, "____________________________", ln=True, align='C')
    
    return pdf.output()

def send_email_with_pdf(receiver_email, subject, body, pdf_bytes, filename, smtp_server, smtp_port, sender_email, sender_password):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True, "E-posta başarıyla gönderildi!"
    except Exception as e:
        return False, f"E-posta gönderim hatası: {str(e)}"

# Varsayılan kolon şablonları
DEFAULT_HEADERS_ASANSOR = ["Asansör_ID", "Konum", "Durum (Etiket)", "Son_Bakım_Notları", "Bekleyen_Eksikler", "Adres"]

# --- HATA ÖNLEME: VERİ TABANLARI YOKSA OLUŞTURMA ---
def init_databases():
    if not os.path.exists(FILE_ASANSOR):
        df = pd.DataFrame(columns=DEFAULT_HEADERS_ASANSOR)
        df.to_csv(FILE_ASANSOR, index=False, encoding='utf-8-sig')

    if not os.path.exists(FILE_STOK):
        df_stok_template = pd.DataFrame({
            "Malzeme_Tipi": [
                "Paslanmaz Çelik",
                "Aynalı Paslanmaz",
                "Desenli / Dekoratif Paslanmaz",
                "Satine Paslanmaz",
                "Laminat / Kompakt Laminat Kaplama",
                "Elektrostatik Boyalı Sac"
            ],
            "Miktar_kg": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        })
        df_stok_template.to_csv(FILE_STOK, index=False, encoding='utf-8-sig')

    if not os.path.exists(FILE_GIDERLER):
        df_gider_template = pd.DataFrame(columns=["Tarih", "Kategori", "Alt_Kategori", "Tutar_TL", "Açıklama"])
        df_gider_template.to_csv(FILE_GIDERLER, index=False, encoding='utf-8-sig')

    if not os.path.exists(FILE_GELIRLER):
        df_gelir_template = pd.DataFrame(columns=["Tarih", "Müşteri", "Ödeme_Yöntemi", "Tutar_TL", "Çek_Vadesi", "Açıklama"])
        df_gelir_template.to_csv(FILE_GELIRLER, index=False, encoding='utf-8-sig')

    if not os.path.exists(FILE_SAC_FIYATLARI):
        df_sac_template = pd.DataFrame({
            "Malzeme_Tipi": [
                "Paslanmaz Çelik",
                "Aynalı Paslanmaz",
                "Desenli / Dekoratif Paslanmaz",
                "Satine Paslanmaz",
                "Laminat / Kompakt Laminat Kaplama",
                "Elektrostatik Boyalı Sac"
            ],
            "Birim_Fiyat_EUR_kg": [3.20, 4.50, 5.50, 3.80, 6.00, 1.80]
        })
        df_sac_template.to_csv(FILE_SAC_FIYATLARI, index=False, encoding='utf-8-sig')

    if not os.path.exists(FILE_TEKLIFLER):
        df_teklif_template = pd.DataFrame(columns=[
            "Teklif_ID", "Tarih", "Musteri", "Sablon", "Malzeme_Tipi", "Kalinlik_mm", 
            "Net_Agirlik_kg", "Fire_Orani", "Tutar_EUR", "Tutar_TRY", "Durum", 
            "Hazirlayan", "Iletim_Durumu", "Odeme_Durumu"
        ])
        df_teklif_template.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')

init_databases()

# --- VERİLERİ YÜKLEME ---
try:
    df_asansor = pd.read_csv(FILE_ASANSOR, encoding='utf-8-sig').dropna(how='all')
    df_asansor.columns = [c.strip() for c in df_asansor.columns]
    
    df_stok = pd.read_csv(FILE_STOK, encoding='utf-8-sig').dropna(how='all')
    
    df_gider = pd.read_csv(FILE_GIDERLER, encoding='utf-8-sig').dropna(how='all')
    df_gider["Tarih"] = pd.to_datetime(df_gider["Tarih"])
    df_gider["Tutar_TL"] = df_gider["Tutar_TL"].astype(float)
    
    df_gelir = pd.read_csv(FILE_GELIRLER, encoding='utf-8-sig').dropna(how='all')
    df_gelir["Tarih"] = pd.to_datetime(df_gelir["Tarih"])
    df_gelir["Tutar_TL"] = df_gelir["Tutar_TL"].astype(float)

    df_sac_fiyatlari = pd.read_csv(FILE_SAC_FIYATLARI, encoding='utf-8-sig').dropna(how='all')
    df_teklifler = pd.read_csv(FILE_TEKLIFLER, encoding='utf-8-sig').dropna(how='all')
except Exception as e:
    st.error(f"Veritabanı yükleme hatası: {e}")
    st.stop()

# Sütun denetimi
if "Iletim_Durumu" not in df_teklifler.columns:
    df_teklifler["Iletim_Durumu"] = "Gönderilmedi"
if "Odeme_Durumu" not in df_teklifler.columns:
    df_teklifler["Odeme_Durumu"] = "Ödeme Bekleniyor"
if "Hazirlayan" not in df_teklifler.columns:
    df_teklifler["Hazirlayan"] = "Bilinmiyor"

# --- 📱 MOBİL QR TARAMA SİMÜLATÖRÜ ---
if "id" in st.query_params:
    scan_id = st.query_params["id"]
    
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    if os.path.exists("asansor_logo.png"):
        st.markdown(f"<img src='data:image/png;base64,{urllib.parse.quote(open('asansor_logo.png', 'rb').read())}' class='logo-img'>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color:#F59E0B;'>AS43 ASANSÖR</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='main-title'>📱 Mobil QR Tarama Servisi</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='main-subtitle'>{scan_id} Asansör Durum ve Bakım Raporu</div>", unsafe_allow_html=True)
    
    col_id = "Asansör_ID"
    col_konum = "Konum"
    col_durum = "Durum (Etiket)"
    col_bakim = "Son_Bakım_Notları"
    col_eksik = "Bekleyen_Eksikler"
    col_adres = "Adres"
    
    satir = df_asansor[df_asansor[col_id].astype(str) == str(scan_id)]
    if not satir.empty:
        d = satir.iloc[0]
        val_durum = str(d[col_durum]).strip()
        color = "#22c55e" if val_durum.lower() == "mavi" else "#ef4444"
        
        st.markdown(f"""
        <div style='background: #1e293b; border-left: 8px solid {color}; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3); color: #f8fafc;'>
            <h3 style='margin-top:0; color:#F59E0B;'>🛠️ Sistem Kaydı: {scan_id}</h3>
            <p style='margin: 8px 0;'><b>📍 Konum:</b> {d[col_konum]}</p>
            <p style='margin: 8px 0;'><b>⚡ Mevcut Etiket Durumu:</b> <span style='background: {color}; color: white; padding: 3px 10px; border-radius: 6px; font-weight: bold;'>{val_durum} Etiket</span></p>
            <p style='margin: 8px 0;'><b>📝 Son Bakım Notu:</b> {d[col_bakim]}</p>
            <p style='margin: 8px 0;'><b>❌ Bekleyen Eksik:</b> {d[col_eksik]}</p>
            <p style='margin: 8px 0;'><b>🏠 Bina Adresi:</b> {d[col_adres]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Bu ekran saha teknisyenlerinin anlık sorgulama yapması için açık durumdadır.")
    else:
        st.error("Kayıt bulunamadı.")
    st.stop()

# --- GÜVENLİ YETKİLENDİRME (AUTH) SİSTEMİ ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

USER_PASSWORDS = {
    "ahmet": "as43ahmet",
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

USER_DB = {username: hash_password(password) for username, password in USER_PASSWORDS.items()}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Giriş Ekranına Özel CSS Enjeksiyonu (Maksimum Turuncu Detaylar)
    st.markdown("""
        <style>
        div[data-testid="stForm"] {
            background: #1e293b !important;
            border: 2px solid #F59E0B !important;
            border-radius: 16px !important;
            padding: 2.5rem !important;
            max-width: 480px !important;
            margin: 5% auto !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("login_form"):
            # Logo ve Firma Görseli Koyu Temaya Uygun Olarak Yükleniyor
            if os.path.exists("asansor_logo.png"):
                import base64
                with open("asansor_logo.png", "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                st.markdown(f"""
                    <div class="logo-container">
                        <img src="data:image/png;base64,{encoded_string}" class="logo-img" />
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='color: #F59E0B; font-weight:800; text-align:center;'>AS43 GRUP</h1>", unsafe_allow_html=True)
                
            st.markdown("<h3 style='margin-top: 5px; margin-bottom: 5px; color:#f8fafc; text-align:center;'>Yönetim Portalı Girişi</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; text-align:center;'>Güvenli ERP ve Teklif Yönetim Alanı</p>", unsafe_allow_html=True)
            
            username_input = st.text_input("👤 Kullanıcı Adı:", placeholder="Kullanıcı adınızı girin").lower().strip()
            password_input = st.text_input("🔑 Şifre:", type="password", placeholder="Şifrenizi girin").strip()
            submit_login = st.form_submit_button("Giriş Yap 🚀")
            
            if submit_login:
                is_valid = False
                if username_input in USER_DB:
                    correct_password = USER_PASSWORDS[username_input]
                    if password_input == correct_password or hash_password(password_input) == USER_DB[username_input]:
                        is_valid = True
                
                if is_valid:
                    st.session_state["authenticated"] = True
                    if username_input in ["unal", "ünal"]:
                        display_name = "Ünal"
                    elif username_input in ["ayca", "ayça"]:
                        display_name = "Ayça"
                    else:
                        display_name = username_input.capitalize()
                        
                    st.session_state["username"] = display_name
                    st.success("Giriş Başarılı! Konsol Yükleniyor...")
                    st.rerun()
                else:
                    st.error("Hatalı Kullanıcı Adı veya Şifre!")
        
        st.markdown("<p style='font-size:0.75rem; color:#64748b; margin-top:20px; text-align:center;'>Yetki veya şifre sıfırlama taleplerinizi sistem yöneticisine bildiriniz.</p>", unsafe_allow_html=True)
    st.stop()

# --- ANLIK EUR/TRY DÖVİZ ENTEGRASYONU ---
@st.cache_data(ttl=3600)
def get_live_eur_rate():
    try:
        url = "https://open.er-api.com/v6/latest/EUR"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            res_data = json.loads(response.read().decode())
            if res_data.get("result") == "success":
                return float(res_data["rates"]["TRY"])
    except Exception:
        pass
    return 38.50

if "exchange_mode" not in st.session_state:
    st.session_state["exchange_mode"] = "Canlı"
if "live_rate" not in st.session_state:
    st.session_state["live_rate"] = get_live_eur_rate()
if "custom_rate" not in st.session_state:
    st.session_state["custom_rate"] = st.session_state["live_rate"]

active_rate = st.session_state["live_rate"] if st.session_state["exchange_mode"] == "Canlı" else st.session_state["custom_rate"]

# --- SOL MENÜ (SIDEBAR) BÖLÜMÜ ---
st.sidebar.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
if os.path.exists("asansor_logo.png"):
    import base64
    with open("asansor_logo.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.sidebar.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{encoded_string}" class="logo-img" style="max-width:140px;" />
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("<h2 style='color:#F59E0B; margin:0;'>AS43 GRUP</h2>", unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown(f"<div class='sidebar-title'>AS43 YÖNETİM PORTALI</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.85rem;'>👤 Hoş Geldiniz, <b>{st.session_state['username']}</b></div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

secilen_modul = st.sidebar.radio(
    "Görüntülenecek Modül:",
    [
        "✍️ Akıllı Teklif Sihirbazı",
        "📋 Geçmiş Teklifler & Takip",
        "⚙️ Sistem Ayarları & Sac Fiyatları",
        "📦 Stok Yönetimi",
        "📊 Finans & Muhasebe Raporu"
    ]
)

st.sidebar.markdown("---")

# Döviz Kuru
st.sidebar.markdown("#### 💶 EUR/TRY Döviz Kuru")
st.sidebar.markdown(
    f"<div style='background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 10px; text-align: center;'><span style='font-size: 0.8rem; color:#94a3b8; font-weight:600;'>AKTİF EUR/TRY KURU</span><br>"
    f"<span style='font-size: 1.4rem; font-weight: 800; color: #22c55e;'>{active_rate:.4f} TL</span><br>"
    f"<span style='font-size: 0.75rem; color:#f59e0b;'>Mod: {st.session_state['exchange_mode']}</span>"
    f"</div>", 
    unsafe_allow_html=True
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔓 Güvenli Çıkış Yap", key="btn_logout"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.rerun()

st.sidebar.markdown("<div style='text-align: center; color: #64748b; font-size: 0.75rem; margin-top:30px;'>AS43 Asansör & Metal ERP v2.0</div>", unsafe_allow_html=True)

# ========================================================
# 1. MODÜL: AKILLI TEKLİF SİHİRBAZI
# ========================================================
if secilen_modul == "✍️ Akıllı Teklif Sihirbazı":
    st.markdown("<div class='main-title'>Akıllı Maliyet & Teklif Sihirbazı</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>Sac Kesim, Büküm, İşçilik ve Operasyon Hesaplama Modülü</div>", unsafe_allow_html=True)
    
    col_w1, col_w2 = st.columns([1, 1.1])
    
    with col_w1:
        st.subheader("📋 Teklif Parametreleri")
        
        musteri_adi = st.text_input("Müşteri / Firma Adı:", value="Özsoy Asansör A.Ş.")
        
        sablon = st.selectbox(
            "Kabin / Karkas Şablonu Seçin:",
            [
                "Standart Kabin (Paslanmaz)",
                "Lüks Paslanmaz Kabin (Desenli/Aynalı)",
                "Panoramik Kabin",
                "Yük & Sedye Kabini",
                "Ağırlık Karkası",
                "Süspansiyon Karkası",
                "Özel Tasarım Metal İmalat"
            ]
        )
        
        st.markdown("##### 🛠️ Hammadde Bilgileri")
        sac_tipleri = df_sac_fiyatlari["Malzeme_Tipi"].tolist()
        secilen_sac = st.selectbox("Sac Malzeme Tipi:", sac_tipleri)
        
        sac_fiyat_row = df_sac_fiyatlari[df_sac_fiyatlari["Malzeme_Tipi"] == secilen_sac]
        birim_fiyat_eur_kg = float(sac_fiyat_row["Birim_Fiyat_EUR_kg"].iloc[0])
        
        st.caption(f"ℹ️ Veritabanı Birim Fiyatı: **{birim_fiyat_eur_kg:.2f} EUR/kg**")
        
        col_inp1, col_inp2, col_inp3 = st.columns(3)
        with col_inp1:
            sac_kalinligi = st.selectbox("Sac Kalınlığı (mm):", [1.0, 1.2, 1.5, 2.0, 3.0, 4.0, 5.0], index=2)
        with col_inp2:
            net_agirlik = st.number_input("Net Ağırlık (kg):", min_value=0.1, value=120.0, step=1.0)
        with col_inp3:
            fire_orani = st.number_input("Fire Oranı (%):", min_value=0.0, max_value=100.0, value=15.0, step=1.0)
            
        st.markdown("##### ⚡ Operasyon Süreleri (Dakika)")
        col_time1, col_time2, col_time3 = st.columns(3)
        with col_time1:
            lazer_suresi = st.number_input("Lazer Kesim Süresi (dk):", min_value=0.0, value=45.0, step=5.0)
        with col_time2:
            bukum_suresi = st.number_input("Büküm Süresi (dk):", min_value=0.0, value=30.0, step=5.0)
        with col_time3:
            iscilik_suresi = st.number_input("Montaj/İşçilik Süresi (dk):", min_value=0.0, value=60.0, step=10.0)
            
        # Birim dakika maliyetleri (İstek üzerine dakikaya çevrildi)
        st.markdown("##### 💶 Birim Dakika Maliyetleri (EUR / Dakika)")
        col_cost1, col_cost2, col_cost3 = st.columns(3)
        with col_cost1:
            lazer_dakika_maliyet = st.number_input("Lazer / Dakika (EUR):", min_value=0.00, value=1.33, step=0.05, format="%.4f")
        with col_cost2:
            bukum_dakika_maliyet = st.number_input("Büküm / Dakika (EUR):", min_value=0.00, value=0.66, step=0.05, format="%.4f")
        with col_cost3:
            iscilik_dakika_maliyet = st.number_input("İşçilik / Dakika (EUR):", min_value=0.00, value=0.25, step=0.05, format="%.4f")
            
        st.markdown("##### 📈 Kar, İskonto & KDV")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            sabit_gider_payi = st.slider("Sabit Gider Payı (%):", min_value=0, max_value=50, value=15)
        with col_m2:
            kar_marji = st.slider("Hedef Kar Marjı (%):", min_value=0, max_value=500, value=25)
        with col_m3:
            iskonto_orani = st.slider("İskonto Oranı (%):", min_value=0, max_value=80, value=10)
            
        kdv_orani = st.selectbox("KDV Oranı (%):", [0, 10, 20], index=2)

    with col_w2:
        st.subheader("📊 Maliyet ve Teklif Analizi")
        
        # Hesaplama
        brut_agirlik = net_agirlik * (1 + (fire_orani / 100))
        hammadde_maliyeti_eur = brut_agirlik * birim_fiyat_eur_kg
        
        # Dakika bazlı operasyon maliyetleri
        lazer_maliyeti_eur = lazer_suresi * lazer_dakika_maliyet
        bukum_maliyeti_eur = bukum_suresi * bukum_dakika_maliyet
        iscilik_maliyeti_eur = iscilik_suresi * iscilik_dakika_maliyet
        
        uretim_ara_toplam_eur = hammadde_maliyeti_eur + lazer_maliyeti_eur + bukum_maliyeti_eur + iscilik_maliyeti_eur
        sabit_gider_maliyeti_eur = uretim_ara_toplam_eur * (sabit_gider_payi / 100)
        
        toplam_maliyet_eur = uretim_ara_toplam_eur + sabit_gider_maliyeti_eur
        
        # Kar eklenmiş liste satış fiyatı
        liste_fiyati_eur = toplam_maliyet_eur * (1 + (kar_marji / 100))
        
        # İskonto hesabı
        iskonto_tutari_eur = liste_fiyati_eur * (iskonto_orani / 100)
        iskontolu_fiyat_eur = liste_fiyati_eur - iskonto_tutari_eur
        
        # KDV Hesabı
        kdv_tutari_eur = iskontolu_fiyat_eur * (kdv_orani / 100)
        genel_toplam_eur = iskontolu_fiyat_eur + kdv_tutari_eur
        
        # TL Hesaplamaları
        genel_toplam_try = genel_toplam_eur * active_rate
        
        # Hazırlayan bilgisi
        hazirlayan = st.session_state['username']
        
        # Geçici bir teklif kodu belirle (Kayıt edilene kadar)
        teklif_no_goster = "T-YENI"
        if not df_teklifler.empty:
            try:
                last_id = df_teklifler["Teklif_ID"].iloc[-1]
                num = int(last_id.split("-")[1])
                teklif_no_goster = f"T-{num + 1}"
            except Exception:
                pass
        
        st.markdown(f"""
        <div class='quote-result-card'>
            <h3 style='margin-top:0; color:#F59E0B; text-align:center; font-weight:800;'>💶 TEKLİF HESAP RAPORU (KDV DAHİL)</h3>
            <table style='width:100%; border-collapse: collapse; font-size:0.95rem; color:#f8fafc;'>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#94a3b8;'>Teklif Kodu:</td>
                    <td style='padding: 6px 0; text-align:right; font-weight:bold; color:#F59E0B;'>{teklif_no_goster}</td>
                </tr>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#94a3b8;'>Hazırlayan:</td>
                    <td style='padding: 6px 0; text-align:right; font-weight:bold;'>{hazirlayan}</td>
                </tr>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#94a3b8;'>Müşteri:</td>
                    <td style='padding: 6px 0; text-align:right; font-weight:bold;'>{musteri_adi}</td>
                </tr>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#94a3b8;'>Üretim Net Maliyeti:</td>
                    <td style='padding: 6px 0; text-align:right;'>{toplam_maliyet_eur:.2f} EUR</td>
                </tr>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#94a3b8;'>Liste Fiyatı (Kar Dahil):</td>
                    <td style='padding: 6px 0; text-align:right;'>{liste_fiyati_eur:.2f} EUR</td>
                </tr>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#ef4444;'>Uygulanan İskonto (%{iskonto_orani}):</td>
                    <td style='padding: 6px 0; text-align:right; color:#ef4444;'>- {iskonto_tutari_eur:.2f} EUR</td>
                </tr>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#94a3b8;'>Ara Toplam (KDV Hariç):</td>
                    <td style='padding: 6px 0; text-align:right;'>{iskontolu_fiyat_eur:.2f} EUR</td>
                </tr>
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 6px 0; color:#3b82f6;'>KDV (%{kdv_orani}):</td>
                    <td style='padding: 6px 0; text-align:right; color:#3b82f6;'>{kdv_tutari_eur:.2f} EUR</td>
                </tr>
                <tr style='border-bottom: 2px solid #F59E0B; font-weight:bold; color: #22c55e;'>
                    <td style='padding: 8px 0; font-size:1.1rem;'>GENEL TOPLAM (KDV DAHİL):</td>
                    <td style='padding: 8px 0; text-align:right; font-size:1.1rem;'>{genel_toplam_eur:.2f} EUR / {genel_toplam_try:,.2f} TL</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # WhatsApp Mesaj Metni
        whatsapp_message = (
            f"*AS43 GRUP LAZER & METAL TEKLİF RAPORU* 💠\n"
            f"----------------------------------------------\n"
            f"📄 *Teklif Kodu:* {teklif_no_goster}\n"
            f"👤 *Hazırlayan:* {hazirlayan}\n"
            f"🏢 *Müşteri:* {musteri_adi}\n"
            f"📅 *Tarih:* {datetime.date.today().strftime('%d.%m.%Y')}\n"
            f"🛗 *Şablon:* {sablon}\n"
            f"----------------------------------------------\n"
            f"💰 *Liste Fiyatı:* {liste_fiyati_eur:.2f} EUR\n"
            f"📉 *İskonto (%{iskonto_orani}):* -{iskonto_tutari_eur:.2f} EUR\n"
            f"Ara Toplam: {iskontolu_fiyat_eur:.2f} EUR\n"
            f"⚡ *KDV (%{kdv_orani}):* {kdv_tutari_eur:.2f} EUR\n"
            f"🔥 *GENEL TOPLAM:* {genel_toplam_eur:.2f} EUR (~{genel_toplam_try:,.2f} TL)\n"
            f"----------------------------------------------\n"
            f"⚠️ *Not:* Geçerlilik süresi 3 gündür."
        )
        
        encoded_message = urllib.parse.quote(whatsapp_message)
        whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_message}"
        
        # Aksiyonlar
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            if st.button("💾 Teklifi Kayıt Geçmişine Ekle", key="btn_save_quote"):
                if not df_teklifler.empty:
                    try:
                        last_id = df_teklifler["Teklif_ID"].iloc[-1]
                        num = int(last_id.split("-")[1])
                        new_id = f"T-{num + 1}"
                    except Exception:
                        new_id = f"T-{len(df_teklifler) + 1001}"
                else:
                    new_id = "T-1001"
                
                yeni_teklif = {
                    "Teklif_ID": new_id,
                    "Tarih": datetime.date.today().strftime("%Y-%m-%d"),
                    "Musteri": musteri_adi,
                    "Sablon": sablon,
                    "Malzeme_Tipi": secilen_sac,
                    "Kalinlik_mm": sac_kalinligi,
                    "Net_Agirlik_kg": net_agirlik,
                    "Fire_Orani": fire_orani,
                    "Tutar_EUR": round(genel_toplam_eur, 2),
                    "Tutar_TRY": round(genel_toplam_try, 2),
                    "Durum": "Beklemede",
                    "Hazirlayan": hazirlayan,
                    "Iletim_Durumu": "Gönderilmedi",
                    "Odeme_Durumu": "Ödeme Bekleniyor"
                }
                
                updated_teklifler = pd.concat([df_teklifler, pd.DataFrame([yeni_teklif])], ignore_index=True)
                updated_teklifler.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')
                st.success(f"Teklif **{new_id}** koduyla kaydedildi!")
                st.rerun()
                
        with act_col2:
            st.link_button("💬 WhatsApp ile Gönder", whatsapp_url)
            
        st.markdown("**WhatsApp / Panoya Kopyalama Hazır Metin:**")
        st.text_area("Teklif düz metni:", whatsapp_message, height=150)

        # PDF Oluşturma
        pdf_bytes = bytes(generate_pdf(
            teklif_no_goster, hazirlayan, musteri_adi, sablon, secilen_sac, sac_kalinligi, net_agirlik, fire_orani,
            hammadde_maliyeti_eur, lazer_suresi, lazer_maliyeti_eur, bukum_suresi, bukum_maliyeti_eur,
            iscilik_suresi, iscilik_maliyeti_eur, sabit_gider_payi, sabit_gider_maliyeti_eur,
            toplam_maliyet_eur, liste_fiyati_eur, (liste_fiyati_eur * active_rate), active_rate,
            iskonto_orani, iskonto_tutari_eur, kdv_orani, kdv_tutari_eur, genel_toplam_eur
        ))
        
        st.markdown("---")
        st.markdown("### 📄 PDF İndir & E-posta Bildirimi")
        
        pdf_col1, pdf_col2 = st.columns(2)
        with pdf_col1:
            st.download_button(
                label="📥 PDF Formatında Teklifi İndir",
                data=pdf_bytes,
                file_name=f"Teklif_{teklif_no_goster}_{musteri_adi.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            
        with pdf_col2:
            smtp_config = {}
            if os.path.exists(FILE_SMTP_AYARLARI):
                try:
                    with open(FILE_SMTP_AYARLARI, "r", encoding="utf-8") as f:
                        smtp_config = json.load(f)
                except Exception:
                    pass
            
            with st.expander("✉️ PDF Teklifi E-posta ile Gönder"):
                email_alici = st.text_input("Alıcı E-posta Adresi:", placeholder="musteri@firma.com")
                smtp_server = st.text_input("SMTP Sunucusu:", value=smtp_config.get("smtp_server", "smtp.gmail.com"))
                smtp_port = st.number_input("SMTP Port:", value=smtp_config.get("smtp_port", 587), step=1)
                smtp_gonderen = st.text_input("Gönderen E-posta:", value=smtp_config.get("sender_email", ""))
                smtp_sifre = st.text_input("SMTP Uygulama Şifresi:", value=smtp_config.get("sender_password", ""), type="password")
                
                if st.button("✉️ Teklifi Gönder"):
                    if not email_alici:
                        st.error("Alıcı adresi girin!")
                    elif not smtp_server or not smtp_gonderen or not smtp_sifre:
                        st.error("Bağlantı ayarlarını doldurun!")
                    else:
                        with st.spinner("E-posta gönderiliyor..."):
                            yeni_config = {
                                "smtp_server": smtp_server,
                                "smtp_port": int(smtp_port),
                                "sender_email": smtp_gonderen,
                                "sender_password": smtp_sifre
                            }
                            try:
                                Guide = open(FILE_SMTP_AYARLARI, "w", encoding="utf-8")
                                json.dump(yeni_config, Guide, ensure_ascii=False, indent=4)
                                Guide.close()
                            except Exception:
                                pass
                                
                            konu = f"AS43 GRUP - Lazer & Metal Teklif Formu ({teklif_no_goster})"
                            govde = (
                                f"Sayın Yetkili,\n\n"
                                f"Firmamız tarafından hazırlanan {teklif_no_goster} nolu teklif detayı ekte PDF olarak iletilmiştir.\n\n"
                                f"Teklif Özeti:\n"
                                f"- Müşteri: {musteri_adi}\n"
                                f"- Tutar: {genel_toplam_eur:.2f} EUR / {genel_toplam_try:,.2f} TL\n"
                                f"- Hazırlayan: {hazirlayan}\n\n"
                                f"İyi çalışmalar dileriz,\n"
                                f"AS43 GRUP Lazer & Metal ERP"
                            )
                            dosya_adi = f"Teklif_{teklif_no_goster}_{musteri_adi.replace(' ', '_')}.pdf"
                            
                            success, msg = send_email_with_pdf(
                                email_alici, konu, govde, pdf_bytes, dosya_adi,
                                smtp_server, int(smtp_port), smtp_gonderen, smtp_sifre
                            )
                            if success:
                                st.success(msg)
                                if not df_teklifler.empty and teklif_no_goster in df_teklifler["Teklif_ID"].values:
                                    idx = df_teklifler[df_teklifler["Teklif_ID"] == teklif_no_goster].index[0]
                                    df_teklifler.at[idx, "Iletim_Durumu"] = "E-posta ile İletildi"
                                    df_teklifler.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')
                            else:
                                st.error(msg)

# ========================================================
# 2. MODÜL: GEÇMİŞ TEKLİFLER VE DURUM TAKİBİ
# ========================================================
elif secilen_modul == "📋 Geçmiş Teklifler & Takip":
    st.markdown("<div class='main-title'>Geçmiş Teklifler ve Veritabanı Takibi</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>Teklif Durumları (Onay, Bekleme, Red) ve Ödeme Takibi Kontrolü</div>", unsafe_allow_html=True)
    
    if df_teklifler.empty:
        st.info("Henüz teklif kaydı bulunmuyor.")
    else:
        st.subheader("🔍 Teklif Sorgulama ve Filtreleme")
        filtre_col1, filtre_col2, filtre_col3 = st.columns(3)
        with filtre_col1:
            teklif_arama = st.text_input("Müşteri ismine göre ara:", "")
        with filtre_col2:
            teklif_durum = st.selectbox("Teklif Durumuna Göre:", ["Tümü", "Onaylandı", "Beklemede", "Reddedildi"])
        with filtre_col3:
            filtre_odeme = st.selectbox("Ödeme Durumuna Göre:", ["Tümü", "Ödeme Bekleniyor", "Ödeme Alındı", "Vadesi Geçti"])
            
        df_filt_teklif = df_teklifler.copy()
        
        if teklif_arama:
            df_filt_teklif = df_filt_teklif[df_filt_teklif["Musteri"].str.contains(teklif_arama, case=False, na=False)]
        if teklif_durum != "Tümü":
            df_filt_teklif = df_filt_teklif[df_filt_teklif["Durum"] == teklif_durum]
        if filtre_odeme != "Tümü":
            df_filt_teklif = df_filt_teklif[df_filt_teklif["Odeme_Durumu"] == filtre_odeme]
            
        st.markdown(f"Bulunan Teklif Sayısı: **{len(df_filt_teklif)}**")
        
        styled_rows = []
        for idx, row in df_filt_teklif.iterrows():
            if row['Durum'] == "Onaylandı":
                durum_html = "<span class='badge badge-onay'>Onaylandı</span>"
            elif row['Durum'] == "Reddedildi":
                durum_html = "<span class='badge badge-red'>Reddedildi</span>"
            else:
                durum_html = "<span class='badge badge-bekle'>Beklemede</span>"
                
            if row['Odeme_Durumu'] == "Ödeme Alındı":
                odeme_html = "<span class='badge badge-odeme-alindi'>Ödeme Alındı</span>"
            elif row['Odeme_Durumu'] == "Vadesi Geçti":
                odeme_html = "<span class='badge badge-odeme-gecikti'>Vadesi Geçti</span>"
            else:
                odeme_html = "<span class='badge badge-odeme-bekliyor'>Ödeme Bekleniyor</span>"
                
            iletim_html = f"<span style='color: {'#22c55e' if row['Iletim_Durumu'] == 'E-posta ile İletildi' else '#94a3b8'};'>{row['Iletim_Durumu']}</span>"
            
            styled_rows.append({
                "Teklif Kodu": row['Teklif_ID'],
                "Tarih": row['Tarih'],
                "Müşteri": row['Musteri'],
                "Şablon": row['Sablon'],
                "Tutar (EUR)": f"€{row['Tutar_EUR']:.2f}",
                "Hazırlayan": row['Hazirlayan'],
                "E-posta İletim": iletim_html,
                "Durum": durum_html,
                "Ödeme Durumu": odeme_html
            })
            
        df_show = pd.DataFrame(styled_rows)
        if not df_show.empty:
            st.write(df_show.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Filtrelere uygun veri bulunamadı.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.subheader("🔄 Teklif Durumunu & Ödeme Durumunu Güncelle")
        up_col1, up_col2, up_col3, up_col4 = st.columns([1.5, 1.5, 1.5, 1])
        
        with up_col1:
            teklif_ids = df_teklifler["Teklif_ID"].unique().tolist()
            secilen_teklif_id = st.selectbox("Teklif Kodu:", teklif_ids)
            
        with up_col2:
            mevcut_teklif_row = df_teklifler[df_teklifler["Teklif_ID"] == secilen_teklif_id]
            varsayilan_durum_index = 1
            if not mevcut_teklif_row.empty:
                m_dur = mevcut_teklif_row["Durum"].values[0]
                if m_dur == "Onaylandı": varsayilan_durum_index = 0
                elif m_dur == "Reddedildi": varsayilan_durum_index = 2
            yeni_durum_secim = st.selectbox("Teklif Durumu:", ["Onaylandı", "Beklemede", "Reddedildi"], index=varsayilan_durum_index)
            
        with up_col3:
            varsayilan_odeme_index = 0
            if not mevcut_teklif_row.empty:
                m_odeme = mevcut_teklif_row["Odeme_Durumu"].values[0] if "Odeme_Durumu" in mevcut_teklif_row.columns else "Ödeme Bekleniyor"
                if m_odeme == "Ödeme Alındı": varsayilan_odeme_index = 1
                elif m_odeme == "Vadesi Geçti": varsayilan_odeme_index = 2
            yeni_odeme_secim = st.selectbox("Ödeme Durumu:", ["Ödeme Bekleniyor", "Ödeme Alındı", "Vadesi Geçti"], index=varsayilan_odeme_index)
            
        with up_col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("💾 Durumları Kaydet", key="btn_update_status"):
                idx = df_teklifler[df_teklifler["Teklif_ID"] == secilen_teklif_id].index[0]
                df_teklifler.at[idx, "Durum"] = yeni_durum_secim
                df_teklifler.at[idx, "Odeme_Durumu"] = yeni_odeme_secim
                df_teklifler.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')
                st.success(f"{secilen_teklif_id} nolu teklif başarıyla güncellendi!")
                st.rerun()

        st.markdown("---")
        st.subheader("⚠️ Kayıt Sil")
        sil_col1, sil_col2 = st.columns([3, 1])
        with sil_col1:
            silinecek_id = st.selectbox("Sistemden kalıcı olarak silmek istediğiniz teklifi seçin:", ["Seçiniz..."] + teklif_ids)
        with sil_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("❌ Teklifi Kalıcı Olarak Sil"):
                if silinecek_id == "Seçiniz...":
                    st.error("Geçerli bir teklif seçin.")
                else:
                    df_teklifler = df_teklifler[df_teklifler["Teklif_ID"] != silinecek_id]
                    df_teklifler.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')
                    st.warning(f"{silinecek_id} nolu teklif silindi!")
                    st.rerun()

# ========================================================
# 3. MODÜL: SİSTEM AYARLARI VE CANLI DÖVİZ KONTROLÜ
# ========================================================
elif secilen_modul == "⚙️ Sistem Ayarları & Sac Fiyatları":
    st.markdown("<div class='main-title'>Sistem Ayarları & Sac Fiyat Veritabanı</div>", unsafe_allow_html=True)
    
    set_tab1, set_tab2 = st.tabs(["💶 EUR/TRY Döviz Ayarları", "📂 Sac Fiyat Listesi Düzenleyici"])
    
    with set_tab1:
        st.subheader("Döviz Ayarları")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            yeni_mode = st.radio(
                "Kur Modu Seçin:", 
                ["Canlı (İnternet Üzerinden Çek)", "Sabit / Manuel (Kullanıcı Tarafından Belirlenen)"],
                index=0 if st.session_state["exchange_mode"] == "Canlı" else 1
            )
        with col_d2:
            manuel_input = st.number_input(
                "Sabit EUR/TRY Kuru Girişi:",
                min_value=1.0,
                value=st.session_state["custom_rate"],
                step=0.01,
                format="%.4f"
            )
            
        if st.button("Döviz Ayarlarını Güncelle & Kaydet"):
            st.session_state["exchange_mode"] = "Canlı" if "Canlı" in yeni_mode else "Sabit"
            st.session_state["custom_rate"] = manuel_input
            if st.session_state["exchange_mode"] == "Canlı":
                st.session_state["live_rate"] = get_live_eur_rate()
            st.success("Döviz kuru ayarları güncellendi!")
            st.rerun()
            
    with set_tab2:
        st.subheader("Sac Hammadde kg/EUR Fiyat Listesi")
        edited_df = st.data_editor(
            df_sac_fiyatlari, 
            use_container_width=True,
            num_rows="fixed",
            key="sac_editor"
        )
        if st.button("Fiyat Değişikliklerini Kaydet"):
            try:
                edited_df["Birim_Fiyat_EUR_kg"] = edited_df["Birim_Fiyat_EUR_kg"].astype(float)
                edited_df.to_csv(FILE_SAC_FIYATLARI, index=False, encoding='utf-8-sig')
                st.success("Fiyatlar kaydedildi!")
                st.rerun()
            except Exception as e:
                st.error(f"Hata: {e}")

# ========================================================
# 4. MODÜL: LAZER SAC STOK YÖNETİMİ
# ========================================================
elif secilen_modul == "📦 Stok Yönetimi":
    st.markdown("<div class='main-title'>Lazer Sac Hammadde Stoğu</div>", unsafe_allow_html=True)
    
    st.subheader("📦 Sac Stok Seviyeleri")
    stock_cols = st.columns(3)
    for idx, row_stok in df_stok.iterrows():
        col_target = stock_cols[idx % 3]
        with col_target:
            max_kapasite = 5000.0
            doluluk = min(float(row_stok['Miktar_kg']) / max_kapasite, 1.0)
            st.markdown(f"""
            <div class='stock-card'>
                <div class='stock-title'>📋 {row_stok['Malzeme_Tipi']}</div>
                <div class='stock-qty'>{row_stok['Miktar_kg']:.1f} kg</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(doluluk)
            st.markdown("<br>", unsafe_allow_html=True)
            
    st.markdown("---", unsafe_allow_html=True)
    st.subheader("🔄 Sac Stok Hareketi Girişi")
    with st.form("stok_hareket_form"):
        secilen_sac = st.selectbox("İşlem Yapılacak Sac Tipi:", df_stok["Malzeme_Tipi"].tolist())
        hareket_tipi = st.selectbox("İşlem Tipi:", ["➕ Stok Ekle (Satın Alma)", "➖ Stok Tüket (Kesim/İmalat)"])
        miktar = st.number_input("Miktar (kg):", min_value=1.0, value=50.0, step=1.0)
        
        if st.form_submit_button("Stok Hareketini Kaydet"):
            idx = df_stok[df_stok["Malzeme_Tipi"] == secilen_sac].index[0]
            mevcut_miktar = float(df_stok.at[idx, "Miktar_kg"])
            if "Stok Ekle" in hareket_tipi:
                yeni_miktar = mevcut_miktar + miktar
            else:
                yeni_miktar = max(0.0, mevcut_miktar - miktar)
            df_stok.at[idx, "Miktar_kg"] = yeni_miktar
            df_stok.to_csv(FILE_STOK, index=False, encoding='utf-8-sig')
            st.success("Stok güncellendi!")
            st.rerun()

# ========================================================
# 5. MODÜL: FİNANS VE GELİR-GİDER ANALİZİ
# ========================================================
elif secilen_modul == "📊 Finans & Muhasebe Raporu":
    st.markdown("<div class='main-title'>Fabrika Gelir - Gider & Finans Raporu</div>", unsafe_allow_html=True)
    
    erp_tab1, erp_tab2 = st.tabs(["📊 Finansal Raporlar", "💸 Yeni Gelir / Gider Girişi Yap"])
    
    with erp_tab1:
        st.subheader("Dönemsel Finansal Raporlama")
        filtre_col1, filtre_col2 = st.columns(2)
        with filtre_col1:
            yil_listesi = sorted(list(set(df_gelir["Tarih"].dt.year.tolist() + df_gider["Tarih"].dt.year.tolist())), reverse=True)
            secilen_yil = st.selectbox("Rapor Yılı:", yil_listesi) if yil_listesi else st.selectbox("Rapor Yılı:", [datetime.date.today().year])
        with filtre_col2:
            ay_listesi = ["Tümü", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            secilen_ay_ad = st.selectbox("Rapor Ayı:", ay_listesi)
            
        ay_numarasi = ay_listesi.index(secilen_ay_ad)
        
        gelir_filtre = df_gelir[df_gelir["Tarih"].dt.year == secilen_yil] if not df_gelir.empty else df_gelir
        gider_filtre = df_gider[df_gider["Tarih"].dt.year == secilen_yil] if not df_gider.empty else df_gider
        
        if secilen_ay_ad != "Tümü" and not df_gelir.empty:
            gelir_filtre = gelir_filtre[gelir_filtre["Tarih"].dt.month == ay_numarasi]
        if secilen_ay_ad != "Tümü" and not df_gider.empty:
            gider_filtre = gider_filtre[gider_filtre["Tarih"].dt.month == ay_numarasi]
            
        toplam_gelir = gelir_filtre["Tutar_TL"].sum() if not df_gelir.empty else 0.0
        toplam_gider = gider_filtre["Tutar_TL"].sum() if not df_gider.empty else 0.0
        net_kar = toplam_gelir - toplam_gider
        
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Toplam Gelir</div><div class='metric-val' style='color:#22c55e;'>{toplam_gelir:,.2f} TL</div></div>", unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Toplam Gider</div><div class='metric-val' style='color:#ef4444;'>{toplam_gider:,.2f} TL</div></div>", unsafe_allow_html=True)
        with kpi_col3:
            color = "#22c55e" if net_kar >= 0 else "#ef4444"
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Net Kar/Zarar</div><div class='metric-val' style='color:{color};'>{net_kar:,.2f} TL</div></div>", unsafe_allow_html=True)
            
    with erp_tab2:
        st.subheader("Giriş Kayıt Paneli")
        insert_col1, insert_col2 = st.columns(2)
        with insert_col1:
            st.markdown("### Gider Girişi")
            with st.form("yeni_gider_form"):
                gider_tarih = st.date_input("İşlem Tarihi:", datetime.date.today(), key="g_tarih")
                gider_kategori = st.selectbox("Gider Kategorisi:", ["Personel Gideri", "Enerji Gideri", "Gaz Gideri", "Nakliye & Lojistik", "Diğer"])
                gider_alt_kategori = st.selectbox("Alt Gider Kalemi:", ["Maaş", "Avans", "Elektrik", "Azot (N₂)", "Oksijen (O₂)", "Nakliye", "Diğer"])
                gider_tutar = st.number_input("Tutar (TL):", min_value=1.0, value=1500.0)
                gider_aciklama = st.text_input("Açıklama:")
                if st.form_submit_button("Gideri Kaydet"):
                    yeni_gider = {
                        "Tarih": str(gider_tarih),
                        "Kategori": gider_kategori,
                        "Alt_Kategori": gider_alt_kategori,
                        "Tutar_TL": float(gider_tutar),
                        "Açıklama": gider_aciklama
                    }
                    updated_gider = pd.concat([df_gider, pd.DataFrame([yeni_gider])], ignore_index=True)
                    updated_gider.to_csv(FILE_GIDERLER, index=False, encoding='utf-8-sig')
                    st.success("Kaydedildi!")
                    st.rerun()
                    
        with insert_col2:
            st.markdown("### Tahsilat (Gelir) Girişi")
            with st.form("yeni_gelir_form"):
                gelir_tarih = st.date_input("Tahsilat Tarihi:", datetime.date.today(), key="gel_tarih")
                gelir_musteri = st.text_input("Müşteri / Firma Adı:")
                gelir_yontem = st.selectbox("Ödeme Yöntemi:", ["Nakit", "Kredi Kartı", "Çek"])
                cek_vadesi = st.date_input("Çek Vade Tarihi:", datetime.date.today() + datetime.timedelta(days=30))
                gelir_tutar = st.number_input("Tutar (TL):", min_value=1.0, value=10000.0)
                gelir_aciklama = st.text_input("Ödeme Açıklaması:")
                if st.form_submit_button("Ödemeyi Kaydet"):
                    if not gelir_musteri:
                        st.error("Müşteri adı girilmeli!")
                    else:
                        vade_str = str(cek_vadesi) if gelir_yontem == "Çek" else ""
                        yeni_gelir = {
                            "Tarih": str(gelir_tarih),
                            "Müşteri": gelir_musteri,
                            "Ödeme_Yöntemi": gelir_yontem,
                            "Tutar_TL": float(gelir_tutar),
                            "Çek_Vadesi": vade_str,
                            "Açıklama": gelir_aciklama
                        }
                        updated_gelir = pd.concat([df_gelir, pd.DataFrame([yeni_gelir])], ignore_index=True)
                        updated_gelir.to_csv(FILE_GELIRLER, index=False, encoding='utf-8-sig')
                        st.success("Ödeme kaydedildi!")
                        st.rerun()
