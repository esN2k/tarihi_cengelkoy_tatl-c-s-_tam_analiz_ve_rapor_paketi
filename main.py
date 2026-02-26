#!/usr/bin/env python3
"""
Tarihi Çengelköy Tatlıcısı - Tam Analiz ve Rapor Paketi
Ana çalıştırma scripti: Tüm analizleri sırasıyla yürütür ve 4 PDF üretir.

Kullanım:
    python main.py
    python main.py --output-dir /path/to/output
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="TCC Tam Analiz ve Rapor Paketi",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "rapor"),
        help="PDF çıktı klasörü (varsayılan: ./rapor/)",
    )
    parser.add_argument(
        "--skip-tarama",
        action="store_true",
        help="Site taramasını atla",
    )
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("TARİHİ ÇENGELKÖY TATLICISI")
    print("TAM ANALİZ VE RAPOR PAKETİ")
    print("=" * 60)

    # Adım 1: Site Taraması
    if not args.skip_tarama:
        print("\n[1/2] Site taraması başlatılıyor...")
        try:
            from scripts.site_tarama import main as tarama_main
            tarama_main()
        except (ImportError, OSError) as e:
            print(f"Site taraması sırasında hata: {e}")
            print("Site taraması atlanıyor, PDF oluşturma devam edecek.")
    else:
        print("\n[1/2] Site taraması atlandı (--skip-tarama)")

    # Adım 2: PDF Oluşturma
    print("\n[2/2] PDF raporları oluşturuluyor...")
    from scripts.pdf_olustur import main as pdf_main
    pdf_main(output_dir)

    print(f"\nBitti. 4 PDF {output_dir}/ klasöründe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
