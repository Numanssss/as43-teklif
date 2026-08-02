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

import os
import base64
import streamlit as st
import pandas as pd
import datetime
import urllib.request
import urllib.parse
import json
import hashlib
from PIL import Image
import io

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="AS43 Grup | Metal & Asansör ERP", layout="wide", page_icon="💠")

# --- LOGO ARKA PLANINI ŞEFFAFLAŞTIRAN YARDIMCI FONKSİYON ---
def get_transparent_logo_base64():
    if not os.path.exists("logo.png"):
        return None
    try:
        img = Image.open("logo.png").convert("RGBA")
        datas = img.getdata()
        new_data = []
        # Beyaz ve yakın tonlarını şeffafa çevir
        for item in datas:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception:
        try:
            with open("logo.png", "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return None

# --- KURUMSAL BRANDING & PREMIUM CSS ---
st.markdown("""
    <style>
    /* Global sayfa arka planı ve Tek-Kanal Doğal Kaydırma */
    html, body {
        background-color: #0f172a;
        color: #f8fafc;
        margin: 0 !important;
        padding: 0 !important;
        height: auto !important;
        min-height: 100% !important;
        overflow-y: auto !important; /* Tüm kaydırma bu ana kanaldan yapılır */
        overflow-x: hidden !important;
        overscroll-behavior-y: contain !important; /* Pull-to-refresh yenilemeyi engeller */
        scroll-behavior: smooth !important; /* Pürüzsüz ve akıcı kaydırma */
    }
    
    /* İç Konteynerlerin Kilitlerini Kırma (Nested Scroll İptali) & GPU Hızlandırma */
    #root, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stApp"], 
    .main, 
    [data-testid="stAppViewBlockContainer"] {
        height: auto !important;
        min-height: 100% !important;
        overflow: visible !important; /* İç kaydırma çubuklarını iptal edip body'ye aktarır */
        overscroll-behavior-y: contain !important;
        /* GPU Donanım Hızlandırması (Arayüz Takılmalarını Engeller) */
        transform: translateZ(0);
        -webkit-transform: translateZ(0);
        will-change: transform;
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
    
    /* Şeffaf Logo Stili */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        margin-bottom: 5px;
        background: transparent !important;
    }
    .logo-img {
        max-width: 200px;
        background: transparent !important;
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
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, f"Teklif No: {clean(teklif_no)}", ln=True, align='R')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, f"Hazirlayan: {clean(hazirlayan)}", ln=True, align='R')
    pdf.cell(0, 5, f"Tarih: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True, align='R')
    pdf.ln(3)
    
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
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(217, 119, 6)
    pdf.cell(0, 8, "MALIYET VE OPERASYON DETAYLARI", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    
    pdf.set_fill_color(217, 119, 6)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(85, 7, "   Maliyet Kalemi / Operasyon", 1, 0, 'L', fill=True)
    pdf.cell(50, 7, "Detay", 1, 0, 'C', fill=True)
    pdf.cell(55, 7, "Tutar (EUR)  ", 1, 1, 'R', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 9)
    
    pdf.cell(85, 6, "   Hammadde Maliyeti", 1, 0, 'L')
    pdf.cell(50, 6, f"{net_agirlik:.1f} kg", 1, 0, 'C')
    pdf.cell(55, 6, f"{hammadde_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, "   Lazer Kesim Maliyeti (Birim Dk)", 1, 0, 'L')
    pdf.cell(50, 6, f"{lazer_suresi:.1f} dk", 1, 0, 'C')
    pdf.cell(55, 6, f"{lazer_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, "   Bukum Maliyeti (Birim Dk)", 1, 0, 'L')
    pdf.cell(50, 6, f"{bukum_suresi:.1f} dk", 1, 0, 'C')
    pdf.cell(55, 6, f"{bukum_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, "   Iscilik & Montaj Maliyeti (Birim Dk)", 1, 0, 'L')
    pdf.cell(50, 6, f"{iscilik_suresi:.1f} dk", 1, 0, 'C')
    pdf.cell(55, 6, f"{iscilik_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.cell(85, 6, f"   Enerji & Sabit Giderler Payi (%{sabit_gider_payi})", 1, 0, 'L')
    pdf.cell(50, 6, "", 1, 0, 'C')
    pdf.cell(55, 6, f"{sabit_gider_maliyeti_eur:.2f} EUR  ", 1, 1, 'R')
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(135, 7, "Toplam Net Maliyet:  ", 1, 0, 'R')
    pdf.cell(55, 7, f"{toplam_maliyet_eur:.2f} EUR  ", 1, 1, 'R')
    
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
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(217, 119, 6)
    pdf.cell(0, 6, "KASE VE IMZA ONAY ALANI", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 9)
    y_start = pdf.get_y()
    
    pdf.set_xy(15, y_start)
    pdf.cell(80, 5, "AS43 GRUP LAZER & METAL", ln=True, align='C')
    pdf.set_x(15)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(80, 4, "(Firma Kase & Yetkili Imza)", ln=True, align='C')
    pdf.ln(12)
    pdf.set_x(15)
    pdf.cell(80, 4, "____________________________", ln=True, align='C')
    
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

DEFAULT_HEADERS_ASANSOR = ["Asansör_ID", "Konum", "Durum (Etiket)", "Son_Bakım_Notları", "Bekleyen_Eksikler", "Adres"]

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

# Eksik sütun düzeltmeleri
if "Iletim_Durumu" not in df_teklifler.columns:
    df_teklifler["Iletim_Durumu"] = "Gönderilmedi"
if "Odeme_Durumu" not in df_teklifler.columns:
    df_teklifler["Odeme_Durumu"] = "Ödeme Bekleniyor"
if "Hazirlayan" not in df_teklifler.columns:
    df_teklifler["Hazirlayan"] = "Bilinmiyor"
if "Durum" not in df_teklifler.columns:
    df_teklifler["Durum"] = "Bekliyor"

# --- 📱 MOBİL QR TARAMA SİMÜLATÖRÜ ---
if "id" in st.query_params:
    scan_id = st.query_params["id"]
    
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    logo_b64_scan = get_transparent_logo_base64()
    if logo_b64_scan:
        st.markdown(f"<img src='data:image/png;base64,{logo_b64_scan}' class='logo-img'>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color:#F59E0B;'>AS43 ASANSÖR</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='main-title'>📱 Mobil QR Tarama Servisi</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='main-subtitle'>{scan_id} Asansör Raporu</div>", unsafe_allow_html=True)
    
    col_id = "Asansör_ID"
    satir = df_asansor[df_asansor[col_id].astype(str) == str(scan_id)]
    if not satir.empty:
        d = satir.iloc[0]
        val_durum = str(d["Durum (Etiket)"]).strip()
        color = "#22c55e" if val_durum.lower() == "mavi" else "#ef4444"
        
        st.markdown(f"""
        <div style='background: #1e293b; border-left: 8px solid {color}; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3); color: #f8fafc;'>
            <h3 style='margin-top:0; color:#F59E0B;'>🛠️ Sistem Kaydı: {scan_id}</h3>
            <p style='margin: 8px 0;'><b>📍 Konum:</b> {d['Konum']}</p>
            <p style='margin: 8px 0;'><b>⚡ Mevcut Etiket Durumu:</b> <span style='background: {color}; color: white; padding: 3px 10px; border-radius: 6px; font-weight: bold;'>{val_durum} Etiket</span></p>
            <p style='margin: 8px 0;'><b>📝 Son Bakım Notu:</b> {d['Son_Bakım_Notları']}</p>
            <p style='margin: 8px 0;'><b>❌ Bekleyen Eksik:</b> {d['Bekleyen_Eksikler']}</p>
            <p style='margin: 8px 0;'><b>🏠 Bina Adresi:</b> {d['Adres']}</p>
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

# Eğer URL'de önceden kaydedilmiş aktif bir oturum parametresi varsa, session_state'e yükle (Yenileme koruması)
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"] and "user" in st.query_params:
    saved_user = st.query_params["user"].lower()
    if saved_user in USER_PASSWORDS:
        st.session_state["authenticated"] = True
        if saved_user in ["unal", "ünal"]:
            st.session_state["username"] = "Ünal"
        elif saved_user in ["ayca", "ayça"]:
            st.session_state["username"] = "Ayça"
        else:
            st.session_state["username"] = saved_user.capitalize()

if not st.session_state["authenticated"]:
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
            # GİRİŞ EKRANI LOGO
            logo_b64_login = get_transparent_logo_base64()
            if logo_b64_login:
                st.markdown(f"""
                    <div class="logo-container">
                        <img src="data:image/png;base64,{logo_b64_login}" class="logo-img" />
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
                    st.query_params["user"] = username_input
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

# SOL MENÜ ŞEFFAF LOGO
logo_b64_sb = get_transparent_logo_base64()
if logo_b64_sb:
    st.sidebar.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_b64_sb}" class="logo-img" style="max-width:160px;" />
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("<h2 style='color:#F59E0B; margin:0;'>AS43 GRUP</h2>", unsafe_allow_html=True)

st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-top:5px;'>👤 Hoş Geldiniz, <b>{st.session_state['username']}</b></div>", unsafe_allow_html=True)
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

st.sidebar.markdown("#### ⚙️ EUR/TRY Döviz Kuru")
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
    st.query_params.clear()
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
            
        st.markdown("##### 💶 Birim Dakika Maliyetleri (EUR / Dakika)")
        col_cost1, col_cost2, col_cost3 = st.columns(3)
        with col_cost1:
            lazer_dakika_maliyet = st.number_input("Lazer / Dakika (EUR):", min_value=0.00, value=1.33, step=0.05, format="%.4f")
        with col_cost2:
            bukum_dakika_maliyet = st.number_input("Büküm / Dakika (EUR):", min_value=0.00, value=0.66, step=0.05, format="%.4f")
        with col_cost3:
            iscilik_dakika_maliyet = st.number_input("İşçilik / Dakika (EUR):", min_value=0.00, value=0.25, step=0.05, format="%.4f")
            
        # İstek üzerine: Kayma çubuğu (slider) yerine sayı girilebilen number_input alanları yapıldı
        st.markdown("##### 📈 Kar, İskonto & KDV")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            sabit_gider_payi = st.number_input("Sabit Gider Payı (%):", min_value=0, max_value=100, value=15, step=1)
        with col_m2:
            kar_marji = st.number_input("Hedef Kar Marjı (%):", min_value=0, max_value=1000, value=25, step=1)
        with col_m3:
            iskonto_orani = st.number_input("İskonto Oranı (%):", min_value=0, max_value=100, value=10, step=1)
            
        kdv_orani = st.selectbox("KDV Oranı (%):", [0, 10, 20], index=2)

    with col_w2:
        st.subheader("📊 Maliyet ve Teklif Analizi")
        
        brut_agirlik = net_agirlik * (1 + (fire_orani / 100))
        hammadde_maliyeti_eur = brut_agirlik * birim_fiyat_eur_kg
        
        lazer_maliyeti_eur = lazer_suresi * lazer_dakika_maliyet
        bukum_maliyeti_eur = bukum_suresi * bukum_dakika_maliyet
        iscilik_maliyeti_eur = iscilik_suresi * iscilik_dakika_maliyet
        
        uretim_ara_toplam_eur = hammadde_maliyeti_eur + lazer_maliyeti_eur + bukum_maliyeti_eur + iscilik_maliyeti_eur
        sabit_gider_maliyeti_eur = uretim_ara_toplam_eur * (sabit_gider_payi / 100)
        
        toplam_maliyet_eur = uretim_ara_toplam_eur + sabit_gider_maliyeti_eur
        
        liste_fiyati_eur = toplam_maliyet_eur * (1 + (kar_marji / 100))
        
        iskonto_tutari_eur = liste_fiyati_eur * (iskonto_orani / 100)
        iskontolu_fiyat_eur = liste_fiyati_eur - iskonto_tutari_eur
        
        kdv_tutari_eur = iskontolu_fiyat_eur * (kdv_orani / 100)
        genel_toplam_eur = iskontolu_fiyat_eur + kdv_tutari_eur
        
        genel_toplam_try = genel_toplam_eur * active_rate
        
        st.markdown(f"""
        <div class='quote-result-card'>
            <h3 style='margin-top:0; color:#F59E0B;'>💰 Fiyatlandırma Özeti</h3>
            <hr style='border-color: #334155;'>
            <p><b>Hammadde Maliyeti:</b> {hammadde_maliyeti_eur:.2f} EUR ({brut_agirlik:.1f} kg)</p>
            <p><b>Operasyonlar (Lazer+Büküm+İşçilik):</b> {(lazer_maliyeti_eur + bukum_maliyeti_eur + iscilik_maliyeti_eur):.2f} EUR</p>
            <p><b>Toplam Net Maliyet:</b> {toplam_maliyet_eur:.2f} EUR</p>
            <p><b>Liste Satış Fiyati (Kâr Dahil):</b> {liste_fiyati_eur:.2f} EUR</p>
            <p><b>İskonto Tutarı (%{iskonto_orani}):</b> -{iskonto_tutari_eur:.2f} EUR</p>
            <h2 style='color:#22c55e; margin-bottom:5px;'>GENEL TOPLAM: {genel_toplam_eur:.2f} EUR</h2>
            <p style='color:#94a3b8; font-size:0.9rem;'>TL Karşılığı (Kur: {active_rate:.2f}): <b>{genel_toplam_try:,.2f} TL</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # NameError Hatasını Düzeltmek İçin Kayıt ve PDF Oluşturma İşlemleri Düzgünce Kapsüllendi
        if st.button("💾 Teklifi Kaydet ve PDF Oluştur"):
            teklif_no = f"AS43-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            yeni_teklif = {
                "Teklif_ID": teklif_no,
                "Tarih": datetime.date.today().strftime('%Y-%m-%d'),
                "Musteri": musteri_adi,
                "Sablon": sablon,
                "Malzeme_Tipi": secilen_sac,
                "Kalinlik_mm": sac_kalinligi,
                "Net_Agirlik_kg": net_agirlik,
                "Fire_Orani": fire_orani,
                "Tutar_EUR": round(genel_toplam_eur, 2),
                "Tutar_TRY": round(genel_toplam_try, 2),
                "Durum": "Bekliyor",
                "Hazirlayan": st.session_state.get("username", "Bilinmiyor"),
                "Iletim_Durumu": "Gönderilmedi",
                "Odeme_Durumu": "Ödeme Bekleniyor"
            }
            
            df_yeni = pd.DataFrame([yeni_teklif])
            df_teklifler_updated = pd.concat([df_teklifler, df_yeni], ignore_index=True)
            df_teklifler_updated.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')
            
            pdf_bytes = generate_pdf(
                teklif_no, st.session_state["username"], musteri_adi, sablon, secilen_sac, sac_kalinligi,
                net_agirlik, fire_orani, hammadde_maliyeti_eur, lazer_suresi, lazer_maliyeti_eur,
                bukum_suresi, bukum_maliyeti_eur, iscilik_suresi, iscilik_maliyeti_eur, sabit_gider_payi,
                sabit_gider_maliyeti_eur, toplam_maliyet_eur, liste_fiyati_eur, (liste_fiyati_eur * active_rate),
                active_rate, iskonto_orani, iskonto_tutari_eur, kdv_orani, kdv_tutari_eur, genel_toplam_eur
            )
            
            st.success(f"Teklif başarıyla kaydedildi! Teklif No: {teklif_no}")
            
            def clean_name(t):
                if not t: return ""
                t = str(t)
                replacements = {'ı': 'i', 'İ': 'I', 'ş': 's', 'Ş': 'S', 'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'}
                for k, v in replacements.items(): t = t.replace(k, v)
                return t

            st.download_button(
                label="📥 Resmi PDF Teklif Belgesini İndir",
                data=pdf_bytes,
                file_name=f"{teklif_no}_{clean_name(musteri_adi)}.pdf",
                mime="application/pdf",
                key=f"download_pdf_{teklif_no}"
            )

# ========================================================
# 2. MODÜL: GEÇMİŞ TEKLİFLER & TAKİP
# ========================================================
elif secilen_modul == "📋 Geçmiş Teklifler & Takip":
    st.markdown("<div class='main-title'>Geçmiş Teklifler ve Durum Takibi</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>Oluşturulan Tekliflerin Yönetimi, İletimi ve Onay Süreçleri</div>", unsafe_allow_html=True)
    
    if df_teklifler.empty:
        st.info("Henüz kaydedilmiş bir teklif bulunmuyor.")
    else:
        st.dataframe(df_teklifler, use_container_width=True)
        
        st.markdown("#### ⚙️ Teklif İşlemleri & Güncelleme")
        teklif_ids = df_teklifler["Teklif_ID"].astype(str).tolist()
        secilen_teklif_id = st.selectbox("İşlem Yapılacak Teklif No:", teklif_ids)
        
        row_sel = df_teklifler[df_teklifler["Teklif_ID"].astype(str) == str(secilen_teklif_id)].iloc[0]
        
        col_op1, col_op2, col_op3 = st.columns(3)
        with col_op1:
            yeni_durum = st.selectbox("Onay Durumu:", ["Bekliyor", "Onaylandı", "Reddedildi"], index=["Bekliyor", "Onaylandı", "Reddedildi"].index(row_sel["Durum"]) if row_sel["Durum"] in ["Bekliyor", "Onaylandı", "Reddedildi"] else 0)
        with col_op2:
            yeni_iletim = st.selectbox("İletim Durumu:", ["Gönderilmedi", "E-posta ile Gönderildi", "WhatsApp ile Gönderildi"], index=0 if row_sel["Iletim_Durumu"] not in ["Gönderilmedi", "E-posta ile Gönderildi", "WhatsApp ile Gönderildi"] else ["Gönderilmedi", "E-posta ile Gönderildi", "WhatsApp ile Gönderildi"].index(row_sel["Iletim_Durumu"]))
        with col_op3:
            yeni_odeme = st.selectbox("Ödeme Durumu:", ["Ödeme Bekleniyor", "Ödeme Alındı", "Ödeme Gecikti"], index=0 if row_sel["Odeme_Durumu"] not in ["Ödeme Bekleniyor", "Ödeme Alındı", "Ödeme Gecikti"] else ["Ödeme Bekleniyor", "Ödeme Alındı", "Ödeme Gecikti"].index(row_sel["Odeme_Durumu"]))
            
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("Durumu Güncelle", use_container_width=True):
                df_teklifler.loc[df_teklifler["Teklif_ID"].astype(str) == str(secilen_teklif_id), "Durum"] = yeni_durum
                df_teklifler.loc[df_teklifler["Teklif_ID"].astype(str) == str(secilen_teklif_id), "Iletim_Durumu"] = yeni_iletim
                df_teklifler.loc[df_teklifler["Teklif_ID"].astype(str) == str(secilen_teklif_id), "Odeme_Durumu"] = yeni_odeme
                df_teklifler.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')
                st.success("Teklif durumu güncellendi!")
                st.rerun()
        
        with col_btn2:
            st.markdown("<p style='color:#ef4444; font-weight:bold; margin-bottom: 2px; margin-top: -10px;'>⚠️ Tehlikeli Alan</p>", unsafe_allow_html=True)
            confirm_sil = st.checkbox("Seçili teklifi silmeyi onaylıyorum.", key="confirm_delete_check")
            if st.button("🗑️ Teklifi Kalıcı Olarak Sil", disabled=not confirm_sil, use_container_width=True):
                df_teklifler = df_teklifler[df_teklifler["Teklif_ID"].astype(str) != str(secilen_teklif_id)]
                df_teklifler.to_csv(FILE_TEKLIFLER, index=False, encoding='utf-8-sig')
                st.success("Teklif başarıyla silindi!")
                st.rerun()

# ========================================================
# 3. MODÜL: SİSTEM AYARLARI & SAC FİYATLARI
# ========================================================
elif secilen_modul == "⚙️ Sistem Ayarları & Sac Fiyatları":
    st.markdown("<div class='main-title'>Sistem Ayarları ve Sac Birim Fiyatları</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>Hammadde Birim Maliyetleri ve Kur Yönetimi</div>", unsafe_allow_html=True)
    
    st.subheader("💶 Döviz Kuru Ayarları")
    col_cur1, col_cur2 = st.columns(2)
    with col_cur1:
        kur_modu = st.radio("Döviz Kuru Modu:", ["Canlı", "Manuel"], index=0 if st.session_state["exchange_mode"] == "Canlı" else 1)
        st.session_state["exchange_mode"] = kur_modu
    with col_cur2:
        if kur_modu == "Manuel":
            manuel_kur = st.number_input("Manuel EUR/TRY Kuru:", min_value=1.0, value=float(st.session_state["custom_rate"]), step=0.1)
            st.session_state["custom_rate"] = manuel_kur
        else:
            st.info(f"Canlı kur aktif (Open ER-API). Güncel kur: {st.session_state['live_rate']:.4f} TL")
            
    st.markdown("---")
    st.subheader("🛠️ Sac Malzeme Birim Fiyatları (EUR / kg)")
    
    edited_sac_df = st.data_editor(df_sac_fiyatlari, use_container_width=True, num_rows="dynamic")
    if st.button("Sac Fiyatlarını Kaydet"):
        edited_sac_df.to_csv(FILE_SAC_FIYATLARI, index=False, encoding='utf-8-sig')
        st.success("Sac birim fiyatları başarıyla güncellendi!")
        st.rerun()

# ========================================================
# 4. MODÜL: STOK YÖNETİMİ
# ========================================================
elif secilen_modul == "📦 Stok Yönetimi":
    st.markdown("<div class='main-title'>Depo Envanteri ve Malzeme Takip Konsolu</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>Depo Envanteri ve Malzeme Takip Konsolu</div>", unsafe_allow_html=True)
    
    edited_stok_df = st.data_editor(df_stok, use_container_width=True, num_rows="dynamic")
    if st.button("Stok Envanterini Güncelle"):
        edited_stok_df.to_csv(FILE_STOK, index=False, encoding='utf-8-sig')
        st.success("Stok verileri başarıyla kaydedildi!")
        st.rerun()

# ========================================================
# 5. MODÜL: FİNANS & MUHASEBE RAPORU
# ========================================================
elif secilen_modul == "📊 Finans & Muhasebe Raporu":
    st.markdown("<div class='main-title'>Finans ve Muhasebe Raporlama Konsolu</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>Gelir, Gider, Kasa ve Nakit Akışı Yönetimi</div>", unsafe_allow_html=True)
    
    tab_fin1, tab_fin2 = st.tabs(["💸 Gider Yönetimi", "💰 Gelir Yönetimi"])
    
    with tab_fin1:
        st.subheader("Gider Ekle")
        with st.form("gider_form"):
            g_tarih = st.date_input("Gider Tarihi", datetime.date.today())
            g_kat = st.selectbox("Kategori", ["Hammadde", "Enerji", "Maaşlar", "Kira", "Bakım-Onarım", "Diğer"])
            g_tutar = st.number_input("Tutar (TL)", min_value=0.0, value=1000.0)
            g_aciklama = st.text_input("Açıklama")
            g_submit = st.form_submit_button("Gideri Kaydet")
            
            if g_submit:
                yeni_gider = pd.DataFrame([[g_tarih, g_kat, "Genel", g_tutar, g_aciklama]], columns=["Tarih", "Kategori", "Alt_Kategori", "Tutar_TL", "Açıklama"])
                df_gider_updated = pd.concat([df_gider, yeni_gider], ignore_index=True)
                df_gider_updated.to_csv(FILE_GIDERLER, index=False, encoding='utf-8-sig')
                st.success("Gider eklendi!")
                st.rerun()
                
        st.subheader("Mevcut Giderler")
        if not df_gider.empty:
            st.dataframe(df_gider, use_container_width=True)
            st.metric("Toplam Gider", f"{df_gider['Tutar_TL'].sum():,.2f} TL")
            
    with tab_fin2:
        st.subheader("Gelir Ekle")
        with st.form("gelir_form"):
            gel_tarih = st.date_input("Gelir Tarihi", datetime.date.today())
            gel_musteri = st.text_input("Müşteri")
            gel_yontem = st.selectbox("Ödeme Yöntemi", ["Nakit", "Banka Havalesi", "Çek", "Kredi Kartı"])
            gel_tutar = st.number_input("Tutar (TL)", min_value=0.0, value=5000.0)
            gel_aciklama = st.text_input("Gelir Açıklaması")
            gel_submit = st.form_submit_button("Geliri Kaydet")
            
            if gel_submit:
                yeni_gelir = pd.DataFrame([[gel_tarih, gel_musteri, gel_yontem, gel_tutar, "", gel_aciklama]], columns=["Tarih", "Müşteri", "Ödeme_Yöntemi", "Tutar_TL", "Çek_Vadesi", "Açıklama"])
                df_gelir_updated = pd.concat([df_gelir, yeni_gelir], ignore_index=True)
                df_gelir_updated.to_csv(FILE_GELIRLER, index=False, encoding='utf-8-sig')
                st.success("Gelir eklendi!")
                st.rerun()
                
        st.subheader("Mevcut Gelirler")
        if not df_gelir.empty:
            st.dataframe(df_gelir, use_container_width=True)
            st.metric("Toplam Gelir", f"{df_gelir['Tutar_TL'].sum():,.2f} TL")
