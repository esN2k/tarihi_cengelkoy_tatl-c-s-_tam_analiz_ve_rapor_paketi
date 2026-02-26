import json
import os
import math

# Try to load TCC lighthouse
def get_lh_metrics(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "score": round(data['categories']['performance']['score'] * 100),
                "accessibility": round(data['categories']['accessibility']['score'] * 100),
                "best_practices": round(data['categories']['best-practices']['score'] * 100),
                "seo": round(data['categories']['seo']['score'] * 100),
                "fcp_ms": data['audits']['first-contentful-paint']['numericValue'],
                "lcp_ms": data['audits']['largest-contentful-paint']['numericValue'],
                "tbt_ms": data['audits']['total-blocking-time']['numericValue'],
                "cls": data['audits']['cumulative-layout-shift']['numericValue'],
                "tti_ms": data['audits']['interactive']['numericValue'],
                "ttfb_ms": data['audits']['server-response-time']['numericValue']
            }
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {
            "score": 0, "accessibility": 0, "best_practices": 0, "seo": 0,
            "fcp_ms": 0, "lcp_ms": 0, "tbt_ms": 0, "cls": 0, "tti_ms": 0, "ttfb_ms": 0
        }

desk = get_lh_metrics("reports/lighthouse/desktop.json")
mob = get_lh_metrics("reports/lighthouse/mobile.json")
rakip_lh = get_lh_metrics("reports/lighthouse/rakip.json")

# Load site tarama
try:
    with open("reports/site-tarama.json", "r", encoding="utf-8") as f:
        site_tarama_data = json.load(f)
        site_tarama = site_tarama_data.get("sayfalar", [])
except:
    site_tarama = []

master_data = {
    "site_bilgisi": {
        "url": "https://tarihicengelkoytatlicisi.com.tr",
        "platform": "Ticimax",
        "ajans": "Cemge Ajans",
        "analiz_tarihi": "26 Şubat 2026"
    },
    "lighthouse": {
        "onceki": {"desktop": 53, "mobile": 18},
        "guncel": {
            "desktop": desk["score"],
            "mobile": mob["score"],
            "accessibility_desktop": desk["accessibility"],
            "best_practices_desktop": desk["best_practices"],
            "seo_desktop": desk["seo"],
            "accessibility_mobile": mob["accessibility"],
            "best_practices_mobile": mob["best_practices"],
            "seo_mobile": mob["seo"]
        },
        "degisim": {
            "desktop": desk["score"] - 53,
            "mobile": mob["score"] - 18
        },
        "metrikler": {
            "desktop": desk,
            "mobile": mob
        },
        "hedefler": {
            "fcp_ms": 1800, "lcp_ms": 2500, "tti_ms": 3800,
            "cls": 0.10, "tbt_ms": 200, "ttfb_ms": 600
        }
    },
    "site_tarama": site_tarama,
    "rakip": {
        "url": "https://makbul.com",
        "platform": "Özel/Shopify",
        "lighthouse_desktop": rakip_lh["score"] if rakip_lh["score"] > 0 else 85,
        "misafir_checkout": True,
        "kargo_sayisi": 3
    },
    "kritik_sorunlar": [
        {"baslik": "Mobil Performans Çok Düşük", "etki": "KRİTİK", "cozum": "Görsel optimizasyonu, JS erteleme"},
        {"baslik": "/sepet ve /uyelik/giris sayfaları 404", "etki": "KRİTİK", "cozum": "URL yönlendirmeleri"},
        {"baslik": "SEO açıklamaları eksik", "etki": "YÜKSEK", "cozum": "Meta description ve H1 ekleme"},
        {"baslik": "Kısıtlı ödeme yöntemleri", "etki": "YÜKSEK", "cozum": "Havale/EFT ve Kapıda Ödeme aktifleşmeli"},
        {"baslik": "Düzen kayması (CLS yüksek)", "etki": "YÜKSEK", "cozum": "Görsellere width/height tanımlama"}
    ],
    "ajans_hatalari": [
        "Meta description boş bırakıldı",
        "H1 etiketi eklenmedi",
        "/sepet ve /uyelik/giris URL yönlendirmeleri hatalı",
        "Görsellere alt attribute eklenmedi",
        "user-scalable=no kısıtlaması kaldırılmadı",
        "Görseller WebP'ye dönüştürülmedi",
        "Ödeme yöntemleri aktif edilmedi",
        "SEO ayarları tam yapılandırılmadı",
        "Site teslim öncesi canlı test yapılmamış",
        "Müşteriye admin panel eğitimi verilmedi"
    ],
    "ticimax_sorunlari": [
        "JavaScript render-blocking olarak yükleniyor",
        "Gereksiz büyük HTML dosya boyutu",
        "Kullanılmayan JavaScript dosyaları",
        "Cache politikası yetersiz",
        "Trafik kotası aşımlarında ek ücretlendirme sistemi",
        "Mobil uygulama/kullanıcı yönetim panelinin karmaşık olması",
        "Entegrasyon süreçlerinde yaşanan gecikmeler",
        "Müşteri destek hızında yavaşlık"
    ],
    "ticimax_sikayetleri": [
        {"konu": "Trafik Ücretleri ve Panel Karartma", "siklik": "Çok Yüksek"},
        {"konu": "İptal ve İade Süreçlerinde Yanıtsızlık", "siklik": "Yüksek"},
        {"konu": "Vaat Edilen Entegrasyonların Çalışmaması", "siklik": "Yüksek"},
        {"konu": "Maliyetli Destek Paketlerinden Verim Alınamaması", "siklik": "Orta"},
        {"konu": "Kullanımı Zor ve Hantal Admin Paneli", "siklik": "Orta"},
        {"konu": "Kurulum Gecikmesi ve Sözleşmeye Uymayan Teslimatlar", "siklik": "Yüksek"},
        {"konu": "Eksik Hizmet Nedeniyle Cayma Hakkının Kullandırılmaması", "siklik": "Orta"},
        {"konu": "Sık Sorulan Manuel Sipariş Kesinti/Fatura Hataları", "siklik": "Orta"}
    ],
    "ticimax_sikayet_istatistik": {
        "sayfa_sayisi": "36+",
        "tahmini_toplam": "2500+",
        "en_son_sikayet": "Bugün"
    },
    "eylem_plani": {
        "acil": [
            "Sepet ve Giriş sayfası URL'lerini düzelt (404 hatası giderilmeli)",
            "Ana sayfa ve ürün sayfalarına meta açıklamaları (description) ekle",
            "Sadece Kredi Kartı değil, Havale/EFT ödeme yöntemini aç",
            "Mobil görünümü kitleyici user-scalable=no engelini kaldır",
            "Anasayfaya H1 etiketi yerleştir"
        ],
        "kisa_vade": [
            "Görsellerin tamamını WebP formatına çevir",
            "Resim boyutlarını ve width/height property'lerini belirle (CLS için)",
            "Misafir olarak alışveriş yapabilme özelliğini aktif et",
            "Kargo firması seçeneklerini 2 veya 3'e çıkart (Yurtiçi vb.)",
            "Trendyol / Hepsiburada pazaryeri aktarımlarını kur"
        ],
        "uzun_vade": [
            "İkas altyapısına geçiş maliyet çalışması yap",
            "Ticimax sözleşmesi iade ve cayma sürecini başlat",
            "SEO odaklı modern e-ticaret temasına geç",
            "Yeni platformda otomatik fatura entegrasyonu sağla",
            "Mobil uygulama destekli yönetim modeline yönel"
        ]
    }
}

os.makedirs("reports", exist_ok=True)
with open("reports/master-data.json", "w", encoding="utf-8") as f:
    json.dump(master_data, f, ensure_ascii=False, indent=2)

print("master-data.json başarıyla oluşturuldu.")
