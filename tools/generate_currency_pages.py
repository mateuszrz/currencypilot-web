"""Generuje podstrony /kurs/<kod> dla walut z tabeli A NBP.

Kazda podstrona jest celem App Linka z aplikacji (`/kurs/eur`), a dla kogos
bez aplikacji — zwyczajna strona zamiast bledu 404.

Czego tu swiadomie NIE MA: liczbowych kursow. Strona jest statyczna, a kurs
zmienia sie codziennie — opublikowana liczba po tygodniu bylaby po prostu
nieprawdziwa. Kurs pokazuje aplikacja, ktora pobiera go na biezaco.

Waluty z realnym wolumenem wyszukiwan dostaja wlasny akapit (NOTES ponizej).
Reszta krotszy wariant — 32 strony roznice sie tylko nazwa waluty to dla
wyszukiwarek strony przelotowe, a takie zestawy potrafia zaszkodzic calej
domenie.

Uruchomienie:  python tools/generate_currency_pages.py
Wymaga:        dostepu do api.nbp.pl (tylko lista walut, bez kursow)
"""

import html
import json
import re
import urllib.request
from pathlib import Path

TABLE_URL = "https://api.nbp.pl/api/exchangerates/tables/A?format=json"

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "kurs"

# Dopelniacz kazdej nazwy — "kurs korony czeskiej", nie "kurs korona czeska".
# Slownik, a nie reguly: polska fleksja ma za duzo wyjatkow, zeby zgadywac
# ("korona czeska" → "czesky" przy naiwnym obcinaniu koncowki).
# Frazy w dopelniaczu sa tez tym, czego ludzie faktycznie szukaja.
GENITIVE = {
    "THB": "bata",
    "USD": "dolara amerykańskiego",
    "AUD": "dolara australijskiego",
    "HKD": "dolara Hongkongu",
    "CAD": "dolara kanadyjskiego",
    "NZD": "dolara nowozelandzkiego",
    "SGD": "dolara singapurskiego",
    "EUR": "euro",
    "HUF": "forinta",
    "CHF": "franka szwajcarskiego",
    "GBP": "funta szterlinga",
    "UAH": "hrywny",
    "JPY": "jena",
    "CZK": "korony czeskiej",
    "DKK": "korony duńskiej",
    "ISK": "korony islandzkiej",
    "NOK": "korony norweskiej",
    "SEK": "korony szwedzkiej",
    "RON": "leja rumuńskiego",
    "TRY": "liry tureckiej",
    "ILS": "nowego izraelskiego szekla",
    "CLP": "peso chilijskiego",
    "PHP": "peso filipińskiego",
    "MXN": "peso meksykańskiego",
    "ZAR": "randa",
    "BRL": "reala",
    "MYR": "ringgita",
    "IDR": "rupii indonezyjskiej",
    "INR": "rupii indyjskiej",
    "KRW": "wona południowokoreańskiego",
    "CNY": "yuana renminbi",
    "XDR": "SDR",
}

# Waluty, ktorych Polacy realnie szukaja — kazda z wlasnym akapitem.
# Tresc ma byc prawdziwa i konkretna, inaczej nie ma po co jej pisac.
NOTES = {
    "EUR": "Euro jest walutą dwudziestu krajów strefy euro, w tym Niemiec, "
           "Francji, Włoch i Słowacji. To najczęściej przeliczana waluta "
           "w Polsce — od zakupów w sklepach internetowych po rozliczanie "
           "wyjazdów służbowych.",
    "USD": "Dolar amerykański jest walutą Stanów Zjednoczonych i podstawową "
           "walutą rozliczeniową w handlu międzynarodowym. W dolarach "
           "notowane są między innymi surowce i większość usług chmurowych.",
    "GBP": "Funt szterling jest walutą Wielkiej Brytanii. Przydaje się przy "
           "zakupach w brytyjskich sklepach i przy rozliczaniu pracy dla "
           "tamtejszych firm.",
    "CHF": "Frank szwajcarski jest walutą Szwajcarii i Liechtensteinu. "
           "W Polsce śledzony głównie przez osoby spłacające kredyty "
           "indeksowane do tej waluty.",
    "CZK": "Korona czeska jest walutą Czech — jedna z najczęściej "
           "przeliczanych walut przy wyjazdach weekendowych.",
    "NOK": "Korona norweska jest walutą Norwegii. Często przeliczana przez "
           "osoby pracujące w Skandynawii.",
    "SEK": "Korona szwedzka jest walutą Szwecji.",
    "DKK": "Korona duńska jest walutą Danii.",
    "JPY": "Jen jest walutą Japonii. NBP podaje jego kurs za sto jenów, "
           "co łatwo przeoczyć przy ręcznym przeliczaniu.",
    "CAD": "Dolar kanadyjski jest walutą Kanady.",
    "AUD": "Dolar australijski jest walutą Australii.",
    "HUF": "Forint jest walutą Węgier. NBP podaje jego kurs za sto forintów.",
    "UAH": "Hrywna jest walutą Ukrainy.",
    "TRY": "Lira turecka jest walutą Turcji.",
}

PAGE = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kurs {gen_title} ({code}) — CurrencyPilot</title>
<meta name="description" content="{meta}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://currencypilot.io/kurs/{slug}">
<style>
  :root {{ color-scheme: light dark; --brand:#0a6fe8; --ink:#0d1117;
           --soft:#4a5568; --bg:#fff; --tint:#f2f6fc; --line:#dfe6f0; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --brand:#4d9dff; --ink:#e8ecf2; --soft:#9aa6b8; --bg:#0c0f14;
             --tint:#12171f; --line:#232b36; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0 auto; padding:2rem 1.5rem 4rem; max-width:44rem;
         background:var(--bg); color:var(--ink);
         font:1rem/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
  a {{ color: var(--brand); }}
  .back {{ font-size:.9rem; margin:0 0 2rem; }}
  .back a {{ text-decoration:none; }}
  h1 {{ font-size:clamp(1.7rem,4vw,2.3rem); line-height:1.15;
       letter-spacing:-.03em; margin:0 0 .5rem; }}
  .code {{ color:var(--soft); margin:0 0 1.75rem; }}
  h2 {{ font-size:1.15rem; margin:2.25rem 0 .6rem; letter-spacing:-.015em; }}
  p {{ margin:0 0 1rem; }}
  .card {{ background:var(--tint); border:1px solid var(--line);
          border-radius:1rem; padding:1.5rem; margin:2rem 0; }}
  .card p:last-child {{ margin-bottom:0; }}
  ul {{ padding-left:1.15rem; color:var(--soft); }}
  li {{ margin:.35rem 0; }}
  footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line);
           color:var(--soft); font-size:.9rem; }}
</style>
</head>
<body>

<p class="back"><a href="/">← CurrencyPilot</a></p>

<h1>Kurs {gen_title}</h1>
<p class="code">{name} · {code} · kurs średni, tabela A</p>

<p>{note}</p>

<div class="card">
  <p>
    <strong>Aktualnego kursu nie znajdziesz na tej stronie</strong> — i to
    celowo. Strona jest statyczna, a kurs zmienia się każdego dnia roboczego,
    więc opublikowana tu liczba szybko przestałaby być prawdziwa.
  </p>
  <p>
    Kurs pokazuje aplikacja <strong>Konwerter walut</strong>: pobiera go na
    bieżąco, oznacza numerem tabeli i datą publikacji, a obok rysuje wykres
    za miesiąc, kwartał albo rok.
  </p>
</div>

<h2>Co daje aplikacja</h2>
<ul>
  <li>przeliczanie {gen} na złote i odwrotnie, z kalkulatorem w środku,</li>
  <li>historię notowań na wykresie — miesiąc, kwartał, rok,</li>
  <li>działanie bez internetu na ostatnio pobranych danych,</li>
  <li>brak reklam, kont i śledzenia.</li>
</ul>

<p style="margin-top:2rem">
  <a href="/">Zobacz, jak działa aplikacja →</a>
</p>

<footer>
  CurrencyPilot · aplikacja informacyjna. Nie świadczy usług wymiany walut
  ani doradztwa finansowego. Kursy mają charakter referencyjny.
</footer>

</body>
</html>
"""


INDEX = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kursy walut — CurrencyPilot</title>
<meta name="description" content="Waluty, których kurs średni publikuje NBP w tabeli A. Aktualny kurs i historię notowań pokazuje aplikacja Konwerter walut.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://currencypilot.io/kurs">
<style>
  :root {{ color-scheme: light dark; --brand:#0a6fe8; --ink:#0d1117;
           --soft:#4a5568; --bg:#fff; --line:#dfe6f0; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --brand:#4d9dff; --ink:#e8ecf2; --soft:#9aa6b8; --bg:#0c0f14;
             --line:#232b36; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0 auto; padding:2rem 1.5rem 4rem; max-width:48rem;
         background:var(--bg); color:var(--ink);
         font:1rem/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
  a {{ color: var(--brand); }}
  .back {{ font-size:.9rem; margin:0 0 2rem; }}
  .back a {{ text-decoration:none; }}
  h1 {{ font-size:clamp(1.7rem,4vw,2.3rem); letter-spacing:-.03em; margin:0 0 .5rem; }}
  .lead {{ color:var(--soft); margin:0 0 2rem; max-width:36rem; }}
  ul {{ list-style:none; padding:0; margin:0;
       display:grid; grid-template-columns:repeat(auto-fill,minmax(14rem,1fr));
       gap:1px; background:var(--line); border:1px solid var(--line);
       border-radius:.75rem; overflow:hidden; }}
  li {{ background:var(--bg); }}
  li a {{ display:flex; justify-content:space-between; gap:1rem;
         padding:.85rem 1rem; text-decoration:none; color:var(--ink); }}
  li a:hover {{ background:var(--line); }}
  .kod {{ color:var(--soft); font-variant-numeric:tabular-nums; }}
  footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line);
           color:var(--soft); font-size:.9rem; }}
</style>
</head>
<body>

<p class="back"><a href="/">← CurrencyPilot</a></p>

<h1>Kursy walut</h1>
<p class="lead">
  Waluty, których kurs średni publikuje NBP w tabeli A. Aktualny kurs
  i historię notowań pokazuje aplikacja — te strony tylko ją opisują.
</p>

<ul>
{items}
</ul>

<footer>
  CurrencyPilot · aplikacja informacyjna. Nie świadczy usług wymiany walut
  ani doradztwa finansowego.
</footer>

</body>
</html>
"""


def fetch_currencies():
    with urllib.request.urlopen(TABLE_URL, timeout=20) as response:
        table = json.load(response)[0]
    return [(r["code"], r["currency"]) for r in table["rates"]]


def write_index(entries):
    """Spis wszystkich walut — bez niego podstrony sa sierotami.

    Strona, do ktorej nic nie linkuje, jest dla wyszukiwarki niewidoczna,
    a dla czlowieka nieosiagalna inaczej niz przez zgadniecie adresu.
    """
    items = "\n".join(
        f'  <li><a href="/kurs/{code.lower()}">'
        f'<span>{html.escape(clean)}</span>'
        f'<span class="kod">{html.escape(code)}</span></a></li>'
        for code, clean in entries
    )
    (OUT / "index.html").write_text(INDEX.format(items=items), encoding="utf-8")


def main():
    currencies = fetch_currencies()
    OUT.mkdir(parents=True, exist_ok=True)

    detailed = 0
    missing = []
    entries = []

    for code, name in currencies:
        # NBP dopisuje kraj w nawiasie ("jen (Japonia)") — w zdaniu zawadza,
        # wiec pokazujemy go osobno, w linijce pod naglowkiem.
        clean = re.sub(r"\s*\(.*?\)", "", name).strip()

        gen = GENITIVE.get(code)
        if gen is None:
            # Nowa waluta w tabeli: nie zgadujemy odmiany, tylko piszemy
            # zdanie, ktore jej nie potrzebuje.
            missing.append(f"{code} ({name})")
            gen = f"waluty {code}"
            gen_title = f"{clean} ({code})"
        else:
            gen_title = gen

        note = NOTES.get(code)
        if note:
            detailed += 1
        else:
            note = (
                f"{clean.capitalize()} ({code}) jest jedną z walut, których "
                f"kurs średni publikuje Narodowy Bank Polski w tabeli A."
            )

        page = PAGE.format(
            code=html.escape(code),
            slug=code.lower(),
            name=html.escape(name),
            gen=html.escape(gen),
            gen_title=html.escape(gen_title),
            note=html.escape(note),
            meta=html.escape(
                f"Kurs {gen} ({code}) — sprawdź aktualny kurs średni "
                f"i historię notowań w aplikacji Konwerter walut."
            ),
        )

        directory = OUT / code.lower()
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(page, encoding="utf-8")

        entries.append((code, clean))

    write_index(sorted(entries, key=lambda e: e[1]))

    print(f"  wygenerowano {len(currencies)} stron w {OUT.relative_to(ROOT)}/")
    print(f"  plus spis /kurs")
    print(f"  w tym {detailed} z wlasnym opisem, "
          f"{len(currencies) - detailed} z ogolnym")
    if missing:
        print("  UWAGA — brak odmiany w GENITIVE, dopisz recznie:")
        for item in missing:
            print(f"    {item}")


if __name__ == "__main__":
    main()
