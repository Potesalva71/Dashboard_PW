"""Crea le schermate annotate (cerchi numerati) usate dalla scheda «Guida alla lettura».
Uso: python crea_immagini_guida.py [cartella_figure]   (default: ../../figure) -> dati_dashboard/guida/g*.jpg
Richiede Pillow. I numeri corrispondono all'elenco «Cosa mostra» in guida.py."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FIG = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "figure"
OUT = Path(__file__).parent / "dati_dashboard" / "guida"; OUT.mkdir(parents=True, exist_ok=True)
ROSSO = (214, 40, 57)

# (file sorgente, file di uscita, marker [(n, x, y)], riquadri [(x0, y0, x1, y1)])
SCHEDE = [
    ("fig_4e_stato_reparto.png", "g1_stato.jpg", [(1, 362, 262), (2, 1000, 236), (3, 362, 342), (4, 362, 678), (5, 362, 934)], []),
    ("fig_4e_ciclo_allarme_S_anomalo.png", "g2_autoclave.jpg", [(1, 362, 218), (2, 362, 268), (3, 395, 322), (4, 395, 520), (5, 362, 818), (6, 362, 930), (7, 362, 986)], [(1350, 536, 1398, 696)]),
    ("fig_4e_qualita_R01.png", "g3_qualita.jpg", [(1, 362, 218), (2, 395, 322), (3, 940, 322), (4, 362, 680), (5, 362, 738), (6, 362, 912)], []),
    ("fig_4e_raccomandazione.png", "g4_vuoto.jpg", [(1, 362, 260), (2, 362, 345), (3, 470, 620), (4, 515, 510), (5, 760, 440), (6, 1425, 470), (7, 362, 840)], []),
    ("fig_4e_pressa_altezza.png", "g5_pressa.jpg", [(1, 362, 218), (2, 362, 345), (3, 362, 417), (4, 362, 555), (5, 425, 708), (6, 362, 825), (7, 362, 942)], []),
]

def font(size):
    for f in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()

for src, dst, marks, boxes in SCHEDE:
    im = Image.open(FIG / src).convert("RGB"); d = ImageDraw.Draw(im); f = font(17)
    for b in boxes: d.rectangle(b, outline=ROSSO, width=3)
    for n, x, y in marks:
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=ROSSO, outline="white", width=2)
        d.text((x, y), str(n), fill="white", font=f, anchor="mm")
    w = 1200; im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(OUT / dst, quality=86, optimize=True); print(dst, im.size, (OUT / dst).stat().st_size // 1024, "KB")
