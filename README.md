# Tarihi Çengelköy Tatlıcısı - Tam Analiz ve Rapor Paketi

E-ticaret sitesi ([tarihicengelkoytatlicisi.com.tr](https://tarihicengelkoytatlicisi.com.tr)) için hazırlanmış teknik denetim, analiz ve rapor paketi.

## Gereksinimler

- Python 3.10+
- reportlab (`pip install reportlab`)
- requests (`pip install requests`)

```bash
pip install -r requirements.txt
```

## Kullanım

Tüm analizleri çalıştırıp 4 PDF oluşturmak için:

```bash
python main.py
```

Sadece PDF oluşturmak için (site taraması olmadan):

```bash
python main.py --skip-tarama
```

Özel çıktı klasörü belirtmek için:

```bash
python main.py --output-dir /path/to/output
```

## Oluşturulan Raporlar

| PDF | Açıklama | Sayfa |
|-----|----------|-------|
| `tcc-teknik-rapor.pdf` | Teknik denetim raporu (Lighthouse, site tarama, entegrasyon, şikayet analizi, eylem planı) | 8 |
| `tcc-ihtarname.pdf` | Hukuki ihtarname (ayıplı teslim bildirimi) | 4 |
| `tcc-ticimax-karsilastirma.pdf` | Ticimax vs İkas platform karşılaştırması | 2 |
| `tcc-yonetici-ozeti.pdf` | Yönetici özeti (basit dil, renkli) | 1 |

## Proje Yapısı

```
├── main.py                  # Ana çalıştırma scripti
├── requirements.txt         # Python bağımlılıkları
├── scripts/
│   ├── site_tarama.py       # Site tarama scripti
│   └── pdf_olustur.py       # PDF oluşturma scripti (reportlab)
└── rapor/                   # Oluşturulan PDF'ler
    ├── tcc-teknik-rapor.pdf
    ├── tcc-ihtarname.pdf
    ├── tcc-ticimax-karsilastirma.pdf
    └── tcc-yonetici-ozeti.pdf
```

## Bilgiler

- **Platform:** Ticimax
- **Ajans:** Cemge Ajans
- **Önceki Lighthouse:** Desktop 53/100 | Mobile 18/100
- **Hedef:** 90+/100
