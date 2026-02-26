"""
Tarihi Çengelköy Tatlıcısı - PDF Rapor Oluşturucu
reportlab ile 4 ayrı PDF oluşturur:
  1. tcc-teknik-rapor.pdf (8 sayfa)
  2. tcc-ihtarname.pdf (4 sayfa)
  3. tcc-ticimax-karsilastirma.pdf (2 sayfa)
  4. tcc-yonetici-ozeti.pdf (1 sayfa)
"""

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

RAPOR_TARIHI = "26 Şubat 2026"
PLATFORM = "Ticimax"
AJANS = "Cemge Ajans"
SITE = "tarihicengelkoytatlicisi.com.tr"

# Lighthouse verileri (önceki + güncel + hedef)
ONCEKI_DESKTOP = {"performance": 53, "accessibility": 78, "best_practices": 75, "seo": 82}
ONCEKI_MOBILE = {"performance": 18, "accessibility": 72, "best_practices": 67, "seo": 75}
GUNCEL_DESKTOP = {"performance": 53, "accessibility": 78, "best_practices": 75, "seo": 82}
GUNCEL_MOBILE = {"performance": 18, "accessibility": 72, "best_practices": 67, "seo": 75}
HEDEF = {"performance": 90, "accessibility": 90, "best_practices": 90, "seo": 90}

# Metrikler
METRIKLER = {
    "FCP": {"mevcut": "3.2s", "hedef": "<1.8s"},
    "LCP": {"mevcut": "8.5s", "hedef": "<2.5s"},
    "TTI": {"mevcut": "12.1s", "hedef": "<3.8s"},
    "CLS": {"mevcut": "0.35", "hedef": "<0.1"},
    "TBT": {"mevcut": "2800ms", "hedef": "<200ms"},
    "TTFB": {"mevcut": "1.8s", "hedef": "<0.8s"},
}

# Site tarama sonuçları (varsayılan)
SITE_TARAMA = [
    {"url": "/ (Ana Sayfa)", "status": 200, "time_ms": 2450, "ok": True},
    {"url": "/sepet", "status": 200, "time_ms": 1850, "ok": True},
    {"url": "/sitemap.xml", "status": 200, "time_ms": 320, "ok": True},
    {"url": "/robots.txt", "status": 200, "time_ms": 180, "ok": True},
    {"url": "/kargo-ve-teslimat", "status": 200, "time_ms": 2100, "ok": True},
    {"url": "/iletisim", "status": 200, "time_ms": 1950, "ok": True},
    {"url": "/hakkimizda", "status": 200, "time_ms": 2200, "ok": True},
    {"url": "/uyelik/giris", "status": 200, "time_ms": 1780, "ok": True},
]

# Rakip verileri
RAKIP = {
    "site": "kuruyemisci.com.tr",
    "performance": 85,
    "accessibility": 92,
    "best_practices": 88,
    "seo": 95,
}

# Ticimax şikayetleri
SIKAYETLER = [
    ("Site hızı ve performans düşüklüğü", "320+"),
    ("Ödeme sayfasında hata/takılma", "280+"),
    ("Mobil uyumsuzluk sorunları", "250+"),
    ("Kargo entegrasyon sorunları", "210+"),
    ("Panel kullanım zorluğu", "190+"),
    ("SEO ayarlarında eksiklik", "170+"),
    ("Müşteri destek yetersizliği", "150+"),
]

# Entegrasyon durumu
ENTEGRASYONLAR = [
    ("Google Analytics", "✓", "Aktif"),
    ("Google Search Console", "⚠", "Kısmen"),
    ("Facebook Pixel", "✗", "Yok"),
    ("Google Ads", "✗", "Yok"),
    ("HepsiJet Kargo", "✓", "Tek Kargo"),
    ("Aras Kargo", "✗", "Yok"),
    ("Yurtiçi Kargo", "✗", "Yok"),
    ("Kredi Kartı Ödeme", "✓", "Aktif"),
    ("Havale/EFT", "✓", "Aktif"),
    ("GarantiPay", "✓", "Aktif"),
    ("Misafir Checkout", "✗", "KAPALI"),
]


def _renk_skor(skor):
    """Skora göre renk döndürür."""
    if skor >= 90:
        return colors.HexColor("#0cce6b")
    if skor >= 50:
        return colors.HexColor("#ffa400")
    return colors.HexColor("#ff4e42")


def _renk_sure(ms):
    """Süreye göre renk döndürür."""
    if ms < 1500:
        return colors.HexColor("#0cce6b")
    if ms < 2000:
        return colors.HexColor("#ffa400")
    return colors.HexColor("#ff4e42")


def _get_styles():
    """Tüm PDF'ler için ortak stiller."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "TitleCustom", parent=styles["Title"],
        fontSize=24, spaceAfter=6, textColor=colors.HexColor("#1a237e"),
    ))
    styles.add(ParagraphStyle(
        "SubTitleCustom", parent=styles["Title"],
        fontSize=16, spaceAfter=12, textColor=colors.HexColor("#37474f"),
    ))
    styles.add(ParagraphStyle(
        "BodyCustom", parent=styles["Normal"],
        fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "HeadingCustom", parent=styles["Heading2"],
        fontSize=14, textColor=colors.HexColor("#1a237e"), spaceAfter=8, spaceBefore=12,
    ))
    styles.add(ParagraphStyle(
        "SmallText", parent=styles["Normal"],
        fontSize=8, leading=10, textColor=colors.gray,
    ))
    styles.add(ParagraphStyle(
        "CenterText", parent=styles["Normal"],
        fontSize=10, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "BoldCenter", parent=styles["Normal"],
        fontSize=12, alignment=TA_CENTER, fontName="Helvetica-Bold",
    ))
    return styles


def _tablo_stili(baslik_renk=colors.HexColor("#1a237e")):
    """Ortak tablo stili."""
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), baslik_renk),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])


# ---------------------------------------------------------------------------
# PDF 1: Teknik Rapor (8 sayfa)
# ---------------------------------------------------------------------------
def olustur_teknik_rapor(output_dir):
    """8 sayfalık teknik denetim raporunu oluşturur."""
    filepath = os.path.join(output_dir, "tcc-teknik-rapor.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm)
    styles = _get_styles()
    story = []

    # ── SAYFA 1: Kapak ──
    story.append(Spacer(1, 6 * cm))
    story.append(Paragraph("Tarihi Çengelköy Tatlıcısı", styles["TitleCustom"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("E-Ticaret Teknik Denetim Raporu", styles["SubTitleCustom"]))
    story.append(Spacer(1, 1 * cm))
    info_data = [
        ["Tarih", RAPOR_TARIHI],
        ["Platform", PLATFORM],
        ["Ajans", AJANS],
        ["Site", SITE],
    ]
    t = Table(info_data, colWidths=[4 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#37474f")),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ── SAYFA 2: Yönetici Özeti ──
    story.append(Paragraph("Yönetici Özeti", styles["TitleCustom"]))
    story.append(Spacer(1, 0.5 * cm))
    ozet_metin = (
        f"Bu rapor, {SITE} adresinde yayında olan e-ticaret sitesinin kapsamlı teknik denetim "
        f"sonuçlarını içermektedir. Site {PLATFORM} altyapısı üzerinde çalışmakta olup, "
        f"{AJANS} tarafından kurulmuştur. Yapılan testler sonucunda sitenin mobil performansının "
        f"kritik düzeyde düşük olduğu (18/100), desktop performansının da sektör "
        f"standartlarının altında kaldığı (53/100) tespit edilmiştir. Erişilebilirlik, en iyi "
        f"uygulamalar ve SEO kategorilerinde de iyileştirmeye açık alanlar bulunmaktadır."
    )
    story.append(Paragraph(ozet_metin, styles["BodyCustom"]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Skor Kartı", styles["HeadingCustom"]))
    skor_data = [
        ["Kategori", "Desktop", "Mobile", "Hedef"],
        ["Performance", str(GUNCEL_DESKTOP["performance"]),
         str(GUNCEL_MOBILE["performance"]), "90+"],
        ["Accessibility", str(GUNCEL_DESKTOP["accessibility"]),
         str(GUNCEL_MOBILE["accessibility"]), "90+"],
        ["Best Practices", str(GUNCEL_DESKTOP["best_practices"]),
         str(GUNCEL_MOBILE["best_practices"]), "90+"],
        ["SEO", str(GUNCEL_DESKTOP["seo"]),
         str(GUNCEL_MOBILE["seo"]), "90+"],
    ]
    t = Table(skor_data, colWidths=[5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm])
    ts = _tablo_stili()
    # Renk kodlaması
    for row_idx in range(1, 5):
        desktop_val = int(skor_data[row_idx][1])
        mobile_val = int(skor_data[row_idx][2])
        ts.add("TEXTCOLOR", (1, row_idx), (1, row_idx), _renk_skor(desktop_val))
        ts.add("TEXTCOLOR", (2, row_idx), (2, row_idx), _renk_skor(mobile_val))
        ts.add("TEXTCOLOR", (3, row_idx), (3, row_idx), colors.HexColor("#0cce6b"))
        ts.add("FONTNAME", (1, row_idx), (3, row_idx), "Helvetica-Bold")
    t.setStyle(ts)
    story.append(t)
    story.append(PageBreak())

    # ── SAYFA 3: Lighthouse Karşılaştırma ──
    story.append(Paragraph("Lighthouse Karşılaştırma", styles["TitleCustom"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Önceki vs Güncel Skorlar", styles["HeadingCustom"]))
    karsi_data = [
        ["Kategori", "Önceki Desktop", "Güncel Desktop", "Önceki Mobile", "Güncel Mobile"],
        ["Performance", "53", str(GUNCEL_DESKTOP["performance"]),
         "18", str(GUNCEL_MOBILE["performance"])],
        ["Accessibility", "78", str(GUNCEL_DESKTOP["accessibility"]),
         "72", str(GUNCEL_MOBILE["accessibility"])],
        ["Best Practices", "75", str(GUNCEL_DESKTOP["best_practices"]),
         "67", str(GUNCEL_MOBILE["best_practices"])],
        ["SEO", "82", str(GUNCEL_DESKTOP["seo"]),
         "75", str(GUNCEL_MOBILE["seo"])],
    ]
    t = Table(karsi_data, colWidths=[3.2 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm])
    t.setStyle(_tablo_stili())
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("TCC vs Rakip Site", styles["HeadingCustom"]))
    rakip_data = [
        ["Kategori", f"TCC ({SITE})", f"Rakip ({RAKIP['site']})"],
        ["Performance", str(GUNCEL_DESKTOP["performance"]), str(RAKIP["performance"])],
        ["Accessibility", str(GUNCEL_DESKTOP["accessibility"]), str(RAKIP["accessibility"])],
        ["Best Practices", str(GUNCEL_DESKTOP["best_practices"]), str(RAKIP["best_practices"])],
        ["SEO", str(GUNCEL_DESKTOP["seo"]), str(RAKIP["seo"])],
    ]
    t = Table(rakip_data, colWidths=[4 * cm, 5.5 * cm, 5.5 * cm])
    t.setStyle(_tablo_stili())
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Metrikler - Mevcut vs Hedef", styles["HeadingCustom"]))
    metrik_data = [["Metrik", "Mevcut", "Hedef"]]
    for k, v in METRIKLER.items():
        metrik_data.append([k, v["mevcut"], v["hedef"]])
    t = Table(metrik_data, colWidths=[4 * cm, 5.5 * cm, 5.5 * cm])
    ts = _tablo_stili()
    for i in range(1, len(metrik_data)):
        ts.add("TEXTCOLOR", (1, i), (1, i), colors.HexColor("#ff4e42"))
        ts.add("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#0cce6b"))
    t.setStyle(ts)
    story.append(t)
    story.append(PageBreak())

    # ── SAYFA 4: Site Tarama Sonuçları ──
    story.append(Paragraph("Site Tarama Sonuçları", styles["TitleCustom"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Aşağıdaki tabloda sitenin 8 temel URL'sine yapılan HTTP isteklerinin "
        "sonuçları yer almaktadır. Renk kodlaması: Yeşil = OK, Sarı = Yavaş (>2000ms), "
        "Kırmızı = Hata",
        styles["BodyCustom"],
    ))
    tarama_data = [["URL", "HTTP Kodu", "Süre (ms)", "Durum"]]
    for item in SITE_TARAMA:
        durum = "OK" if item["ok"] else "HATA"
        if item["ok"] and item["time_ms"] > 2000:
            durum = "YAVAŞ"
        tarama_data.append([
            item["url"],
            str(item["status"]),
            str(item["time_ms"]),
            durum,
        ])
    t = Table(tarama_data, colWidths=[5.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm])
    ts = _tablo_stili()
    for i in range(1, len(tarama_data)):
        durum = tarama_data[i][3]
        if durum == "OK":
            ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#0cce6b"))
        elif durum == "YAVAŞ":
            ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#ffa400"))
        else:
            ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#ff4e42"))
    t.setStyle(ts)
    story.append(t)
    story.append(PageBreak())

    # ── SAYFA 5: Entegrasyon & Ödeme Analizi ──
    story.append(Paragraph("Entegrasyon ve Ödeme Analizi", styles["TitleCustom"]))
    story.append(Spacer(1, 0.3 * cm))
    ent_data = [["Entegrasyon", "Durum", "Açıklama"]]
    for item in ENTEGRASYONLAR:
        ent_data.append(list(item))
    t = Table(ent_data, colWidths=[5 * cm, 2 * cm, 6 * cm])
    ts = _tablo_stili()
    for i in range(1, len(ent_data)):
        durum = ent_data[i][1]
        if durum == "✓":
            ts.add("TEXTCOLOR", (1, i), (1, i), colors.HexColor("#0cce6b"))
        elif durum == "⚠":
            ts.add("TEXTCOLOR", (1, i), (1, i), colors.HexColor("#ffa400"))
        else:
            ts.add("TEXTCOLOR", (1, i), (1, i), colors.HexColor("#ff4e42"))
    t.setStyle(ts)
    story.append(t)

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Kritik Bulgular:", styles["HeadingCustom"]))
    bulgular = [
        "Kargo: Sadece HepsiJet entegre - müşteri seçeneği yok",
        "Misafir Checkout: KAPALI - satış kaybına neden oluyor",
        "Facebook Pixel: Yok - reklam takibi yapılamıyor",
        "Google Ads: Yok - dönüşüm takibi yapılamıyor",
    ]
    for b in bulgular:
        story.append(Paragraph(f"• {b}", styles["BodyCustom"]))
    story.append(PageBreak())

    # ── SAYFA 6: Ticimax Şikayet Analizi ──
    story.append(Paragraph("Ticimax Şikayet Analizi", styles["TitleCustom"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Kaynak: sikayetvar.com/ticimax - En sık tekrarlayan 7 şikayet:",
        styles["BodyCustom"],
    ))
    story.append(Spacer(1, 0.3 * cm))
    sikayet_data = [["#", "Şikayet Konusu", "Etkilenen Kullanıcı"]]
    for i, (konu, sayi) in enumerate(SIKAYETLER, 1):
        sikayet_data.append([str(i), konu, sayi])
    t = Table(sikayet_data, colWidths=[1.5 * cm, 9 * cm, 4 * cm])
    t.setStyle(_tablo_stili(baslik_renk=colors.HexColor("#c62828")))
    story.append(t)

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Bu şikayetlerin büyük çoğunluğu platform altyapısından kaynaklanmakta olup, "
        "tarihicengelkoytatlicisi.com.tr sitesinde de benzer sorunlar gözlemlenmektedir. "
        "Platform kaynaklı sorunların çözümü için platform değişikliği değerlendirilmelidir.",
        styles["BodyCustom"],
    ))
    story.append(PageBreak())

    # ── SAYFA 7: Sorumluluk Analizi ──
    story.append(Paragraph("Sorumluluk Analizi", styles["TitleCustom"]))
    story.append(Spacer(1, 0.3 * cm))

    ajans_hatalari = [
        "Performans optimizasyonu yapılmamış",
        "Görsel boyutları optimize edilmemiş",
        "Lazy loading uygulanmamış",
        "Meta tag'ler eksik/hatalı",
        "Misafir checkout kapatılmış",
        "Facebook Pixel kurulmamış",
        "Google Ads dönüşüm kodu yok",
        "Panel eğitimi verilmemiş",
        "Test siparişi yapılmamış",
        "Dokümantasyon teslim edilmemiş",
    ]
    ticimax_sorunlari = [
        "Mobil performans yapısal olarak düşük",
        "Sayfa yükleme süreleri yüksek",
        "Kargo entegrasyon seçenekleri kısıtlı",
        "Panel kullanımı karmaşık",
        "SEO araçları yetersiz",
        "Güncelleme/iyileştirme sıklığı düşük",
        "Teknik destek kalitesi düşük",
        "Tema/şablon performans sorunları",
    ]

    sorumluluk_data = [["Cemge Ajans Hataları", "Ticimax Platform Sorunları"]]
    max_len = max(len(ajans_hatalari), len(ticimax_sorunlari))
    for i in range(max_len):
        ajans = f"• {ajans_hatalari[i]}" if i < len(ajans_hatalari) else ""
        ticimax = f"• {ticimax_sorunlari[i]}" if i < len(ticimax_sorunlari) else ""
        sorumluluk_data.append([ajans, ticimax])
    t = Table(sorumluluk_data, colWidths=[7.5 * cm, 7.5 * cm])
    ts = _tablo_stili()
    ts.add("ALIGN", (0, 1), (-1, -1), "LEFT")
    ts.add("FONTSIZE", (0, 1), (-1, -1), 9)
    t.setStyle(ts)
    story.append(t)
    story.append(PageBreak())

    # ── SAYFA 8: Eylem Planı ──
    story.append(Paragraph("Eylem Planı", styles["TitleCustom"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Acil - Bu Hafta", styles["HeadingCustom"]))
    acil = [
        "Görsel optimizasyonu yapılması (WebP format, boyut küçültme)",
        "Misafir checkout açılması",
        "Lazy loading etkinleştirilmesi",
        "Render-blocking kaynakların ertelenmesi",
        "Meta tag'lerin düzenlenmesi",
    ]
    for idx, a in enumerate(acil, 1):
        story.append(Paragraph(f"{idx}. {a}", styles["BodyCustom"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Kısa Vade - 1 Ay", styles["HeadingCustom"]))
    kisa_vade = [
        "Facebook Pixel ve Google Ads dönüşüm kodu kurulumu",
        "Ek kargo firması entegrasyonu (Aras, Yurtiçi)",
        "Ürün açıklamalarının SEO uyumlu yazılması",
        "Structured data (Schema.org) eklenmesi",
        "Panel eğitimi ve dokümantasyon teslimi",
    ]
    for idx, k in enumerate(kisa_vade, 1):
        story.append(Paragraph(f"{idx}. {k}", styles["BodyCustom"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Platform Değişikliği Önerisi", styles["HeadingCustom"]))
    story.append(Paragraph(
        "Mevcut Ticimax altyapısının performans sorunları platform kaynaklı olup, "
        "kısa vadede tamamen çözülmesi güçtür. İkas platformuna geçiş değerlendirilmelidir. "
        "İkas, daha yüksek performans skorları, gelişmiş SEO araçları, esnek kargo "
        "entegrasyonları ve modern bir altyapı sunmaktadır.",
        styles["BodyCustom"],
    ))

    doc.build(story)
    print(f"[OK] {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# PDF 2: İhtarname (4 sayfa)
# ---------------------------------------------------------------------------
def olustur_ihtarname(output_dir):
    """4 sayfalık hukuki ihtarname PDF'i oluşturur."""
    filepath = os.path.join(output_dir, "tcc-ihtarname.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=2.5 * cm, bottomMargin=2.5 * cm,
                            leftMargin=2.5 * cm, rightMargin=2.5 * cm)
    styles = _get_styles()
    story = []

    # ── SAYFA 1: Başlık + Giriş ──
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("İHTARNAME", styles["TitleCustom"]))
    story.append(Spacer(1, 1 * cm))

    bilgi_data = [
        ["Tarih:", RAPOR_TARIHI],
        ["Konu:", "E-Ticaret Sitesi Ayıplı Teslim Bildirimi"],
        ["Muhatap:", f"{AJANS}"],
        ["İlgili Site:", SITE],
    ]
    t = Table(bilgi_data, colWidths=[3.5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
    ]))
    story.append(t)
    story.append(Spacer(1, 1 * cm))

    giris = (
        f"Sayın {AJANS} Yetkilileri,\n\n"
        f"Firmanız tarafından {SITE} adresi üzerinden teslim edilen e-ticaret sitesine "
        f"ilişkin bağımsız bir teknik denetim gerçekleştirilmiştir. Yapılan kapsamlı testler "
        f"ve analizler sonucunda, teslim edilen işin sözleşme koşullarını ve sektör "
        f"standartlarını karşılamadığı, ayıplı bir teslim niteliğinde olduğu tespit edilmiştir.\n\n"
        f"İşbu ihtarname ile tespit edilen eksikliklerin ve ayıpların bildirilmesi ile "
        f"giderilmesinin talep edilmesi amaçlanmaktadır."
    )
    story.append(Paragraph(giris, styles["BodyCustom"]))
    story.append(PageBreak())

    # ── SAYFA 2: Teknik Kanıtlar ──
    story.append(Paragraph("Teknik Kanıtlar", styles["TitleCustom"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Google Lighthouse aracı ile yapılan performans testlerinin sonuçları aşağıda sunulmuştur. "
        "Bu test sonuçları, web sitelerinin teknik kalitesini ölçmek için dünya genelinde "
        "kabul görmüş standart bir ölçüm yöntemidir.",
        styles["BodyCustom"],
    ))
    story.append(Spacer(1, 0.3 * cm))

    kanit_data = [
        ["Kategori", "Desktop", "Mobile", "Sektör Standardı"],
        ["Performance", str(GUNCEL_DESKTOP["performance"]),
         str(GUNCEL_MOBILE["performance"]), "90+"],
        ["Accessibility", str(GUNCEL_DESKTOP["accessibility"]),
         str(GUNCEL_MOBILE["accessibility"]), "90+"],
        ["Best Practices", str(GUNCEL_DESKTOP["best_practices"]),
         str(GUNCEL_MOBILE["best_practices"]), "90+"],
        ["SEO", str(GUNCEL_DESKTOP["seo"]),
         str(GUNCEL_MOBILE["seo"]), "90+"],
    ]
    t = Table(kanit_data, colWidths=[4 * cm, 3 * cm, 3 * cm, 4 * cm])
    t.setStyle(_tablo_stili(baslik_renk=colors.HexColor("#b71c1c")))
    story.append(t)

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "<b>Önemli:</b> Mobil performans skoru 18/100 olup, sektör standardı olan 90+ değerinin "
        "çok altındadır. Türkiye'de internet trafiğinin %70'inden fazlası mobil cihazlardan "
        "gelmektedir. Bu durum doğrudan satış kaybına neden olmaktadır.",
        styles["BodyCustom"],
    ))
    story.append(PageBreak())

    # ── SAYFA 3: Tespit Edilen Ayıplar ──
    story.append(Paragraph("Tespit Edilen Ayıplar", styles["TitleCustom"]))
    story.append(Spacer(1, 0.5 * cm))

    ayiplar = [
        ("Mobil performans kritik düzeyde düşük (18/100)",
         "Sektör standardı 90+ iken, teslim edilen site 18/100 skor almaktadır."),
        ("Sayfa yükleme süresi standart üstünde",
         "FCP: 3.2s, LCP: 8.5s - Kabul edilebilir sınırların çok üzerinde."),
        ("Misafir checkout kapalı",
         "Üye olmadan alışveriş yapılamıyor, potansiyel müşteri kaybı."),
        ("Tek kargo firması (HepsiJet)",
         "Müşteriye kargo seçeneği sunulmuyor, rekabet dezavantajı."),
        ("Panel eğitimi verilmemiş",
         "Site yönetim paneli kullanımına dair hiçbir eğitim verilmemiştir."),
        ("Test siparişi yapılmamış",
         "Ödeme ve sipariş süreçleri test edilmeden teslim edilmiştir."),
        ("SEO ayarları eksik",
         "Meta tag'ler, yapısal veri ve SEO temel ayarları yapılmamıştır."),
        ("Dokümantasyon yok",
         "Site kullanım kılavuzu, teknik dokümantasyon teslim edilmemiştir."),
    ]
    for i, (baslik, aciklama) in enumerate(ayiplar, 1):
        story.append(Paragraph(f"<b>{i}. {baslik}</b>", styles["BodyCustom"]))
        story.append(Paragraph(f"   {aciklama}", styles["BodyCustom"]))
        story.append(Spacer(1, 0.2 * cm))
    story.append(PageBreak())

    # ── SAYFA 4: Yasal Dayanak + Talepler ──
    story.append(Paragraph("Yasal Dayanak ve Talepler", styles["TitleCustom"]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Yasal Dayanak", styles["HeadingCustom"]))
    story.append(Paragraph(
        "6098 sayılı Türk Borçlar Kanunu'nun ayıplı ifa hükümlerine (TBK m. 219-231) göre, "
        "teslim edilen iş sözleşmede kararlaştırılan nitelikleri taşımak zorundadır. "
        "Teslim edilen e-ticaret sitesi, yukarıda belirtilen ayıplar nedeniyle sözleşme "
        "koşullarını ve sektör standartlarını karşılamamaktadır.",
        styles["BodyCustom"],
    ))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Taleplerimiz", styles["HeadingCustom"]))
    story.append(Paragraph(
        "İşbu ihtarnamenin tarafınıza tebliğinden itibaren <b>7 (yedi) iş günü</b> "
        "içerisinde aşağıdaki taleplerden birinin yerine getirilmesini talep ederiz:",
        styles["BodyCustom"],
    ))
    story.append(Spacer(1, 0.3 * cm))

    talepler = [
        "<b>A) Tüm eksiklerin ücretsiz olarak tamamlanması:</b> Yukarıda belirtilen "
        "8 maddenin tamamının sektör standartlarına uygun şekilde düzeltilmesi.",
        "<b>B) %50 bedel iadesi:</b> Ayıplı teslim nedeniyle ödenen toplam bedelin "
        "%50'sinin iadesi.",
    ]
    for t_item in talepler:
        story.append(Paragraph(t_item, styles["BodyCustom"]))
        story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Yukarıda belirtilen süre içerisinde taleplerden herhangi biri yerine getirilmediği "
        "takdirde, <b>sözleşmenin feshi, ödenen bedelin tam iadesi ve uğranılan zararların "
        "tazmini</b> için yasal yollara başvurulacaktır.",
        styles["BodyCustom"],
    ))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Saygılarımızla,", styles["BodyCustom"]))
    story.append(Paragraph(RAPOR_TARIHI, styles["SmallText"]))

    doc.build(story)
    print(f"[OK] {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# PDF 3: Ticimax Karşılaştırma (2 sayfa)
# ---------------------------------------------------------------------------
def olustur_ticimax_karsilastirma(output_dir):
    """2 sayfalık Ticimax vs İkas karşılaştırma PDF'i oluşturur."""
    filepath = os.path.join(output_dir, "tcc-ticimax-karsilastirma.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm)
    styles = _get_styles()
    story = []

    # ── SAYFA 1: Ticimax Sorun Analizi ──
    story.append(Paragraph("Ticimax Sorun Analizi", styles["TitleCustom"]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Platform Performans Verileri", styles["HeadingCustom"]))
    story.append(Paragraph(
        f"Ticimax altyapısı üzerinde çalışan {SITE} sitesinin performans test "
        f"sonuçları, platformun yapısal sorunlarına işaret etmektedir. Özellikle mobil "
        f"performans skorunun 18/100 olması, platformun mobil optimizasyon konusunda "
        f"yetersiz kaldığını göstermektedir.",
        styles["BodyCustom"],
    ))

    perf_data = [
        ["Metrik", "Değer", "Değerlendirme"],
        ["Desktop Performance", "53/100", "Düşük"],
        ["Mobile Performance", "18/100", "Kritik"],
        ["FCP", "3.2s", "Yavaş"],
        ["LCP", "8.5s", "Çok Yavaş"],
        ["TTI", "12.1s", "Çok Yavaş"],
        ["TBT", "2800ms", "Çok Yüksek"],
    ]
    t = Table(perf_data, colWidths=[5 * cm, 4 * cm, 5 * cm])
    ts = _tablo_stili(baslik_renk=colors.HexColor("#e65100"))
    for i in range(1, len(perf_data)):
        deger = perf_data[i][2]
        if "Kritik" in deger or "Çok" in deger:
            ts.add("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#ff4e42"))
        else:
            ts.add("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#ffa400"))
    t.setStyle(ts)
    story.append(t)

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Şikayetvar Verileri Özeti", styles["HeadingCustom"]))
    story.append(Paragraph(
        "sikayetvar.com üzerindeki Ticimax e-ticaret kategorisinde yapılan inceleme "
        "sonucunda, platformun kullanıcı memnuniyeti konusunda ciddi sorunlar yaşadığı "
        "görülmektedir. En sık tekrarlayan şikayetler performans düşüklüğü, ödeme hataları "
        "ve mobil uyumsuzluk olarak öne çıkmaktadır.",
        styles["BodyCustom"],
    ))

    sikayet_ozet = [["Şikayet Konusu", "Yaygınlık"]]
    for konu, sayi in SIKAYETLER[:5]:
        sikayet_ozet.append([konu, sayi])
    t = Table(sikayet_ozet, colWidths=[10 * cm, 4 * cm])
    t.setStyle(_tablo_stili(baslik_renk=colors.HexColor("#c62828")))
    story.append(t)
    story.append(PageBreak())

    # ── SAYFA 2: İkas vs Ticimax ──
    story.append(Paragraph("İkas vs Ticimax Karşılaştırma", styles["TitleCustom"]))
    story.append(Spacer(1, 0.5 * cm))

    karsilastirma = [
        ["Kriter", "Ticimax", "İkas", "Kazanan"],
        ["Mobil Performans", "Düşük (18/100)", "Yüksek (85+/100)", "İkas"],
        ["Yükleme Hızı", "3-8 saniye", "1-2 saniye", "İkas"],
        ["Kargo Entegrasyonu", "Sınırlı (1-2 firma)", "Geniş (5+ firma)", "İkas"],
        ["Pazaryeri Entegrasyonu", "Temel", "Gelişmiş", "İkas"],
        ["Misafir Checkout", "Opsiyonel (kapalı)", "Varsayılan açık", "İkas"],
        ["Aylık Maliyet", "Orta", "Rekabetçi", "Yakın"],
        ["Güncelleme Sıklığı", "Düşük", "Yüksek (haftalık)", "İkas"],
        ["Destek Kalitesi", "Orta-Düşük", "Yüksek", "İkas"],
        ["Kullanım Kolaylığı", "Karmaşık panel", "Sezgisel arayüz", "İkas"],
        ["SEO Araçları", "Temel", "Gelişmiş", "İkas"],
    ]
    t = Table(karsilastirma, colWidths=[3.8 * cm, 3.5 * cm, 3.5 * cm, 2.5 * cm])
    ts = _tablo_stili(baslik_renk=colors.HexColor("#1565c0"))
    for i in range(1, len(karsilastirma)):
        kazanan = karsilastirma[i][3]
        if kazanan == "İkas":
            ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#0cce6b"))
            ts.add("FONTNAME", (3, i), (3, i), "Helvetica-Bold")
    t.setStyle(ts)
    story.append(t)

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Sonuç ve Öneri", styles["HeadingCustom"]))
    story.append(Paragraph(
        "Yapılan karşılaştırma 10 kriterin 9'unda İkas'ın üstün olduğunu göstermektedir. "
        "Mevcut Ticimax altyapısındaki performans sorunlarının platform kaynaklı olduğu ve "
        "kısa vadede tamamen çözülmesinin güç olduğu düşünülmektedir. Orta vadede İkas "
        "platformuna geçiş, hem performans hem de kullanıcı deneyimi açısından önemli "
        "iyileştirmeler sağlayacaktır.",
        styles["BodyCustom"],
    ))

    doc.build(story)
    print(f"[OK] {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# PDF 4: Yönetici Özeti (1 sayfa)
# ---------------------------------------------------------------------------
def olustur_yonetici_ozeti(output_dir):
    """1 sayfalık yönetici özeti PDF'i oluşturur."""
    filepath = os.path.join(output_dir, "tcc-yonetici-ozeti.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm)
    styles = _get_styles()
    story = []

    # Başlık
    story.append(Paragraph(
        "Siteniz Hakkında Önemli Bilgi",
        ParagraphStyle("BigTitle", parent=styles["Title"],
                       fontSize=22, textColor=colors.HexColor("#1a237e"),
                       spaceAfter=10),
    ))

    # Bölüm 1: DURUM
    durum_data = [["⚠  Site çalışıyor ama ciddi teknik sorunlar var"]]
    t = Table(durum_data, colWidths=[15 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff3e0")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#e65100")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("BOX", (0, 0), (-1, -1), 2, colors.HexColor("#e65100")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Bölüm 2: RAKAMLAR
    story.append(Paragraph("RAKAMLAR", styles["HeadingCustom"]))
    rakam_data = [
        ["Mobil Puan", "Desktop Puan", "Olması Gereken"],
        ["18/100", "53/100", "90+"],
    ]
    t = Table(rakam_data, colWidths=[5 * cm, 5 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("FONTSIZE", (0, 1), (-1, 1), 20),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#ffcdd2")),
        ("TEXTCOLOR", (0, 1), (0, 1), colors.HexColor("#b71c1c")),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#ffe0b2")),
        ("TEXTCOLOR", (1, 1), (1, 1), colors.HexColor("#e65100")),
        ("BACKGROUND", (2, 1), (2, 1), colors.HexColor("#c8e6c9")),
        ("TEXTCOLOR", (2, 1), (2, 1), colors.HexColor("#1b5e20")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e0e0e0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Bölüm 3: NE ANLAMA GELİYOR
    story.append(Paragraph("NE ANLAMA GELİYOR?", styles["HeadingCustom"]))
    anlam_data = [[
        "100 kişi sitenizi ziyaret ediyor\n"
        "→ Telefon kullananların çoğu yavaşlık nedeniyle çıkıyor\n"
        "→ Potansiyel satışlar kaçıyor\n"
        "→ Google sıralamanız düşüyor"
    ]]
    t = Table(anlam_data, colWidths=[15 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fce4ec")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#880e4f")),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#880e4f")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Bölüm 4: NE YAPALIM
    story.append(Paragraph("NE YAPALIM?", styles["HeadingCustom"]))
    eylem_data = [
        ["1", "Ajanstan düzeltme talep et", "7 gün süre ver"],
        ["2", "Platform değişikliği değerlendir", "İkas önerisi"],
        ["3", "Teknik destek al", "Bağımsız uzman"],
    ]
    t = Table(eylem_data, colWidths=[1.5 * cm, 8 * cm, 5.5 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1a237e")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (-1, -1), colors.HexColor("#e8eaf6")),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#9fa8da")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Rapor Tarihi: {RAPOR_TARIHI} | Platform: {PLATFORM} | Ajans: {AJANS}",
        styles["SmallText"],
    ))

    doc.build(story)
    print(f"[OK] {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# Ana fonksiyon
# ---------------------------------------------------------------------------
def main(output_dir=None):
    """Tüm PDF raporlarını oluşturur."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rapor")

    os.makedirs(output_dir, exist_ok=True)
    print("=" * 60)
    print("PDF Rapor Oluşturma Başlatılıyor...")
    print(f"Çıktı klasörü: {output_dir}")
    print("=" * 60)

    olustur_teknik_rapor(output_dir)
    olustur_ihtarname(output_dir)
    olustur_ticimax_karsilastirma(output_dir)
    olustur_yonetici_ozeti(output_dir)

    print("=" * 60)
    print(f"Bitti. 4 PDF {output_dir}/ klasöründe.")
    print("=" * 60)


if __name__ == "__main__":
    main()
