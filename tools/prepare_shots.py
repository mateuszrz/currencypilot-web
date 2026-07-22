"""Przygotowuje surowe zrzuty z telefonu do uzycia na stronie.

Surowy zrzut z `adb shell screencap` ma pasek stanu (godzina, bateria,
ikony powiadomien) i systemowy uchwyt gestow na dole. Na stronie oba
wygladaja jak smiec i zdradzaja prywatne dane wlasciciela telefonu,
wiec je odcinamy. Wynik zapisujemy w WebP, bo strona ma sie ladowac
szybko, a to te same piksele przy ~5x mniejszym pliku.

Uruchomienie:  python tools/prepare_shots.py <katalog-z-surowymi-zrzutami> [katalog-wyjsciowy]
Wymaga:        Pillow

Domyslnie zapisuje do /shots/ (polski landing). Drugi argument pozwala celowac
gdzie indziej, np. /en/shots/ dla angielskiego landingu.
"""

import sys
from pathlib import Path

from PIL import Image

# Pixel 9: 1080x2424. Pasek stanu konczy sie ok. 150 px, uchwyt gestow
# zajmuje ostatnie ~60 px. Liczymy w proporcjach, zeby zrzut z innego
# telefonu tez sie przyciął sensownie.
TOP_RATIO = 150 / 2424
BOTTOM_RATIO = 60 / 2424

# Szerokosc docelowa: na stronie zrzut ma ok. 300 px, wiec 720 px starcza
# na ekrany o podwojonej gestosci i zostawia zapas.
TARGET_WIDTH = 720

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "shots"


def prepare(path):
    img = Image.open(path)
    top = int(img.height * TOP_RATIO)
    bottom = img.height - int(img.height * BOTTOM_RATIO)

    cropped = img.crop((0, top, img.width, bottom))
    height = round(cropped.height * TARGET_WIDTH / cropped.width)

    return cropped.resize((TARGET_WIDTH, height), Image.LANCZOS)


def main():
    args = sys.argv[1:]
    if not 1 <= len(args) <= 2:
        raise SystemExit(
            "Uzycie: python tools/prepare_shots.py <katalog> [katalog-wyjsciowy]"
        )

    source = Path(args[0])
    out_dir = Path(args[1]) if len(args) == 2 else DEFAULT_OUT
    raws = sorted(source.glob("*.png"))
    if not raws:
        raise SystemExit(f"Brak plikow PNG w {source}")

    out_dir.mkdir(parents=True, exist_ok=True)

    for raw in raws:
        out = out_dir / f"{raw.stem}.webp"
        prepared = prepare(raw)
        prepared.save(out, "WEBP", quality=85, method=6)
        kb = out.stat().st_size / 1024
        print(f"  {out.name}  {prepared.width}x{prepared.height}  {kb:.0f} kB")


if __name__ == "__main__":
    main()
