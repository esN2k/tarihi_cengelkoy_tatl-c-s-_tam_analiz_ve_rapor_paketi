import requests, time, json
from xml.etree import ElementTree as ET

urls = {
    "Ana Sayfa": "https://tarihicengelkoytatlicisi.com.tr",
    "Sepet": "https://tarihicengelkoytatlicisi.com.tr/sepet",
    "Checkout": "https://tarihicengelkoytatlicisi.com.tr/checkout",
    "Kargo Bilgi": "https://tarihicengelkoytatlicisi.com.tr/kargo-ve-teslimat",
    "İletişim": "https://tarihicengelkoytatlicisi.com.tr/iletisim",
    "Hakkımızda": "https://tarihicengelkoytatlicisi.com.tr/hakkimizda",
    "Üye Girişi": "https://tarihicengelkoytatlicisi.com.tr/uyelik/giris",
    "Sitemap": "https://tarihicengelkoytatlicisi.com.tr/sitemap.xml",
    "Robots": "https://tarihicengelkoytatlicisi.com.tr/robots.txt"
}

results = []
for name, url in urls.items():
    try:
        start = time.time()
        r = requests.get(url, timeout=15, 
                        headers={"User-Agent": "Mozilla/5.0"})
        ms = round((time.time()-start)*1000)
        results.append({
            "sayfa": name, "url": url,
            "durum": r.status_code,
            "sure_ms": ms,
            "hiz_degerlendirme": "✓ Hızlı" if ms<2000 
                                 else "⚠ Yavaş" if ms<4000 
                                 else "✗ Çok Yavaş"
        })
    except Exception as e:
        results.append({"sayfa": name, "url": url,
                       "durum": "HATA", "sure_ms": 0,
                       "hiz_degerlendirme": "✗ Erişilemiyor"})

# Sitemap URL sayısı
try:
    sm = requests.get("https://tarihicengelkoytatlicisi.com.tr/sitemap.xml")
    root = ET.fromstring(sm.content)
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    url_count = len(root.findall('.//sm:url', ns))
except:
    url_count = "Okunamadı"

import os
os.makedirs("reports", exist_ok=True)
with open("reports/site-tarama.json", "w", encoding="utf-8") as f:
    json.dump({"sayfalar": results, "sitemap_url_sayisi": url_count}, f, 
              ensure_ascii=False, indent=2)

print(f"Tarama tamamlandı. Sitemap URL sayısı: {url_count}")
for r in results:
    print(f"{r['durum']} | {r['sure_ms']}ms | {r['hiz_degerlendirme']} | {r['sayfa']}")
