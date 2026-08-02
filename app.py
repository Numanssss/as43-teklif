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
import tempfile

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
    /* Global sayfa arka planı ve Pull-to-Refresh Engelleme */
    html, body {
        background-color: #0f172a;
        color: #f8fafc;
        margin: 0 !important;
        padding: 0 !important;
        overscroll-behavior-y: contain !important; /* Sayfa yenilemeyi tamamen engeller */
        overscroll-behavior-x: none !important;
    }
    
    /* Mobil Kaydırma ve Stabilizasyon */
    [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #0f172a;
        color: #f8fafc;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior-y: contain !important; /* Alt container yenilemesini engeller */
    }
    
    /* GPU Donanım Hızlandırması (Arayüz Takılmalarını ve Kaydırma Kilitlenmelerini Engeller) */
    .main .block-container {
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
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
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

def generate_pdf(teklif_no, hazirlayan, musteri_adi, sablon, secilen_sac, sac_kalinligi, net_agirlik, fire_orani, hammadde_maliyeti_eur, lazer_suresi, lazer_maliyeti_eur, bukum_suresi, bukum_maliyeti_eur, iscilik_suresi, iscilik_maliyeti_eur, sabit_gider_payi, sabit_gider_maliyeti_eur, toplam_maliyet_eur, liste_fiyati_eur, liste_fiyati_try, active_rate, iskonto_orani, iskonto_tutari_eur, kdv_orani, kdv_tutari_eur, genel_toplam_eur, detay_data=None, images_paths=None):
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
    
    if detay_data and images_paths:
        pdf.add_page()
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.rect(10, 10, 190, 22)
        pdf.line(75, 10, 75, 32)
        
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 12, 13, 58)
        else:
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_xy(12, 18)
            pdf.cell(58, 8, "AS43 GRUP", align="C")
            
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_xy(75, 15)
        pdf.cell(70, 12, "ASANSOR IMALAT TEKLIF EKI", align="C")
        
        pdf.line(145, 10, 145, 32)
        pdf.line(145, 15.5, 200, 15.5)
        pdf.line(145, 21, 200, 21)
        pdf.line(145, 26.5, 200, 26.5)
        pdf.line(175, 10, 175, 21)
        pdf.line(175, 26.5, 175, 32)
        
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_xy(146, 11)
        pdf.cell(28, 4, "DOKUMAN NO")
        pdf.set_xy(176, 11)
        pdf.cell(24, 4, "REVIZYON NO")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(163, 11)
        pdf.cell(10, 4, "ONY-FRM-026")
        pdf.set_xy(193, 11)
        pdf.cell(10, 4, "1")
        
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_xy(146, 16.5)
        pdf.cell(28, 4, "YAYIN TARIHI")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(163, 16.5)
        pdf.cell(10, 4, "15.12.2022")
        
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_xy(146, 22)
        pdf.cell(50, 4, "REVIZYON TARIHI")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(170, 22)
        pdf.cell(20, 4, "01.06.2023")
        
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_xy(146, 27.5)
        pdf.cell(28, 4, "SAYFA NO")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(176, 27.5)
        pdf.cell(24, 4, "2 / 2")
        
        pdf.set_fill_color(245, 158, 11)
        pdf.rect(10, 32, 190, 5, 'F')
        pdf.rect(10, 32, 190, 5)
        pdf.line(57.5, 32, 57.5, 37)
        pdf.line(105, 32, 105, 37)
        pdf.line(152.5, 32, 152.5, 37)
        
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(10, 32)
        pdf.cell(47.5, 5, "TABAN MODELI RESMI", align="C")
        pdf.set_xy(57.5, 32)
        pdf.cell(47.5, 5, "KABIN MODELI RESMI", align="C")
        pdf.set_xy(105, 32)
        pdf.cell(47.5, 5, "TAVAN MODELI RESMI", align="C")
        pdf.set_xy(152.5, 32)
        pdf.cell(47.5, 5, "KUYU KESITI / OZEL", align="C")
        pdf.set_text_color(0, 0, 0)
        
        pdf.rect(10, 37, 190, 30)
        pdf.line(57.5, 37, 57.5, 67)
        pdf.line(105, 37, 105, 67)
        pdf.line(152.5, 37, 152.5, 67)
        
        image_keys = ["taban", "kabin", "tavan", "kuyu"]
        for idx, key in enumerate(image_keys):
            img_path = images_paths.get(key)
            x_start = 10 + (idx * 47.5)
            if img_path and os.path.exists(img_path):
                try:
                    pdf.image(img_path, x_start + 2, 38, 43.5, 28)
                except Exception:
                    pass
                
        pdf.rect(10, 67, 190, 6)
        pdf.line(57.5, 67, 57.5, 73)
        pdf.line(105, 67, 105, 73)
        pdf.line(152.5, 67, 152.5, 73)
        pdf.set_font("Helvetica", "B", 6.5)
        
        pdf.set_xy(10, 68)
        pdf.cell(47.5, 4, clean(f"Doseme: {detay_data.get('taban_modeli', '')}"), align="C")
        pdf.set_xy(57.5, 68)
        pdf.cell(47.5, 4, clean(f"Kabin: {detay_data.get('dim_kabin', 'Olcu Yok')}"), align="C")
        pdf.set_xy(105, 68)
        pdf.cell(47.5, 4, clean(f"Tavan: {detay_data.get('tavan_modeli', '')}"), align="C")
        pdf.set_xy(152.5, 68)
        pdf.cell(47.5, 4, clean(f"Kuyu: {detay_data.get('dim_kuyu', 'Olcu Yok')}"), align="C")
        
        pdf.set_fill_color(245, 158, 11)
        pdf.rect(10, 75, 190, 5, 'F')
        pdf.rect(10, 75, 190, 5)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(10, 75)
        pdf.cell(190, 5, "TEKNIK ASANSOR SPECIFIKASYONLARI", align="C")
        pdf.set_text_color(0, 0, 0)
        
        pdf.rect(10, 80, 190, 45)
        pdf.line(105, 80, 105, 125)
        for i in range(1, 9):
            y_line = 80 + (i * 5)
            pdf.line(10, y_line, 200, y_line)
            
        left_specs = [
            ("Kapasite", clean(detay_data.get("kapasite", "")) + " kg"),
            ("Hiz", clean(detay_data.get("hiz", "")) + " m/s"),
            ("Durak", clean(detay_data.get("durak", "")) + " Ad."),
            ("Giris Sayisi", clean(detay_data.get("giris_sayisi", ""))),
            ("Aski Tipi", clean(detay_data.get("aski_tipi", ""))),
            ("Kuyu Tipi", clean(detay_data.get("kuyu_tipi", ""))),
            ("Ana Ray Olcusu", clean(detay_data.get("ana_ray", ""))),
            ("Ana Ray Arasi Mesafesi", clean(detay_data.get("ana_ray_arasi", "")))
        ]
        right_specs = [
            ("Kabin Modeli", clean(detay_data.get("kabin_modeli", ""))),
            ("Kabin Kaplamasi", clean(detay_data.get("kabin_kaplama", ""))),
            ("Doseme Tipi", clean(detay_data.get("doseme_tipi", ""))),
            ("Aksesuar Kaplamasi", clean(detay_data.get("aksesuar_kaplama", ""))),
            ("Kapi Giris Kaplamasi", clean(detay_data.get("kapi_giris_kaplama", ""))),
            ("Tavan Modeli", clean(detay_data.get("tavan_modeli", ""))),
            ("Taban Modeli", clean(detay_data.get("taban_modeli", ""))),
            ("Ayna Yeri ve Olcusu", clean(detay_data.get("ayna_detay", "")))
        ]
        
        pdf.set_font("Helvetica", "B", 7)
        for idx, (label, val) in enumerate(left_specs):
            y_pos = 81 + (idx * 5)
            pdf.set_xy(12, y_pos)
            pdf.cell(45, 4, label + ":")
            pdf.set_font("Helvetica", "", 7)
            pdf.set_xy(57, y_pos)
            pdf.cell(45, 4, str(val))
            pdf.set_font("Helvetica", "B", 7)
            
        for idx, (label, val) in enumerate(right_specs):
            y_pos = 81 + (idx * 5)
            pdf.set_xy(107, y_pos)
            pdf.cell(45, 4, label + ":")
            pdf.set_font("Helvetica", "", 7)
            pdf.set_xy(152, y_pos)
            pdf.cell(45, 4, str(val))
            pdf.set_font("Helvetica", "B", 7)
            
        pdf.rect(10, 126, 190, 20)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_xy(12, 127)
        pdf.cell(10, 4, "NOT:")
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_xy(22, 127)
        pdf.multi_cell(176, 3, clean(detay_data.get("not", "")))
        
    out = pdf.output(dest='S')
    if isinstance(out, str):
        return out.encode('latin1')
    return bytes(out)

def generate_asansor_imalat_pdf(data, images):
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            pass
        def footer(self):
            pass

    def clean(t):
        if not t: return ""
        t = str(t)
        replacements = {
            'ı': 'i', 'İ': 'I', 'ş': 's', 'Ş': 'S',
            'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U',
            'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C',
            '€': 'EUR', '’': "'", '‘': "'", '”': '"', '“': '"'
        }
        for k, v in replacements.items():
            t = t.replace(k, v)
        return t

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(False)
    
    # 1. HEADER SECTION
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.rect(10, 10, 190, 22) # Main header rect
    pdf.line(75, 10, 75, 32)
    
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 12, 13, 58)
    else:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_xy(12, 18)
        pdf.cell(58, 8, "AS43 GRUP", align="C")
        
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(75, 15)
    pdf.cell(70, 12, "ASANSOR IMALAT TEKLIF TALEP FORMU", align="C")
    
    pdf.line(145, 10, 145, 32)
    pdf.line(145, 15.5, 200, 15.5)
    pdf.line(145, 21, 200, 21)
    pdf.line(145, 26.5, 200, 26.5)
    pdf.line(175, 10, 175, 21)
    pdf.line(175, 26.5, 175, 32)
    
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(146, 11)
    pdf.cell(28, 4, "DOKUMAN NO")
    pdf.set_xy(176, 11)
    pdf.cell(24, 4, "REVIZYON NO")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(163, 11)
    pdf.cell(10, 4, "ONY-FRM-026")
    pdf.set_xy(193, 11)
    pdf.cell(10, 4, "1")
    
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(146, 16.5)
    pdf.cell(28, 4, "YAYIN TARIHI")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(163, 16.5)
    pdf.cell(10, 4, "15.12.2022")
    
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(146, 22)
    pdf.cell(50, 4, "REVIZYON TARIHI")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(170, 22)
    pdf.cell(20, 4, "01.06.2023")
    
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(146, 27.5)
    pdf.cell(28, 4, "SAYFA NO")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(176, 27.5)
    pdf.cell(24, 4, "1 / 1")
    
    # 2. IMALAT TEKLIF TALEP FORMU HEADER BAR
    pdf.set_fill_color(245, 158, 11) # Orange Header
    pdf.rect(10, 32, 190, 5, 'F')
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 32)
    pdf.cell(190, 5, "IMALAT TEKLIF TALEP FORMU", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.rect(10, 32, 190, 5)
    
    # 3. FIRMA / REFERANS / SIPARIS NO
    pdf.rect(10, 37, 190, 12)
    pdf.line(100, 37, 100, 49)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_xy(12, 38)
    pdf.cell(20, 4, "Firma:")
    pdf.set_xy(12, 41)
    pdf.cell(20, 4, "Referans:")
    pdf.set_xy(12, 44)
    pdf.cell(20, 4, "Siparis No:")
    
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(35, 38)
    pdf.cell(60, 4, clean(data.get("firma", "")))
    pdf.set_xy(35, 41)
    pdf.cell(60, 4, clean(data.get("referans", "")))
    pdf.set_xy(35, 44)
    pdf.cell(60, 4, clean(data.get("siparis_no", "")))
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(110, 40)
    pdf.cell(80, 6, clean(data.get("teklif_no", "")), align="C")
    
    # 4. KABIN OZELLIKLERI HEADER
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 49, 190, 5, 'F')
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 49)
    pdf.cell(190, 5, "KABIN OZELLIKLERI", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.rect(10, 49, 190, 5)
    
    # 5. KABIN OZELLIKLERI GRID
    pdf.rect(10, 54, 190, 50)
    pdf.line(105, 54, 105, 104)
    
    for i in range(1, 10):
        y_line = 54 + (i * 5)
        pdf.line(10, y_line, 200, y_line)
        
    left_specs = [
        ("Kapasite", clean(data.get("kapasite", "")) + " kg"),
        ("Hiz", clean(data.get("hiz", "")) + " m/s"),
        ("Kabin Genislik x Derinlik", clean(data.get("kabin_gen_der", ""))),
        ("Seyir / Son Kat / Kuyu D.", clean(data.get("seyir_detay", ""))),
        ("Durak", clean(data.get("durak", "")) + " Ad."),
        ("Giris Sayisi", clean(data.get("giris_sayisi", ""))),
        ("Aski Tipi", clean(data.get("aski_tipi", ""))),
        ("Kuyu Tipi", clean(data.get("kuyu_tipi", ""))),
        ("Ana Ray Olcusu", clean(data.get("ana_ray", ""))),
        ("Ana Ray Arasi Mesafesi", clean(data.get("ana_ray_arasi", "")))
    ]
    right_specs = [
        ("Kabin Modeli", clean(data.get("kabin_modeli", ""))),
        ("Kabin Kaplamasi", clean(data.get("kabin_kaplama", ""))),
        ("Doseme Tipi", clean(data.get("doseme_tipi", ""))),
        ("Aksesuar Kaplamasi", clean(data.get("aksesuar_kaplama", ""))),
        ("Kapi Giris Kaplamasi", clean(data.get("kapi_giris_kaplama", ""))),
        ("Tavan Modeli", clean(data.get("tavan_modeli", ""))),
        ("Taban Modeli", clean(data.get("taban_modeli", ""))),
        ("Ayna Yeri ve Olcusu", clean(data.get("ayna_detay", ""))),
        ("Kabin Sabitleme Kiti", clean(data.get("sabitleme_kit", ""))),
        ("Asiri Yuk Sistemi", clean(data.get("asiri_yuk", "")))
    ]
    
    pdf.set_font("Helvetica", "B", 7)
    for idx, (label, val) in enumerate(left_specs):
        y_pos = 55 + (idx * 5)
        pdf.set_xy(12, y_pos)
        pdf.cell(45, 4, label + ":")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(57, y_pos)
        pdf.cell(45, 4, str(val))
        pdf.set_font("Helvetica", "B", 7)
        
    for idx, (label, val) in enumerate(right_specs):
        y_pos = 55 + (idx * 5)
        pdf.set_xy(107, y_pos)
        pdf.cell(45, 4, label + ":")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(152, y_pos)
        pdf.cell(45, 4, str(val))
        pdf.set_font("Helvetica", "B", 7)
        
    # 6. NOT SECTION
    pdf.rect(10, 104, 190, 12)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_xy(12, 105)
    pdf.cell(10, 4, "NOT:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(22, 105)
    pdf.multi_cell(176, 3, clean(data.get("not", "")))
    
    # 7. IMAGE SLOTS
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 116, 190, 5, 'F')
    pdf.rect(10, 116, 190, 5)
    pdf.line(57.5, 116, 57.5, 121)
    pdf.line(105, 116, 105, 121)
    pdf.line(152.5, 116, 152.5, 121)
    
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 116)
    pdf.cell(47.5, 5, "TABAN MODELI RESMI", align="C")
    pdf.set_xy(57.5, 116)
    pdf.cell(47.5, 5, "KABIN MODELI RESMI", align="C")
    pdf.set_xy(105, 116)
    pdf.cell(47.5, 5, "TAVAN MODELI RESMI", align="C")
    pdf.set_xy(152.5, 116)
    pdf.cell(47.5, 5, "KUYU KESITI / OZEL", align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.rect(10, 121, 190, 30)
    pdf.line(57.5, 121, 57.5, 151)
    pdf.line(105, 121, 105, 151)
    pdf.line(152.5, 121, 152.5, 151)
    
    image_keys = ["taban", "kabin", "tavan", "kuyu"]
    for idx, key in enumerate(image_keys):
        img_path = images.get(key)
        x_start = 10 + (idx * 47.5)
        if img_path and os.path.exists(img_path):
            try:
                pdf.image(img_path, x_start + 2, 122, 43.5, 28)
            except Exception:
                pass
            
    pdf.rect(10, 151, 190, 6)
    pdf.line(57.5, 151, 57.5, 157)
    pdf.line(105, 151, 105, 157)
    pdf.line(152.5, 151, 152.5, 157)
    pdf.set_font("Helvetica", "B", 6.5)
    
    pdf.set_xy(10, 152)
    pdf.cell(47.5, 4, clean(f"Doseme: {data.get('taban_modeli', '')}"), align="C")
    pdf.set_xy(57.5, 152)
    pdf.cell(47.5, 4, clean(f"Kabin: {data.get('dim_kabin', 'Olcu Yok')}"), align="C")
    pdf.set_xy(105, 152)
    pdf.cell(47.5, 4, clean(f"Tavan: {data.get('tavan_modeli', '')}"), align="C")
    pdf.set_xy(152.5, 152)
    pdf.cell(47.5, 4, clean(f"Kuyu: {data.get('dim_kuyu', 'Olcu Yok')}"), align="C")
    
    # 8. AGIRLIK SASESI & MAKINE MOTOR BILGILERI
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 157, 190, 5, 'F')
    pdf.rect(10, 157, 190, 5)
    pdf.line(105, 157, 105, 162)
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(10, 157)
    pdf.cell(95, 5, "Agirlik Sasesi", align="C")
    pdf.set_xy(105, 157)
    pdf.cell(95, 5, "Makine-Motor ve Makine Sasesi Bilgileri", align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.rect(10, 162, 190, 16)
    pdf.line(105, 162, 105, 178)
    pdf.line(10, 170, 200, 170)
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(12, 163)
    pdf.cell(40, 3, "Agirlik Sasesi:")
    pdf.set_xy(12, 166)
    pdf.cell(40, 3, "Agirlik Ray Arasi:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(42, 163)
    pdf.cell(50, 3, clean(data.get("agirlik_sasesi", "")))
    pdf.set_xy(42, 166)
    pdf.cell(50, 3, clean(data.get("agirlik_ray_arasi", "")) + " cm")
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(107, 163)
    pdf.cell(40, 3, "Makine Sasesi:")
    pdf.set_xy(107, 166)
    pdf.cell(40, 3, "Motor Marka:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(137, 163)
    pdf.cell(50, 3, clean(data.get("makine_sasesi", "")))
    pdf.set_xy(137, 166)
    pdf.cell(50, 3, clean(data.get("motor_marka", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(12, 171)
    pdf.cell(40, 3, "Agirlik Adet:")
    pdf.set_xy(12, 174)
    pdf.cell(40, 3, "Agirlik Ray Olcusu:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(42, 171)
    pdf.cell(50, 3, clean(data.get("agirlik_adet", "")))
    pdf.set_xy(42, 174)
    pdf.cell(50, 3, clean(data.get("agirlik_ray_olcu", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(107, 171)
    pdf.cell(40, 3, "Kasnak Olculeri:")
    pdf.set_xy(107, 174)
    pdf.cell(40, 3, "Seperator (K. Agirlik):")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(137, 171)
    pdf.cell(50, 3, clean(data.get("kasnak_olculeri", "")))
    pdf.set_xy(137, 174)
    pdf.cell(50, 3, clean(data.get("seperator", "")))
    
    # 9. KAPI OLCU VE OZELLIKLERI
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 178, 190, 5, 'F')
    pdf.rect(10, 178, 190, 5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(10, 178)
    pdf.cell(190, 5, "Kapi Olcu ve Ozellikleri", align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.rect(10, 183, 190, 20)
    pdf.line(105, 183, 105, 203)
    pdf.line(10, 193, 200, 193)
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(12, 184)
    pdf.cell(45, 3, "Genislik x Yukseklik:")
    pdf.set_xy(12, 187)
    pdf.cell(45, 3, "Kabin Kapi Adedi:")
    pdf.set_xy(12, 190)
    pdf.cell(45, 3, "Model:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(57, 184)
    pdf.cell(45, 3, clean(data.get("kapi_gen_yuk", "")))
    pdf.set_xy(57, 187)
    pdf.cell(45, 3, clean(data.get("kabin_kapi_adedi", "")))
    pdf.set_xy(57, 190)
    pdf.cell(45, 3, clean(data.get("kapi_model", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(107, 184)
    pdf.cell(45, 3, "Kat Kapi Adedi:")
    pdf.set_xy(107, 187)
    pdf.cell(45, 3, "Model:")
    pdf.set_xy(107, 190)
    pdf.cell(45, 3, "Yon 1:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(152, 184)
    pdf.cell(45, 3, clean(data.get("kat_kapi_adedi", "")))
    pdf.set_xy(152, 187)
    pdf.cell(45, 3, clean(data.get("kat_kapi_model", "")))
    pdf.set_xy(152, 190)
    pdf.cell(45, 3, clean(data.get("kapi_yon", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(12, 194)
    pdf.cell(45, 3, "Yon 1 / Kaplama:")
    pdf.set_xy(12, 197)
    pdf.cell(45, 3, "NOT:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(57, 194)
    pdf.cell(45, 3, clean(data.get("kapi_kaplama", "")))
    pdf.set_xy(57, 197)
    pdf.cell(45, 3, clean(data.get("kapi_not", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(107, 194)
    pdf.cell(45, 3, "Kasa Kaplama:")
    pdf.set_xy(107, 197)
    pdf.cell(45, 3, "Panel Kaplama:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(152, 194)
    pdf.cell(45, 3, clean(data.get("kasa_kaplama", "")))
    pdf.set_xy(152, 197)
    pdf.cell(45, 3, clean(data.get("panel_kaplama", "")))
    
    # 10. KUMANDA PANOSU
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 203, 190, 5, 'F')
    pdf.rect(10, 203, 190, 5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(10, 203)
    pdf.cell(190, 5, "Kumanda Panosu", align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.rect(10, 208, 190, 15)
    pdf.line(105, 208, 105, 223)
    pdf.line(10, 215.5, 200, 215.5)
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(12, 209)
    pdf.cell(45, 3, "Adet:")
    pdf.set_xy(12, 212)
    pdf.cell(45, 3, "Guc:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(57, 209)
    pdf.cell(45, 3, clean(data.get("pano_adet", "")))
    pdf.set_xy(57, 212)
    pdf.cell(45, 3, clean(data.get("pano_guc", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(107, 209)
    pdf.cell(45, 3, "Tipi:")
    pdf.set_xy(107, 212)
    pdf.cell(45, 3, "Surucu:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(152, 209)
    pdf.cell(45, 3, clean(data.get("pano_tipi", "")))
    pdf.set_xy(152, 212)
    pdf.cell(45, 3, clean(data.get("pano_surucu", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(12, 216.5)
    pdf.cell(45, 3, "Kumanda Karti:")
    pdf.set_xy(12, 219.5)
    pdf.cell(45, 3, "Salt Malzeme:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(57, 216.5)
    pdf.cell(45, 3, clean(data.get("pano_kart", "")))
    pdf.set_xy(57, 219.5)
    pdf.cell(45, 3, clean(data.get("pano_salt", "")))
    
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_xy(107, 216.5)
    pdf.cell(45, 3, "Konum Yeri:")
    pdf.set_xy(107, 219.5)
    pdf.cell(45, 3, "NOT:")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_xy(152, 216.5)
    pdf.cell(45, 3, clean(data.get("pano_konum", "")))
    pdf.set_xy(152, 219.5)
    pdf.cell(45, 3, clean(data.get("pano_not", "")))
    
    # 11. MUSTERI TEMSILCISI & IMALAT MUDURU SIGNATURE AREA
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 223, 190, 5, 'F')
    pdf.rect(10, 223, 190, 5)
    pdf.line(105, 223, 105, 228)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_xy(10, 223)
    pdf.cell(95, 5, "Musteri Temsilcisi", align="C")
    pdf.set_xy(105, 223)
    pdf.cell(95, 5, "Imalat Muduru", align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.rect(10, 228, 190, 25)
    pdf.line(105, 228, 105, 253)
    
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_xy(12, 230)
    pdf.cell(50, 4, "Adi Soyadi:")
    pdf.set_xy(12, 234)
    pdf.cell(50, 4, "Tarih / Imza:")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(32, 230)
    pdf.cell(60, 4, clean(data.get("musteri_temsilcisi", "")))
    pdf.set_xy(12, 245)
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(80, 4, "**Bilgilerin Dogru Oldugunu Onayliyorum.**", align="C")
    
    pdf.set_xy(107, 230)
    pdf.cell(50, 4, "Adi Soyadi:")
    pdf.set_xy(107, 234)
    pdf.cell(50, 4, "Tarih / Imza:")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(127, 230)
    pdf.cell(60, 4, clean(data.get("imalat_muduru", "")))
    pdf.set_xy(107, 245)
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(80, 4, "**Imalata Engel Durum Tespit Edilmemistir.**", align="C")
    
    # 12. PLANLANAN IMALAT TESLIM TARIHLERI
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, 253, 190, 5, 'F')
    pdf.rect(10, 253, 190, 5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(10, 253)
    pdf.cell(190, 5, "Planlanan Imalat Teslim Tarihleri", align="C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.rect(10, 258, 190, 5)
    pdf.line(55, 258, 55, 263)
    pdf.line(110, 258, 110, 263)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_xy(10, 258)
    pdf.cell(45, 5, "Urunler", align="C")
    pdf.set_xy(55, 258)
    pdf.cell(55, 5, "Teslim Tarihi", align="C")
    pdf.set_xy(110, 258)
    pdf.cell(90, 5, "Aciklama", align="C")
    
    pdf.rect(10, 263, 190, 24)
    pdf.line(55, 263, 55, 287)
    pdf.line(110, 263, 110, 287)
    pdf.line(10, 269, 200, 269)
    pdf.line(10, 275, 200, 275)
    pdf.line(10, 281, 200, 281)
    
    deliveries = [
        ("Kabin(ler)", data.get("tarih_kabin", ""), data.get("desc_kabin", "")),
        ("Sase ve Pudreller", data.get("tarih_sase", ""), data.get("desc_sase", "")),
        ("Kapilar", data.get("tarih_kapi", ""), data.get("desc_kapi", "")),
        ("Pano(lar)", data.get("tarih_pano", ""), data.get("desc_pano", ""))
    ]
    pdf.set_font("Helvetica", "", 7)
    for idx, (prod, t_date, desc) in enumerate(deliveries):
        y_pos = 264 + (idx * 6)
        pdf.set_xy(12, y_pos)
        pdf.cell(40, 4, prod)
        pdf.set_xy(57, y_pos)
        pdf.cell(50, 4, str(t_date))
        pdf.set_xy(112, y_pos)
        pdf.cell(85, 4, desc)
        
    out = pdf.output(dest='S')
    if isinstance(out, str):
        return out.encode('latin1')
    return bytes(out)

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
        "🛗 Asansör İmalat Teklif Formu",
        "📋 Geçmiş Teklifler & Takip",
        "⚙️ Sistem Ayarları & Sac Fiyatları",
        "📦 Stok Yönetimi",
        "📊 Finans & Muhasebe Raporu"
    ]
)

st.sidebar.markdown("---")

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
        tab_calc, tab_tech = st.tabs(["💰 Maliyet & Fiyat Hesaplama", "📐 Teknik Detaylar & Görseller (Resimli Teklif Eki)"])
        
        with tab_calc:
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
                
            st.markdown("##### 📈 Kar, İskonto & KDV")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                sabit_gider_payi = st.number_input("Sabit Gider Payı (%):", min_value=0, max_value=100, value=15, step=1)
            with col_m2:
                kar_marji = st.number_input("Hedef Kar Marjı (%):", min_value=0, max_value=1000, value=25, step=1)
            with col_m3:
                iskonto_orani = st.number_input("İskonto Oranı (%):", min_value=0, max_value=100, value=10, step=1)
                
            kdv_orani = st.selectbox("KDV Oranı (%):", [0, 10, 20], index=2)

        with tab_tech:
            st.subheader("📐 Teknik Görsel ve Detay Eki (İsteğe Bağlı)")
            st.info("Bu alanları doldurursanız teklif PDF'inize otomatik olarak resimli ve ölçülü 2. sayfa eklenecektir.")
            
            t_kapasite = st.text_input("Kapasite (kg):", value="450", key="t_kapasite")
            t_hiz = st.text_input("Hız (m/s):", value="YOK", key="t_hiz")
            t_durak = st.text_input("Durak Adedi:", value="0", key="t_durak")
            t_giris = st.text_input("Giriş Sayısı:", value="TEK GİRİŞ", key="t_giris")
            t_aski = st.text_input("Askı Tipi:", value="1/2", key="t_aski")
            t_kuyu = st.text_input("Kuyu Tipi:", value="BETON", key="t_kuyu")
            t_ray = st.text_input("Ana Ray Ölçüsü:", value="YOK", key="t_ray")
            t_ray_arasi = st.text_input("Ana Ray Arası Mesafesi:", value="HİDROLİK L KARKAS ARKADA", key="t_ray_arasi")
            
            st.markdown("---")
            t_model = st.text_input("Kabin Modeli:", value="ONY 2232", key="t_model")
            t_kaplama = st.text_input("Kabin Kaplaması:", value="304 SATİNE PASL", key="t_kaplama")
            t_doseme = st.text_input("Döşeme Tipi:", value="DİKEY", key="t_doseme")
            t_aksesuar = st.text_input("Aksesuar Kaplaması:", value="304 SATİNE PASL", key="t_aksesuar")
            t_kapi_giris = st.text_input("Kapı Giriş Kaplaması:", value="304 SATİNE PASL", key="t_kapi_giris")
            t_tavan = st.text_input("Tavan Modeli:", value="T-189", key="t_tavan")
            t_taban = st.text_input("Taban Modeli:", value="ANTİBAKTERİYEL+SUNTA", key="t_taban")
            t_ayna = st.text_input("Ayna Yeri ve Ölçüsü:", value="YERDEN 30 CM SÜPER AYNA PASL (DAR OLSUN)", key="t_ayna")
            
            st.markdown("---")
            st.subheader("🖼️ Görsel Yüklemeleri & Alt Ölçüler")
            t_file_taban = st.file_uploader("Taban Resmi:", type=["png", "jpg", "jpeg"], key="t_up_taban")
            t_dim_taban = st.text_input("Taban Ölçü Bilgisi:", value="Antibakteriyel Sunta", key="t_in_dim_taban")
            
            t_file_kabin = st.file_uploader("Kabin Resmi:", type=["png", "jpg", "jpeg"], key="t_up_kabin")
            t_dim_kabin = st.text_input("Kabin Ölçü Bilgisi (Genişlik x Derinlik):", value="150 X 85 cm", key="t_in_dim_kabin")
            
            t_file_tavan = st.file_uploader("Tavan Resmi:", type=["png", "jpg", "jpeg"], key="t_up_tavan")
            t_dim_tavan = st.text_input("Tavan Ölçü Bilgisi:", value="T-189 Model", key="t_in_dim_tavan")
            
            t_file_kuyu = st.file_uploader("Kuyu/Özel Çizim Resmi:", type=["png", "jpg", "jpeg"], key="t_up_kuyu")
            t_dim_kuyu = st.text_input("Kuyu Ölçü Bilgisi (Kuyu Genişlik x Derinlik):", value="170 X 124 cm", key="t_in_dim_kuyu")
            
            t_not = st.text_area("Özel Açıklama / Notlar:", value="HİDROLİK ASANSÖR SADECE KABİN KOVASI YAPILACAKTIR. 150 CM GENİŞLİK 85 CM DERİNLİK OLACAKTIR.", key="t_not")

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
            <p><b>Liste Satış Fiyatı (Kâr Dahil):</b> {liste_fiyati_eur:.2f} EUR</p>
            <p><b>İskonto Tutarı (%{iskonto_orani}):</b> -{iskonto_tutari_eur:.2f} EUR</p>
            <h2 style='color:#22c55e; margin-bottom:5px;'>GENEL TOPLAM: {genel_toplam_eur:.2f} EUR</h2>
            <p style='color:#94a3b8; font-size:0.9rem;'>TL Karşılığı (Kur: {active_rate:.2f}): <b>{genel_toplam_try:,.2f} TL</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
            
            # Görsel ve Detayları Geçici Olarak Kaydetme
            images_paths_tech = {}
            for k, f in [("taban", t_file_taban), ("kabin", t_file_kabin), ("tavan", t_file_tavan), ("kuyu", t_file_kuyu)]:
                if f:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        tmp.write(f.getvalue())
                        images_paths_tech[k] = tmp.name
                else:
                    images_paths_tech[k] = None
                    
            pdf_data_tech = {
                "kapasite": t_kapasite,
                "hiz": t_hiz,
                "durak": t_durak,
                "giris_sayisi": t_giris,
                "aski_tipi": t_aski,
                "kuyu_tipi": t_kuyu,
                "ana_ray": t_ray,
                "ana_ray_arasi": t_ray_arasi,
                "kabin_modeli": t_model,
                "kabin_kaplama": t_kaplama,
                "doseme_tipi": t_doseme,
                "aksesuar_kaplama": t_aksesuar,
                "kapi_giris_kaplama": t_kapi_giris,
                "tavan_modeli": t_tavan,
                "taban_modeli": t_taban,
                "ayna_detay": t_ayna,
                "dim_kabin": t_dim_kabin,
                "dim_kuyu": t_dim_kuyu,
                "not": t_not
            }
            
            pdf_bytes = generate_pdf(
                teklif_no, st.session_state["username"], musteri_adi, sablon, secilen_sac, sac_kalinligi,
                net_agirlik, fire_orani, hammadde_maliyeti_eur, lazer_suresi, lazer_maliyeti_eur,
                bukum_suresi, bukum_maliyeti_eur, iscilik_suresi, iscilik_maliyeti_eur, sabit_gider_payi,
                sabit_gider_maliyeti_eur, toplam_maliyet_eur, liste_fiyati_eur, (liste_fiyati_eur * active_rate),
                active_rate, iskonto_orani, iskonto_tutari_eur, kdv_orani, kdv_tutari_eur, genel_toplam_eur,
                detay_data=pdf_data_tech, images_paths=images_paths_tech
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
# 1B. MODÜL: ASANSÖR İMALAT TEKLİF FORMU
# ========================================================
elif secilen_modul == "🛗 Asansör İmalat Teklif Formu":
    st.markdown("<div class='main-title'>Asansör İmalat Teklif & Teknik Detay Formu</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>Teknik Özellikler, Ölçüler ve Resimli Detay Kartı Hazırlama</div>", unsafe_allow_html=True)
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.subheader("📋 Genel ve Kabin Özellikleri")
        firma = st.text_input("Firma / Müşteri Adı:", value="AS 43 ASANSÖR")
        referans = st.text_input("Referans (örn: HİDROLİK ÇARPMA):", value="HİDROLİK ÇARPMA")
        siparis_no = st.text_input("Sipariş No (örn: YI2202500003058):", value="YI2202500003058")
        teklif_no_form = st.text_input("Teklif / Form Referans No:", value="2025/42")
        
        st.markdown("---")
        kapasite = st.text_input("Kapasite (kg):", value="450")
        hiz = st.text_input("Hız (m/s):", value="YOK")
        durak = st.text_input("Durak Adedi:", value="0")
        giris_sayisi = st.text_input("Giriş Sayısı (örn: TEK GİRİŞ):", value="TEK GİRİŞ")
        kabin_modeli = st.text_input("Kabin Modeli:", value="ONY 2232")
        kabin_kaplama = st.text_input("Kabin Kaplaması:", value="304 SATİNE PASL")
        doseme_tipi = st.text_input("Döşeme Tipi:", value="DİKEY")
        aksesuar_kaplama = st.text_input("Aksesuar Kaplaması:", value="304 SATİNE PASL")
        kapi_giris_kaplama = st.text_input("Kapı Giriş Kaplaması:", value="304 SATİNE PASL")
        tavan_modeli = st.text_input("Tavan Modeli:", value="T-189")
        taban_modeli = st.text_input("Taban Modeli:", value="ANTİBAKTERİYEL+SUNTA")
        aski_tipi = st.text_input("Askı Tipi:", value="1/2")
        kuyu_tipi = st.text_input("Kuyu Tipi:", value="BETON")
        ayna_detay = st.text_input("Ayna Yeri ve Ölçüsü:", value="YERDEN 30 CM SÜPER AYNA PASL (DAR OLSUN)")
        sabitleme_kit = st.text_input("Kabin Sabitleme Kiti:", value="YOK")
        asiri_yuk = st.text_input("Aşırı Yük Sistemi:", value="YOK")
        ana_ray = st.text_input("Ana Ray Ölçüsü:", value="YOK")
        ana_ray_arasi = st.text_input("Ana Ray Arası Mesafesi:", value="HİDROLİK L KARKAS ARKADA")
        
        st.markdown("---")
        st.subheader("⚙️ Ağırlık Şasesi ve Motor")
        agirlik_sasesi = st.text_input("Ağırlık Şasesi:", value="YOK")
        agirlik_ray_arasi = st.text_input("Ağırlık Ray Arası (cm):", value="YOK")
        agirlik_adet = st.text_input("Ağırlık Adet:", value="YOK")
        agirlik_ray_olcu = st.text_input("Ağırlık Ray Ölçüsü:", value="YOK")
        makine_sasesi = st.text_input("Makine Şasesi:", value="YOK")
        motor_marka = st.text_input("Motor Marka:", value="YOK")
        kasnak_olculeri = st.text_input("Kasnak Ölçüleri:", value="YOK")
        seperator = st.text_input("Seperatör (K. Ağırlık):", value="YOK")
        
    with col_e2:
        st.subheader("🚪 Kapı, Kumanda ve Diğer Bilgiler")
        kapi_gen_yuk = st.text_input("Kapı Giriş Genişlik x Yükseklik:", value="150 X 210")
        kabin_kapi_adedi = st.text_input("Kabin Kapı Adedi (örn: TEK GİRİŞ):", value="TEK GİRİŞ")
        kapi_model = st.text_input("Kapı Modeli (Kabin):", value="ÇARPMA")
        kat_kapi_adedi = st.text_input("Kat Kapı Adedi:", value="YOK")
        kat_kapi_model = st.text_input("Kat Kapı Modeli:", value="YOK")
        kapi_yon = st.text_input("Kapı Yönü:", value="ÇARPMA")
        kapi_kaplama = st.text_input("Kapı Kaplama:", value="YOK")
        kasa_kaplama = st.text_input("Kasa Kaplama:", value="YOK")
        panel_kaplama = st.text_input("Panel Kaplama:", value="YOK")
        kapi_not = st.text_input("Kapı Notu:", value="YOK")
         
        st.markdown("---")
        pano_adet = st.text_input("Pano Adet:", value="1")
        pano_guc = st.text_input("Pano Güç:", value="Standart")
        pano_tipi = st.text_input("Pano Tipi:", value="YOK")
        pano_surucu = st.text_input("Pano Sürücü:", value="YOK")
        pano_kart = st.text_input("Kumanda Kartı:", value="YOK")
        pano_salt = st.text_input("Şalt Malzeme:", value="YOK")
        pano_konum = st.text_input("Konum Yeri:", value="YOK")
        pano_not = st.text_input("Pano Notu:", value="YOK")
         
        st.markdown("---")
        st.subheader("📝 İmzalar ve Teslimat")
        musteri_temsilcisi = st.text_input("Müşteri Temsilcisi Adı Soyadı:", value=st.session_state.get("username", "Ahmet Bey"))
        imalat_muduru = st.text_input("İmalat Müdürü Adı Soyadı:", value="Mehmet Usta")
         
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tarih_kabin = st.text_input("Kabin Teslim Tarihi:", value="-")
            tarih_sase = st.text_input("Şase Teslim Tarihi:", value="-")
            tarih_kapilar = st.text_input("Kapılar Teslim Tarihi:", value="-")
            tarih_pano = st.text_input("Pano Teslim Tarihi:", value="-")
        with col_t2:
            desc_kabin = st.text_input("Kabin Açıklama:", value="-")
            desc_sase = st.text_input("Şase Açıklama:", value="-")
            desc_kapilar = st.text_input("Kapılar Açıklama:", value="-")
            desc_pano = st.text_input("Pano Açıklama:", value="-")
             
        genel_not = st.text_area("Özel Form Notu (Ortada Görünen):", value="HİDROLİK ASANSÖR SADECE KABİN KOVASI YAPILACAKTIR. 150 CM GENİŞLİK 85 CM DERİNLİK OLACAKTIR.")
 
    st.markdown("---")
    st.subheader("🖼️ Görsel Girişleri ve Alt Ölçü Bilgileri")
     
    col_img1, col_img2, col_img3, col_img4 = st.columns(4)
    with col_img1:
        st.markdown("**1. TABAN MODELİ**")
        file_taban = st.file_uploader("Taban Görseli:", type=["png", "jpg", "jpeg"], key="up_taban")
        dim_taban = st.text_input("Taban Ölçü Bilgisi:", value="Antibakteriyel Sunta", key="in_dim_taban")
    with col_img2:
        st.markdown("**2. KABİN MODELİ**")
        file_kabin = st.file_uploader("Kabin Görseli:", type=["png", "jpg", "jpeg"], key="up_kabin")
        dim_kabin = st.text_input("Kabin Ölçü Bilgisi (Genişlik x Derinlik):", value="150 X 85 cm", key="in_dim_kabin")
    with col_img3:
        st.markdown("**3. TAVAN MODELİ**")
        file_tavan = st.file_uploader("Tavan Görseli:", type=["png", "jpg", "jpeg"], key="up_tavan")
        dim_tavan = st.text_input("Tavan Ölçü Bilgisi:", value="T-189 Model", key="in_dim_tavan")
    with col_img4:
        st.markdown("**4. KUYU KESİTİ / ÖZEL ÇİZİM**")
        file_kuyu = st.file_uploader("Kuyu/Özel Görseli:", type=["png", "jpg", "jpeg"], key="up_kuyu")
        dim_kuyu = st.text_input("Kuyu Ölçü Bilgisi (Kuyu Genişlik x Derinlik):", value="170 X 124 cm", key="in_dim_kuyu")
 
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 İmalat Teklif Belgesi (PDF) Oluştur", use_container_width=True):
        images_paths = {}
        for k, f in [("taban", file_taban), ("kabin", file_kabin), ("tavan", file_tavan), ("kuyu", file_kuyu)]:
            if f:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(f.getvalue())
                    images_paths[k] = tmp.name
            else:
                images_paths[k] = None
                 
        # Parse Genişlik x Derinlik or details
        kabin_gen_der = f"{dim_kabin}"
         
        pdf_data = {
            "firma": firma,
            "referans": referans,
            "siparis_no": siparis_no,
            "teklif_no": teklif_no_form,
            "kapasite": kapasite,
            "hiz": hiz,
            "kabin_gen_der": kabin_gen_der,
            "seyir_detay": "0 / 0 / 0 mm",
            "durak": durak,
            "giris_sayisi": giris_sayisi,
            "aski_tipi": aski_tipi,
            "kuyu_tipi": kuyu_tipi,
            "ana_ray": ana_ray,
            "ana_ray_arasi": ana_ray_arasi,
            "kabin_modeli": kabin_modeli,
            "kabin_kaplama": kabin_kaplama,
            "doseme_tipi": doseme_tipi,
            "aksesuar_kaplama": aksesuar_kaplama,
            "kapi_giris_kaplama": kapi_giris_kaplama,
            "tavan_modeli": tavan_modeli,
            "taban_modeli": taban_modeli,
            "ayna_detay": ayna_detay,
            "sabitleme_kit": sabitleme_kit,
            "asiri_yuk": asiri_yuk,
            "not": genel_not,
            "dim_kabin": dim_kabin,
            "dim_kuyu": dim_kuyu,
            "agirlik_sasesi": agirlik_sasesi,
            "agirlik_ray_arasi": agirlik_ray_arasi,
            "agirlik_adet": agirlik_adet,
            "agirlik_ray_olcu": agirlik_ray_olcu,
            "makine_sasesi": makine_sasesi,
            "motor_marka": motor_marka,
            "kasnak_olculeri": kasnak_olculeri,
            "seperator": seperator,
            "kapi_gen_yuk": kapi_gen_yuk,
            "kabin_kapi_adedi": kabin_kapi_adedi,
            "kapi_model": kapi_model,
            "kat_kapi_adedi": kat_kapi_adedi,
            "kat_kapi_model": kat_kapi_model,
            "kapi_yon": kapi_yon,
            "kapi_kaplama": kapi_kaplama,
            "kasa_kaplama": kasa_kaplama,
            "panel_kaplama": panel_kaplama,
            "kapi_not": kapi_not,
            "pano_adet": pano_adet,
            "pano_guc": pano_guc,
            "pano_tipi": pano_tipi,
            "pano_surucu": pano_surucu,
            "pano_kart": pano_kart,
            "pano_salt": pano_salt,
            "pano_konum": pano_konum,
            "pano_not": pano_not,
            "musteri_temsilcisi": musteri_temsilcisi,
            "imalat_muduru": imalat_muduru,
            "tarih_kabin": tarih_kabin,
            "tarih_sase": tarih_sase,
            "tarih_kapi": tarih_kapilar,
            "tarih_pano": tarih_pano,
            "desc_kabin": desc_kabin,
            "desc_sase": desc_sase,
            "desc_kapi": desc_kapilar,
            "desc_pano": desc_pano
        }
         
        try:
            pdf_bytes_imalat = generate_asansor_imalat_pdf(pdf_data, images_paths)
            st.success("İmalat teklif formu başarıyla hazırlandı!")
             
            def clean_name_sb(t):
                if not t: return ""
                t = str(t)
                replacements = {'ı': 'i', 'İ': 'I', 'ş': 's', 'Ş': 'S', 'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'}
                for k, v in replacements.items(): t = t.replace(k, v)
                return t
                 
            st.download_button(
                label="📥 Resmi İmalat Teklif PDF Dosyasını İndir",
                data=pdf_bytes_imalat,
                file_name=f"Imalat_Teklif_{clean_name_sb(firma)}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF oluşturulurken bir hata oluştu: {e}")

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
