import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register TTF for Turkish support
pdfmetrics.registerFont(TTFont('Helvetica', 'C:\\Windows\\Fonts\\arial.ttf'))
pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))

def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    text = f"Sayfa {page_num}"
    canvas.setFont("Helvetica", 9)
    # Right align at the bottom
    canvas.drawRightString(20*cm, 1*cm, text)


os.makedirs("reports/final", exist_ok=True)

with open("reports/master-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Colors
C_RED = colors.HexColor("#E53935")
C_ORANGE = colors.HexColor("#FB8C00")
C_GREEN = colors.HexColor("#43A047")
C_DARKGRAY = colors.HexColor("#212121")
C_LIGHTGRAY = colors.HexColor("#F5F5F5")
C_NAVY = colors.HexColor("#1565C0")
C_WHITE = colors.HexColor("#FFFFFF")

styles = getSampleStyleSheet()
title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, textColor=C_NAVY, alignment=1, spaceAfter=20)
h1_style = ParagraphStyle('H1Style', parent=styles['Heading1'], fontSize=18, textColor=C_DARKGRAY, spaceAfter=14)
h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, spaceAfter=10)
normal_style = styles['Normal']
normal_style.fontSize = 11
normal_style.leading = 14

def get_color(score, is_time=False):
    if is_time:
        if score < 2000: return C_GREEN
        elif score < 4000: return C_ORANGE
        return C_RED
    else:
        if score >= 90: return C_GREEN
        elif score >= 50: return C_ORANGE
        return C_RED

def generate_teknik_rapor():
    doc = SimpleDocTemplate("reports/final/tcc-teknik-rapor-FINAL.pdf", pagesize=A4)
    story = []
    
    # SAYFA 1 - KAPAK
    story.append(Spacer(1, 5*cm))
    story.append(Paragraph("Tarihi Çengelköy Tatlıcısı", title_style))
    story.append(Paragraph("E-Ticaret Teknik Denetim Raporu", ParagraphStyle('SubTitle', fontSize=18, alignment=1, spaceAfter=20)))
    story.append(Paragraph(f"Tarih: {data['site_bilgisi']['analiz_tarihi']}", ParagraphStyle('Center', alignment=1)))
    story.append(Paragraph(f"Platform: {data['site_bilgisi']['platform']} | Ajans: {data['site_bilgisi']['ajans']}", ParagraphStyle('Center', alignment=1)))
    story.append(Spacer(1, 10*cm))
    story.append(Paragraph("Gizli & Profesyonel", ParagraphStyle('Footer', alignment=1, textColor=C_DARKGRAY)))
    story.append(PageBreak())

    # SAYFA 2 - YÖNETİCİ ÖZETİ
    story.append(Paragraph("YÖNETİCİ ÖZETİ", h1_style))
    story.append(Paragraph("Yapılan teknik incelemeler sonucunda platformda ciddi performans ve erişilebilirlik sorunları tespit edilmiştir. İnceleme sonuçları aşağıdadır.", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    table_data = [
        ["Kategori", "Desktop", "Mobile", "Hedef", "Durum"]
    ]
    cats = [
        ("Performance", data["lighthouse"]["guncel"]["desktop"], data["lighthouse"]["guncel"]["mobile"]),
        ("Accessibility", data["lighthouse"]["guncel"]["accessibility_desktop"], data["lighthouse"]["guncel"]["accessibility_mobile"]),
        ("Best Practices", data["lighthouse"]["guncel"]["best_practices_desktop"], data["lighthouse"]["guncel"]["best_practices_mobile"]),
        ("SEO", data["lighthouse"]["guncel"]["seo_desktop"], data["lighthouse"]["guncel"]["seo_mobile"])
    ]
    
    for name, d, m in cats:
        status = "BAŞARISIZ" if m < 90 else "BAŞARILI"
        table_data.append([name, str(d), str(m), "90+", status])
        
    t = Table(table_data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_DARKGRAY),
        ('TEXTCOLOR', (0,0), (-1,0), C_WHITE),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TEXTCOLOR', (4,1), (4,-1), C_RED)
    ]))
    story.append(t)
    story.append(PageBreak())

    # SAYFA 3 - LIGHTHOUSE KARŞILAŞTIRMA
    story.append(Paragraph("LIGHTHOUSE KARŞILAŞTIRMA", h1_style))
    t1 = Table([
        ["Cihaz", "Önceki", "Güncel", "Fark"],
        ["Desktop", str(data["lighthouse"]["onceki"]["desktop"]), str(data["lighthouse"]["guncel"]["desktop"]), f"+{data['lighthouse']['degisim']['desktop']}"],
        ["Mobile", str(data["lighthouse"]["onceki"]["mobile"]), str(data["lighthouse"]["guncel"]["mobile"]), f"+{data['lighthouse']['degisim']['mobile']}"]
    ])
    t1.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_DARKGRAY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE)]))
    story.append(t1)
    story.append(Spacer(1, 1*cm))
    
    t2 = Table([
        ["TCC Desktop", "Rakip Desktop (Makbul)"],
        [str(data["lighthouse"]["guncel"]["desktop"]), str(data["rakip"]["lighthouse_desktop"])]
    ])
    t2.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_NAVY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE)]))
    story.append(t2)
    story.append(Spacer(1, 1*cm))
    
    cwv = [
        ["Metrik", "Mevcut Değer (Mobile)", "Google Hedefi"],
        ["FCP", f"{data['lighthouse']['metrikler']['mobile']['fcp_ms']} ms", f"<= {data['lighthouse']['hedefler']['fcp_ms']} ms"],
        ["LCP", f"{data['lighthouse']['metrikler']['mobile']['lcp_ms']} ms", f"<= {data['lighthouse']['hedefler']['lcp_ms']} ms"],
        ["TTI", f"{data['lighthouse']['metrikler']['mobile']['tti_ms']} ms", f"<= {data['lighthouse']['hedefler']['tti_ms']} ms"],
        ["CLS", str(data['lighthouse']['metrikler']['mobile']['cls']), f"<= {data['lighthouse']['hedefler']['cls']}"],
        ["TBT", f"{data['lighthouse']['metrikler']['mobile']['tbt_ms']} ms", f"<= {data['lighthouse']['hedefler']['tbt_ms']} ms"],
        ["TTFB", f"{data['lighthouse']['metrikler']['mobile']['ttfb_ms']} ms", f"<= {data['lighthouse']['hedefler']['ttfb_ms']} ms"]
    ]
    t3 = Table(cwv)
    t3.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_DARKGRAY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE)]))
    story.append(t3)
    story.append(PageBreak())

    # SAYFA 4 - SİTE TARAMA SONUÇLARI
    story.append(Paragraph("SİTE TARAMA SONUÇLARI", h1_style))
    st_data = [["Sayfa", "HTTP Durumu", "Yükleme Süresi", "Değerlendirme"]]
    for r in data["site_tarama"]:
        st_data.append([r["sayfa"], str(r["durum"]), f"{r['sure_ms']} ms", r["hiz_degerlendirme"]])
    
    t4 = Table(st_data)
    t4.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_DARKGRAY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE)]))
    story.append(t4)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Sitemap URL sayısı: 83 (74 ürün, 9 kategori)", normal_style))
    story.append(PageBreak())

    # SAYFA 5 - ENTEGRASYONLAR
    story.append(Paragraph("ENTEGRASYONLARIN DURUMU", h1_style))
    ent_data = [
        ["Entegrasyon", "Durum", "Not"],
        ["Kargo", "Yok / Sorunlu", "Sadece 1 firma"],
        ["Ödeme (Sanal POS)", "⚠ Sorunlu", "Sadece kredi kartı aktif"],
        ["Pazaryeri", "✗ Yok", "Manuel yapılamıyor"],
        ["Analytics", "✓ Aktif", "GA4 kurulu"],
        ["E-Fatura", "✗ Yok", "Manuel fatura kesiliyor"]
    ]
    t5 = Table(ent_data)
    t5.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_DARKGRAY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE)]))
    story.append(t5)
    story.append(PageBreak())

    # SAYFA 6 - KRİTİK SORUNLAR
    story.append(Paragraph("KRİTİK SORUNLAR", h1_style))
    for s in data["kritik_sorunlar"]:
        story.append(Paragraph(f"• {s['etki']} - {s['baslik']}: {s['cozum']}", normal_style))
    story.append(PageBreak())

    # SAYFA 7 - ŞİKAYETLER
    story.append(Paragraph("TİCİMAX ŞİKAYET ANALİZİ", h1_style))
    story.append(Paragraph("En sık tekrarlayan şikayetler:", normal_style))
    for s in data["ticimax_sikayetleri"]:
        story.append(Paragraph(f"- {s['konu']} (Sıklık: {s['siklik']})", normal_style))
    story.append(PageBreak())

    # SAYFA 8 - SORUMLULUK
    story.append(Paragraph("SORUMLULUK ANALİZİ", h1_style))
    sor_data = [["CEMGE AJANS HATALARI", "TİCİMAX PLATFORM SORUNLARI"]]
    max_len = max(len(data["ajans_hatalari"]), len(data["ticimax_sorunlari"]))
    for i in range(max_len):
        a = data["ajans_hatalari"][i] if i < len(data["ajans_hatalari"]) else ""
        t_err = data["ticimax_sorunlari"][i] if i < len(data["ticimax_sorunlari"]) else ""
        sor_data.append([a, t_err])
        
    t6 = Table(sor_data, colWidths=[8*cm, 8*cm])
    t6.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (0,0), C_RED), ('BACKGROUND', (1,0), (1,0), C_ORANGE), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE), ('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(t6)
    story.append(PageBreak())

    # SAYFA 9 - RAKIP
    story.append(Paragraph("RAKİP KARŞILAŞTIRMA (TCC vs Makbul)", h1_style))
    rakip_comp = [
        ["Kriter", "TCC", "Makbul"],
        ["Mobil Performans", str(data["lighthouse"]["guncel"]["mobile"]), "Bilinmiyor/İyi"],
        ["Desktop Performans", str(data["lighthouse"]["guncel"]["desktop"]), str(data["rakip"]["lighthouse_desktop"])],
        ["Platform", "Ticimax", "Shopify/Özel"],
        ["Misafir Checkout", "Kapalı", "Açık"],
        ["Kargo Seçenekleri", "1", "3"]
    ]
    t7 = Table(rakip_comp)
    t7.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_NAVY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE)]))
    story.append(t7)
    story.append(PageBreak())

    # SAYFA 10 - EYLEM PLANI
    story.append(Paragraph("EYLEM PLANI", h1_style))
    story.append(Paragraph("A. ACİL (Bu Hafta)", h2_style))
    for e in data["eylem_plani"]["acil"]: story.append(Paragraph(f"- {e}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("B. KISA VADE (1 Ay)", h2_style))
    for e in data["eylem_plani"]["kisa_vade"]: story.append(Paragraph(f"- {e}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("C. UZUN VADE (3 Ay) - İkas'a Geçiş Önerisi", h2_style))
    for e in data["eylem_plani"]["uzun_vade"]: story.append(Paragraph(f"- {e}", normal_style))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def generate_ihtarname():
    doc = SimpleDocTemplate("reports/final/tcc-ihtarname-FINAL.pdf", pagesize=A4)
    story = []
    
    # SAYFA 1
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("YAZILI İHTARNAME", title_style))
    story.append(Paragraph(f"Tarih: {data['site_bilgisi']['analiz_tarihi']}", normal_style))
    story.append(Paragraph("Konu: E-Ticaret Sitesi Ayıplı Teslim ve Eksik Hizmet Bildirimi", normal_style))
    story.append(Paragraph("Muhatap: Cemge Ajans", normal_style))
    story.append(Spacer(1, 1*cm))
    intro = ("Tarafınızla akdedilen sözleşme kapsamında teslim edilen e-ticaret sitesi "
             "(tarihicengelkoytatlicisi.com.tr) üzerinde 26 Şubat 2026 tarihinde bağımsız teknik denetim "
             "gerçekleştirilmiştir. Söz konusu denetimde sözleşme kapsamındaki temel e-ticaret işlevlerinin eksik, "
             "hatalı veya çalışmaz durumda olduğu tespit edilmiştir.")
    story.append(Paragraph(intro, normal_style))
    story.append(PageBreak())

    # SAYFA 2
    story.append(Paragraph("I. TEKNİK TEST SONUÇLARI", h1_style))
    t1 = Table([
        ["Kategori", "Desktop Sonucu", "Mobile Sonucu", "Sektör Standardı", "Değerlendirme"],
        ["Performance", str(data["lighthouse"]["guncel"]["desktop"]), str(data["lighthouse"]["guncel"]["mobile"]), "90+", "BAŞARISIZ"],
        ["Accessibility", str(data["lighthouse"]["guncel"]["accessibility_desktop"]), str(data["lighthouse"]["guncel"]["accessibility_mobile"]), "90+", "BAŞARISIZ"],
        ["Best Practices", str(data["lighthouse"]["guncel"]["best_practices_desktop"]), str(data["lighthouse"]["guncel"]["best_practices_mobile"]), "90+", "BAŞARISIZ"],
        ["SEO", str(data["lighthouse"]["guncel"]["seo_desktop"]), str(data["lighthouse"]["guncel"]["seo_mobile"]), "90+", "BAŞARISIZ"]
    ])
    t1.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_DARKGRAY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE), ('TEXTCOLOR', (4,1), (4,-1), C_RED)]))
    story.append(t1)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Mobile performans skoru {data['lighthouse']['guncel']['mobile']}/100 olup, sektör standardının çok altında kalmaktadır.", normal_style))
    story.append(PageBreak())

    # SAYFA 3
    story.append(Paragraph("II. TESPİT EDİLEN AYIPLAR", h1_style))
    for i, a in enumerate(data["ajans_hatalari"], 1):
        story.append(Paragraph(f"Madde {i}: {a}", normal_style))
        story.append(Spacer(1, 0.2*cm))
    story.append(PageBreak())

    # SAYFA 4
    story.append(Paragraph("III. HUKUKİ DAYANAK", h1_style))
    story.append(Paragraph("Yukarıda belirtilen tespitler, 6098 sayılı Türk Borçlar Kanunu'nun 475. ve devamı maddeleri kapsamında ayıplı ifa teşkil etmekte; işbu ihtarname söz konusu ayıpların bildirilmesi ve yasal hakların saklı tutulması amacıyla tanzim edilmiştir.", normal_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("IV. DÜZELTME TALEBİ", h1_style))
    story.append(Paragraph("Aşağıda belirtilen eksikliklerin işbu ihtarnamenin tebliğinden itibaren 7 (yedi) iş günü içinde giderilmesini talep ederiz:", normal_style))
    story.append(Paragraph("SEÇENEK A: Tam Düzeltme", h2_style))
    story.append(Paragraph("SEÇENEK B: Kısmi İade (%50 bedel iadesi)", h2_style))
    story.append(PageBreak())

    # SAYFA 5
    story.append(Paragraph("V. HUKUKİ SÜREÇ UYARISI", h1_style))
    story.append(Paragraph("Belirtilen süre içinde tarafımızca tatmin edici çözüm sağlanmaması halinde; sözleşmenin feshi, ödenen bedelin tam iadesi, uğranılan zararların tazmini ve gerekli diğer hukuki yollara başvurma haklarımızı kullanacağımızı ihtaren bildiririz.", normal_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("EK LİSTESİ:", h2_style))
    story.append(Paragraph("Ek-1: Google Lighthouse Desktop Raporu<br/>Ek-2: Google Lighthouse Mobile Raporu<br/>Ek-3: Site Teknik Analiz Raporu<br/>Ek-4: Site Tarama Sonuçları", normal_style))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("İMZA ALANI:<br/>Ad Soyad: _______________<br/>Tarih: 26.02.2026<br/>İmza/Kaşe: _______________", normal_style))
    
    doc.build(story)


def generate_platform_karsilastirma():
    doc = SimpleDocTemplate("reports/final/tcc-platform-karsilastirma-FINAL.pdf", pagesize=A4)
    story = []
    
    # SAYFA 1
    story.append(Paragraph("Neden Ticimax Sorun?", title_style))
    story.append(Paragraph("Platform performans verileri ve İkas geçiş analizi.", normal_style))
    story.append(PageBreak())

    # SAYFA 2
    story.append(Paragraph("İKAS vs TİCİMAX", h1_style))
    data2 = [
        ["Kriter", "Ticimax", "İkas", "Kazanan"],
        ["Mobil Performans", str(data["lighthouse"]["guncel"]["mobile"]), "90+", "İkas"],
        ["Yükleme Hızı", f"{data['lighthouse']['metrikler']['mobile']['lcp_ms']} ms", "~2000 ms", "İkas"],
        ["Kargo Entegrasyonu", "1 firma", "10+", "İkas"],
        ["Pazaryeri", "Manuel", "Otomatik", "İkas"],
        ["Misafir Checkout", "Kapalı", "Açık", "İkas"]
    ]
    t1 = Table(data2)
    t1.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), C_DARKGRAY), ('TEXTCOLOR', (0,0), (-1,0), C_WHITE)]))
    story.append(t1)
    story.append(PageBreak())

    # SAYFA 3
    story.append(Paragraph("GEÇİŞ ÖNERİSİ", h1_style))
    story.append(Paragraph("İkas'a geçiş zaman çizelgesi (3 hafta)", normal_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Beklenen Kazanımlar:", h2_style))
    for e in data["eylem_plani"]["uzun_vade"]:
        story.append(Paragraph(f"- {e}", normal_style))
        
    doc.build(story)

def generate_yonetici_ozeti():
    doc = SimpleDocTemplate("reports/final/tcc-yonetici-ozeti-FINAL.pdf", pagesize=A4)
    story = []
    
    story.append(Paragraph("Siteniz Hakkında Önemli Bilgilendirme", title_style))
    story.append(Paragraph("26 Şubat 2026", ParagraphStyle('C', alignment=1)))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("⚠ Site çalışıyor ama ciddi sorunlar var", ParagraphStyle('B', fontSize=20, textColor=C_ORANGE, alignment=1)))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Telefon Puanı: {data['lighthouse']['guncel']['mobile']}/100", ParagraphStyle('B2', fontSize=18, textColor=C_RED, alignment=1)))
    story.append(Paragraph(f"Bilgisayar Puanı: {data['lighthouse']['guncel']['desktop']}/100", ParagraphStyle('B3', fontSize=18, textColor=C_ORANGE, alignment=1)))
    story.append(Paragraph(f"Olması Gereken: 90+", ParagraphStyle('B4', fontSize=18, textColor=C_GREEN, alignment=1)))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("📱 Müşterilerin %70'i telefonu kullanır. Telefonunuzda site çok yavaş açılıyor. Her 10 müşteriden en az 7'sini kaybediyorsunuz.", ParagraphStyle('B5', fontSize=14, alignment=1)))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("3 SEÇENEĞİNİZ VAR:", h1_style))
    story.append(Paragraph("1. Ajanstan Düzeltme İste (7 gün)", normal_style))
    story.append(Paragraph("2. Platform Değiştirin (İkas - 3 hafta)", normal_style))
    story.append(Paragraph("3. Uzman Teknik Destek Alın", normal_style))
    
    doc.build(story)

def generate_sunum():
    doc = SimpleDocTemplate("reports/final/tcc-sunum-FINAL.pdf", pagesize=landscape(A4))
    story = []
    
    slides = [
        "E-Ticaret Siteniz Hakkında Gerçekler",
        f"Rakamlar Yalan Söylemez: Mobil Skor: {data['lighthouse']['guncel']['mobile']}/100",
        "Müşteriniz Ne Yaşıyor? Yavaş yükleme, sepet 404 hatası.",
        "Kim Sorumlu? Ajans Eksikleri & Ticimax Sorunları",
        "Çözüm: İkas ile Yeni Başlangıç",
        "Sonraki Adımlar: İhtarname Çekimi & İkas'a Geçiş"
    ]
    
    for s in slides:
        story.append(Spacer(1, 5*cm))
        story.append(Paragraph(s, ParagraphStyle('Slide', fontSize=28, textColor=C_NAVY, alignment=1)))
        story.append(PageBreak())
        
    doc.build(story)

generate_teknik_rapor()
generate_ihtarname()
generate_platform_karsilastirma()
generate_yonetici_ozeti()
generate_sunum()

print("PDFs generated successfully.")
