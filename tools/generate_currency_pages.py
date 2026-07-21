"""Generuje strony kursow: /kurs-euro/, /kurs-dolara/ i tak dalej.

Kazda strona pokazuje aktualny kurs sredni NBP, tabele ostatnich notowan,
gotowe przeliczenia popularnych kwot i wykres. Wszystko jest w HTML-u —
bez JavaScriptu — zeby wyszukiwarka widziala te same liczby co czlowiek.

Kurs na stronie statycznej starzeje sie, wiec strony przebudowuje codziennie
GitHub Actions (.github/workflows/kursy.yml) po publikacji tabeli NBP.
Data i numer tabeli sa widoczne na stronie, zeby nikt nie musial zgadywac,
z kiedy jest liczba.

Uruchomienie:  python tools/generate_currency_pages.py
Wymaga:        dostepu do api.nbp.pl
"""

import html
import json
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

from currencies import COUNTRY, CURRENCIES, NOTES

API = "https://api.nbp.pl/api/exchangerates"
ROOT = Path(__file__).resolve().parent.parent

# Ile notowan pokazujemy w tabeli i na wykresie.
HISTORY_DAYS = 30
TABLE_ROWS = 10

# Kwoty w gotowych przeliczeniach — to frazy z dlugiego ogona
# ("100 euro ile to zlotych").
AMOUNTS = [1, 10, 50, 100, 500, 1000]


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def fetch_table():
    return fetch(f"{API}/tables/A?format=json")[0]


def fetch_series(code, days=HISTORY_DAYS):
    """Ostatnie notowania waluty. 404 znaczy brak notowan, nie awarie."""
    try:
        data = fetch(f"{API}/rates/a/{code}/last/{days}/?format=json")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return []
        raise
    return [(r["effectiveDate"], r["mid"]) for r in data["rates"]]


def pl_number(value, places=4):
    """Liczba po polsku: przecinek dziesietny, spacja co tysiac."""
    text = f"{value:,.{places}f}"
    return text.replace(",", " ").replace(".", ",")


def pl_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d.%m.%Y")


def sparkline(points, width=680, height=160):
    """Wykres jako inline SVG — bez bibliotek i bez zapytan do sieci."""
    if len(points) < 2:
        return ""

    values = [v for _, v in points]
    low, high = min(values), max(values)
    span = high - low or 1

    step = width / (len(points) - 1)
    coords = [
        (i * step, height - (v - low) / span * (height - 20) - 10)
        for i, (_, v) in enumerate(points)
    ]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = f"0,{height} " + line + f" {width},{height}"

    return (
        f'<svg class="chart" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="none" role="img" '
        f'aria-label="Wykres kursu z ostatnich {len(points)} notowań">'
        f'<polygon points="{area}" fill="var(--fill)"/>'
        f'<polyline points="{line}" fill="none" stroke="var(--brand)" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
        f"</svg>"
    )


def build_page(code, rate, series, table_meta):
    slug, gen, nominative = CURRENCIES[code]
    country = COUNTRY.get(code, "")
    note = NOTES.get(code)

    mid = rate["mid"]
    number = table_meta["no"]
    effective = table_meta["effectiveDate"]

    # Zmiana wzgledem pierwszego notowania w okresie — konkret, ktory
    # odroznia dzisiejsza wersje strony od wczorajszej.
    change_html = ""
    if len(series) >= 2:
        first = series[0][1]
        if first:
            pct = (mid - first) / first * 100
            arrow = "wzrost" if pct >= 0 else "spadek"
            change_html = (
                f"<p>W ciągu ostatnich {len(series)} notowań kurs "
                f"{gen} zanotował {arrow} o "
                f"<strong>{pl_number(abs(pct), 2)}%</strong> — z "
                f"{pl_number(first)} do {pl_number(mid)} zł.</p>"
            )

    rows = "\n".join(
        f"<tr><td>{pl_date(day)}</td><td>{pl_number(value)} zł</td></tr>"
        for day, value in reversed(series[-TABLE_ROWS:])
    )

    conversions = "\n".join(
        f"<tr><td>{pl_number(amount, 0)} {code}</td>"
        f"<td>{pl_number(amount * mid, 2)} zł</td></tr>"
        for amount in AMOUNTS
    )

    # Dane strukturalne — pomagaja wyszukiwarce zrozumiec, ze to kurs waluty.
    structured = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "ExchangeRateSpecification",
            "currency": code,
            "currentExchangeRate": {
                "@type": "UnitPriceSpecification",
                "price": round(mid, 4),
                "priceCurrency": "PLN",
            },
            "url": f"https://currencypilot.io/{slug}",
        },
        ensure_ascii=False,
    )

    return PAGE.format(
        code=html.escape(code),
        slug=slug,
        gen=html.escape(gen),
        nominative=html.escape(nominative),
        country=html.escape(country),
        note=html.escape(note) if note else "",
        note_block=f"<p>{html.escape(note)}</p>" if note else "",
        mid=pl_number(mid),
        effective=pl_date(effective),
        table_no=html.escape(number),
        change=change_html,
        rows=rows,
        conversions=conversions,
        chart=sparkline(series),
        structured=structured,
        history_count=len(series),
    )


PAGE = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kurs {gen} ({code}) — {mid} zł · CurrencyPilot</title>
<meta name="description" content="Kurs {gen} ({code}) z dnia {effective}: 1 {code} = {mid} zł. Kurs średni NBP, tabela {table_no}, historia notowań i przelicznik.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://currencypilot.io/{slug}">
<script type="application/ld+json">{structured}</script>
<style>
  :root {{ color-scheme: light dark; --brand:#0a6fe8; --fill:rgba(10,111,232,.12);
           --ink:#0d1117; --soft:#4a5568; --bg:#fff; --tint:#f2f6fc; --line:#dfe6f0; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --brand:#4d9dff; --fill:rgba(77,157,255,.16); --ink:#e8ecf2;
             --soft:#9aa6b8; --bg:#0c0f14; --tint:#12171f; --line:#232b36; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0 auto; padding:2rem 1.5rem 4rem; max-width:46rem;
         background:var(--bg); color:var(--ink);
         font:1rem/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
  a {{ color:var(--brand); }}
  .back {{ font-size:.9rem; margin:0 0 1.5rem; }}
  .back a {{ text-decoration:none; }}
  h1 {{ font-size:clamp(1.6rem,4vw,2.2rem); line-height:1.15;
       letter-spacing:-.03em; margin:0 0 1.25rem; }}
  .now {{ background:var(--tint); border:1px solid var(--line);
         border-radius:1rem; padding:1.5rem; margin:0 0 1.5rem; }}
  .rate {{ font-size:clamp(2rem,6vw,2.8rem); font-weight:700;
          letter-spacing:-.03em; line-height:1.1; }}
  .meta {{ color:var(--soft); font-size:.9rem; margin:.5rem 0 0; }}
  .chart {{ width:100%; height:auto; display:block; margin:1.25rem 0 0;
           border-radius:.5rem; }}
  h2 {{ font-size:1.2rem; margin:2.5rem 0 .75rem; letter-spacing:-.02em; }}
  p {{ margin:0 0 1rem; }}
  table {{ width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; }}
  th, td {{ text-align:left; padding:.6rem .75rem; border-bottom:1px solid var(--line); }}
  th {{ color:var(--soft); font-weight:600; font-size:.85rem;
       text-transform:uppercase; letter-spacing:.05em; }}
  td:last-child, th:last-child {{ text-align:right; }}
  .cta {{ background:var(--tint); border:1px solid var(--line);
         border-radius:1rem; padding:1.5rem; margin:2.5rem 0 0; }}
  .cta p:last-child {{ margin-bottom:0; }}
  footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line);
           color:var(--soft); font-size:.85rem; }}
</style>
</head>
<body>

<p class="back"><a href="/">← CurrencyPilot</a> · <a href="/kursy-walut">wszystkie waluty</a></p>

<h1>Kurs {gen} ({code})</h1>

<div class="now">
  <div class="rate">1 {code} = {mid} zł</div>
  <p class="meta">Kurs średni NBP · tabela {table_no} · {effective}</p>
  {chart}
</div>

{change}
{note_block}
<p>
  {nominative} to waluta, której obszarem obowiązywania jest {country}.
  Kurs średni publikuje Narodowy Bank Polski w tabeli A — w dni robocze
  około godziny 12:15.
</p>

<h2>Ile to złotych</h2>
<table>
  <thead><tr><th>Kwota</th><th>Wartość w złotych</th></tr></thead>
  <tbody>
{conversions}
  </tbody>
</table>
<p class="meta">Przeliczenia po kursie średnim z {effective}.</p>

<h2>Ostatnie notowania</h2>
<table>
  <thead><tr><th>Data</th><th>Kurs średni</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>

<div class="cta">
  <p>
    <strong>Kurs zmienia się codziennie.</strong> Ta strona pokazuje notowanie
    z {effective} i jest odświeżana każdego dnia roboczego po publikacji
    tabeli NBP.
  </p>
  <p>
    Jeśli chcesz mieć aktualny kurs pod ręką razem z kalkulatorem i wykresem —
    <a href="/">zobacz aplikację Konwerter walut</a>. Działa też bez internetu,
    na ostatnio pobranych danych.
  </p>
</div>

<h2>Częste pytania</h2>
<p>
  <strong>Czy to kurs, po którym kupię {gen} w kantorze?</strong><br>
  Nie. Kurs średni NBP jest kursem referencyjnym — używa się go w księgowości
  i rozliczeniach podatkowych. Kantory i banki doliczają własną marżę, więc
  kupno wypada drożej, a sprzedaż taniej.
</p>
<p>
  <strong>Kiedy pojawia się nowy kurs?</strong><br>
  NBP publikuje tabelę A w dni robocze około 12:15. W weekendy i święta
  obowiązuje ostatnia opublikowana tabela.
</p>

<footer>
  Dane: Narodowy Bank Polski, tabela A (kursy średnie). CurrencyPilot nie jest
  powiązany z NBP. Kursy mają charakter informacyjny — nie stanowią oferty
  ani doradztwa finansowego.
</footer>

</body>
</html>
"""


INDEX = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kursy walut NBP — tabela z {effective} · CurrencyPilot</title>
<meta name="description" content="Kursy średnie NBP z {effective}, tabela {table_no}. Wszystkie waluty tabeli A wraz z historią notowań.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://currencypilot.io/kursy-walut">
<style>
  :root {{ color-scheme: light dark; --brand:#0a6fe8; --ink:#0d1117;
           --soft:#4a5568; --bg:#fff; --tint:#f2f6fc; --line:#dfe6f0; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --brand:#4d9dff; --ink:#e8ecf2; --soft:#9aa6b8; --bg:#0c0f14;
             --tint:#12171f; --line:#232b36; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0 auto; padding:2rem 1.5rem 4rem; max-width:46rem;
         background:var(--bg); color:var(--ink);
         font:1rem/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
  a {{ color:var(--brand); }}
  .back {{ font-size:.9rem; margin:0 0 1.5rem; }} .back a {{ text-decoration:none; }}
  h1 {{ font-size:clamp(1.6rem,4vw,2.2rem); letter-spacing:-.03em; margin:0 0 .4rem; }}
  .meta {{ color:var(--soft); margin:0 0 2rem; }}
  table {{ width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; }}
  th, td {{ text-align:left; padding:.6rem .5rem; border-bottom:1px solid var(--line); }}
  th {{ color:var(--soft); font-weight:600; font-size:.85rem;
       text-transform:uppercase; letter-spacing:.05em; }}
  td:last-child, th:last-child {{ text-align:right; }}
  td a {{ text-decoration:none; }}
  .kod {{ color:var(--soft); font-size:.85rem; }}
  footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line);
           color:var(--soft); font-size:.85rem; }}
</style>
</head>
<body>

<p class="back"><a href="/">← CurrencyPilot</a></p>

<h1>Kursy walut NBP</h1>
<p class="meta">Tabela {table_no} · {effective} · kursy średnie</p>

<table>
  <thead><tr><th>Waluta</th><th>Kurs średni</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>

<footer>
  Dane: Narodowy Bank Polski, tabela A. Strona odświeżana codziennie po
  publikacji tabeli. CurrencyPilot nie jest powiązany z NBP.
</footer>

</body>
</html>
"""


def write_sitemap(slugs, effective):
    """Mapa strony — generowana, zeby nie zapomniec o nowej walucie.

    `lastmod` stron kursow to data notowania, nie data buildu: strona zmienia
    sie razem z tabela NBP, a nie za kazdym przebiegiem workflow.
    """
    static = []
    for path, filename in [("", "index.html"), ("privacy", "privacy/index.html")]:
        file = ROOT / filename
        if file.exists():
            modified = date.fromtimestamp(file.stat().st_mtime).isoformat()
            static.append((f"https://currencypilot.io/{path}", modified, "0.9"))

    entries = static + [
        ("https://currencypilot.io/kursy-walut", effective, "0.8")
    ] + [
        (f"https://currencypilot.io/{slug}", effective, "0.7") for slug in slugs
    ]

    body = "\n".join(
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>"
        for loc, lastmod, priority in entries
    )

    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    return len(entries)


def write_redirects():
    """Stare adresy /kurs/<kod> kieruja na nowe, frazowe.

    Aplikacja wypuszczona przed ta zmiana nadal buduje linki w starym
    formacie, a i tak juz ktos moze je miec zapisane. Redirect trzymamy
    w vercel.json obok reszty konfiguracji, ale wpisujemy go stad, zeby
    nie rozjechal sie ze slownikiem walut.
    """
    config_path = ROOT / "vercel.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    config["redirects"] = [
        {
            "source": f"/kurs/{code.lower()}",
            "destination": f"/{slug}",
            "permanent": True,
        }
        for code, (slug, _, _) in CURRENCIES.items()
    ] + [
        {"source": "/kurs", "destination": "/kursy-walut", "permanent": True},
    ]

    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(config["redirects"])


def main():
    table = fetch_table()
    rates = {r["code"]: r for r in table["rates"]}
    meta = {"no": table["no"], "effectiveDate": table["effectiveDate"]}

    written = 0
    index_rows = []

    for code, (slug, gen, nominative) in CURRENCIES.items():
        rate = rates.get(code)
        if rate is None:
            print(f"  pominieto {code} — nie ma go w dzisiejszej tabeli")
            continue

        series = fetch_series(code)
        page = build_page(code, rate, series, meta)

        directory = ROOT / slug
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(page, encoding="utf-8")
        written += 1

        index_rows.append(
            (nominative, f'<tr><td><a href="/{slug}">{html.escape(nominative)}</a>'
                         f' <span class="kod">{code}</span></td>'
                         f'<td>{pl_number(rate["mid"])} zł</td></tr>')
        )

    index = INDEX.format(
        effective=pl_date(meta["effectiveDate"]),
        table_no=html.escape(meta["no"]),
        rows="\n".join(row for _, row in sorted(index_rows)),
    )
    directory = ROOT / "kursy-walut"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "index.html").write_text(index, encoding="utf-8")

    redirects = write_redirects()
    urls = write_sitemap(
        [CURRENCIES[code][0] for code in CURRENCIES if code in rates],
        meta["effectiveDate"],
    )

    print(f"  tabela {meta['no']} z {pl_date(meta['effectiveDate'])}")
    print(f"  wygenerowano {written} stron walut + spis /kursy-walut")
    print(f"  przekierowan ze starych adresow: {redirects}")
    print(f"  adresow w sitemap.xml: {urls}")


if __name__ == "__main__":
    main()
