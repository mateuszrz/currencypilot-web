"""Generuje obrazek podgladu spolecznosciowego og.png (1024x500).

Niebieskie tlo marki, po lewej okragly badge z bialym kalkulatorem (ten sam
motyw co ikona aplikacji), po prawej nazwa i podtytul. Rysujemy kodem, zeby
zmiana napisu albo koloru byla jedna linijka.

Uruchomienie:  python tools/generate_og.py
Wymaga:        Pillow
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "og.png"

W, H = 1024, 500
BRAND = (10, 132, 255)
WHITE = (255, 255, 255)
TOP = (43, 147, 247)   # jasniejszy niebieski u gory
BOTTOM = (10, 95, 208)  # ciemniejszy u dolu
SS = 4  # supersampling dla gladkich krawedzi

_BOLD = ["C:/Windows/Fonts/arialbd.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
_REG = ["C:/Windows/Fonts/arial.ttf", "arial.ttf", "DejaVuSans.ttf"]


def font(paths, px):
    for p in paths:
        try:
            return ImageFont.truetype(p, int(px))
        except OSError:
            continue
    return ImageFont.load_default()


def gradient(w, h):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        color = tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=color)
    return img


def calculator(size):
    """Bialy kalkulator z niebieskim wyswietlaczem ($) i przyciskami."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    bw, bh = size * 0.60, size * 0.84
    bx, by = (size - bw) / 2, (size - bh) / 2
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=size * 0.11, fill=WHITE)

    pad = size * 0.085
    ix0, iy0 = bx + pad, by + pad
    ix1, iy1 = bx + bw - pad, by + bh - pad
    iw, ih = ix1 - ix0, iy1 - iy0
    r = size * 0.018

    disp_h = ih * 0.26
    d.rounded_rectangle([ix0, iy0, ix1, iy0 + disp_h], radius=r, fill=BRAND)
    d.text((ix0 + iw / 2, iy0 + disp_h / 2), "$", font=font(_BOLD, disp_h * 1.15),
           fill=WHITE, anchor="mm")

    grid_top = iy0 + disp_h + ih * 0.10
    gh = iy1 - grid_top
    gap = iw * 0.16
    kw = (iw - gap * 2) / 3
    kh = (gh - gap * 2) / 3
    for row in range(3):
        for col in range(3):
            x0 = ix0 + col * (kw + gap)
            y0 = grid_top + row * (kh + gap)
            d.rounded_rectangle([x0, y0, x0 + kw, y0 + kh], radius=r, fill=BRAND)
    return img


def main():
    base = gradient(W * SS, H * SS).convert("RGBA")

    # Badge na osobnej warstwie i alpha_composite — inaczej „biel z alfa"
    # przy splaszczeniu do RGB wychodzi w pelni biala, nie polprzezroczysta.
    cx, cy, rad = 178 * SS, 250 * SS, 112 * SS
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(255, 255, 255, 40))
    od.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
               outline=(255, 255, 255, 110), width=2 * SS)
    base.alpha_composite(overlay)

    cal = calculator(int(rad * 1.35))
    base.alpha_composite(cal, (cx - cal.width // 2, cy - cal.height // 2))

    # Teksty po prawej.
    d = ImageDraw.Draw(base)
    tx = 336 * SS
    d.text((tx, 200 * SS), "Konwerter walut", font=font(_BOLD, 66 * SS),
           fill=WHITE, anchor="lm")
    d.text((tx, 262 * SS), "Kursy średnie, kalkulator, historia",
           font=font(_REG, 30 * SS), fill=WHITE, anchor="lm")
    d.text((tx, 314 * SS), "Bez reklam  ·  bez kont  ·  bez śledzenia",
           font=font(_REG, 24 * SS), fill=(214, 231, 252), anchor="lm")

    out = base.resize((W, H), Image.LANCZOS).convert("RGB")
    out.save(OUT, "PNG")
    print(f"  {OUT.name}  {out.width}x{out.height}")


if __name__ == "__main__":
    main()
