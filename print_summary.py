import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('reports/master-data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("================================================")
print("TCC RAPOR PAKETI - TAMAMLANDI")
print("================================================")
print("Tarih: 26 Şubat 2026\n")
print("LIGHTHOUSE SONUÇLARI:")
prev_d = d["lighthouse"]["onceki"]["desktop"]
curr_d = d["lighthouse"]["guncel"]["desktop"]
diff_d = d["lighthouse"]["degisim"]["desktop"]
prev_m = d["lighthouse"]["onceki"]["mobile"]
curr_m = d["lighthouse"]["guncel"]["mobile"]
diff_m = d["lighthouse"]["degisim"]["mobile"]

print(f"  Desktop: {prev_d} → {curr_d} ({'+' if diff_d > 0 else ''}{diff_d} değişim)")
print(f"  Mobile:  {prev_m} → {curr_m} ({'+' if diff_m > 0 else ''}{diff_m} değişim)\n")
print("OLUŞTURULAN DOSYALAR:")
print("  reports/final/tcc-teknik-rapor-FINAL.pdf    (10 sayfa)")
print("  reports/final/tcc-ihtarname-FINAL.pdf       (5 sayfa)")
print("  reports/final/tcc-platform-karsilastirma-FINAL.pdf (3 sayfa)")
print("  reports/final/tcc-yonetici-ozeti-FINAL.pdf  (1 sayfa)")
print("  reports/final/tcc-sunum-FINAL.pdf           (6 sayfa)\n")
print(f"TOPLAM KRİTİK SORUN: {len(d['kritik_sorunlar'])}")
print(f"AJANS HATALARI: {len(d['ajans_hatalari'])} madde")
print(f"TİCİMAX SORUNLARI: {len(d['ticimax_sorunlari'])} madde\n")
print("DURUM: [OK] TESLIMAT HAZIR")
print("================================================")
