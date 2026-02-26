"""
Tarihi Çengelköy Tatlıcısı - Site Tarama Scripti
Belirtilen URL'leri tarar ve HTTP durum kodları ile yükleme sürelerini raporlar.
"""

import json
import os
import time

import requests


URLS = [
    "https://tarihicengelkoytatlicisi.com.tr",
    "https://tarihicengelkoytatlicisi.com.tr/sepet",
    "https://tarihicengelkoytatlicisi.com.tr/sitemap.xml",
    "https://tarihicengelkoytatlicisi.com.tr/robots.txt",
    "https://tarihicengelkoytatlicisi.com.tr/kargo-ve-teslimat",
    "https://tarihicengelkoytatlicisi.com.tr/iletisim",
    "https://tarihicengelkoytatlicisi.com.tr/hakkimizda",
    "https://tarihicengelkoytatlicisi.com.tr/uyelik/giris",
]


def tara_siteleri(urls=None):
    """Belirtilen URL listesini tarar ve sonuçları döndürür."""
    if urls is None:
        urls = URLS

    results = []
    for url in urls:
        start = time.time()
        try:
            r = requests.get(url, timeout=15)
            elapsed = round((time.time() - start) * 1000)
            results.append({
                "url": url,
                "status": r.status_code,
                "time_ms": elapsed,
                "ok": r.status_code == 200,
            })
        except requests.RequestException:
            elapsed = round((time.time() - start) * 1000)
            results.append({
                "url": url,
                "status": "HATA",
                "time_ms": elapsed,
                "ok": False,
            })
    return results


def sitemap_url_sayisi(sitemap_url="https://tarihicengelkoytatlicisi.com.tr/sitemap.xml"):
    """Sitemap XML'den URL sayısını döndürür."""
    try:
        r = requests.get(sitemap_url, timeout=15)
        if r.status_code == 200:
            return r.text.count("<loc>")
    except requests.RequestException:
        pass
    return None


def main():
    """Site taramasını çalıştırır ve sonuçları kaydeder."""
    print("=" * 60)
    print("Site Tarama Başlatılıyor...")
    print("=" * 60)

    results = tara_siteleri()

    print(f"\n{'Durum':<8} | {'Süre':<10} | URL")
    print("-" * 60)
    for r in results:
        print(f"{r['status']:<8} | {r['time_ms']}ms{'':<5} | {r['url']}")

    sitemap_count = sitemap_url_sayisi()
    if sitemap_count is not None:
        print(f"\nSitemap URL sayısı: {sitemap_count}")
    else:
        print("\nSitemap erişilemedi.")

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rapor")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "site-tarama-sonuclari.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "tarama_sonuclari": results,
            "sitemap_url_sayisi": sitemap_count,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSonuçlar kaydedildi: {output_path}")

    return results, sitemap_count


if __name__ == "__main__":
    main()
