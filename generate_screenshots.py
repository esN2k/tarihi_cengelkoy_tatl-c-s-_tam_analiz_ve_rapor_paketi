import fitz
import os
import glob

os.makedirs('reports/final/screenshots', exist_ok=True)
pdf_files = glob.glob('reports/final/*.pdf')

for pdf_path in pdf_files:
    pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=150)
        out_path = f"reports/final/screenshots/{pdf_name}_page_{i+1}.png"
        pix.save(out_path)
        print(f"Saved {out_path}")
    doc.close()

print("All screenshots generated successfully.")
