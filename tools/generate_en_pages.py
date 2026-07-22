"""Generates the English currency pages under /en/.

English pages use ECB reference rates (base = euro), matching what the app
shows for English users. Each currency gets a "1 X = Y EUR" page; the euro
itself is the hub at /en/ that lists "1 EUR = Y X" and links out.

Static HTML, no JavaScript — search engines see the same numbers a person
does. Rebuilt daily by the same workflow as the Polish pages, after the ECB
publishes (around 16:00 CET on business days).

Run:      python tools/generate_en_pages.py
Requires: access to www.ecb.europa.eu
"""

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlopen

from currencies_en import CURRENCIES_EN, NOTES_EN

DAILY = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
HIST = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"
ROOT = Path(__file__).resolve().parent.parent

HISTORY_DAYS = 30
TABLE_ROWS = 10
AMOUNTS = [1, 10, 50, 100, 500, 1000]

# Currencies shown on the euro hub page (1 EUR = Y X), the ones people look up.
HUB = ["USD", "GBP", "CHF", "JPY", "PLN", "SEK", "NOK", "CZK", "CAD", "AUD"]


def fetch_days(url):
    """ECB XML -> list of (date, {code: rate per 1 EUR}), oldest first."""
    with urlopen(url, timeout=30) as response:
        root = ET.fromstring(response.read())

    days = []
    for element in root.iter():
        if element.tag.endswith("Cube") and "time" in element.attrib:
            rates = {
                child.attrib["currency"]: float(child.attrib["rate"])
                for child in element
                if "currency" in child.attrib and "rate" in child.attrib
            }
            days.append((element.attrib["time"], rates))
    days.sort(key=lambda d: d[0])
    return days


def en_number(value, places=4):
    """English format: comma thousands, dot decimal — Python's default."""
    return f"{value:,.{places}f}"


def en_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def sparkline(points, width=680, height=160):
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
        f'aria-label="Exchange rate over the last {len(points)} quotes">'
        f'<polygon points="{area}" fill="var(--fill)"/>'
        f'<polyline points="{line}" fill="none" stroke="var(--brand)" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
        f"</svg>"
    )


def build_currency_page(code, per_eur, series_eur, effective):
    slug, name, country = CURRENCIES_EN[code]
    note = NOTES_EN.get(code)

    # We store the euro value of one unit of the currency (ECB quotes the
    # other way round: units of the currency per one euro).
    mid = 1 / per_eur

    change_html = ""
    if len(series_eur) >= 2:
        first = series_eur[0][1]
        if first:
            pct = (mid - first) / first * 100
            direction = "risen" if pct >= 0 else "fallen"
            change_html = (
                f"<p>Over the last {len(series_eur)} quotes the {name} has "
                f"{direction} <strong>{en_number(abs(pct), 2)}%</strong> "
                f"against the euro — from {en_number(first)} to "
                f"{en_number(mid)} EUR.</p>"
            )

    rows = "\n".join(
        f"<tr><td>{en_date(day)}</td><td>{en_number(value)} EUR</td></tr>"
        for day, value in reversed(series_eur[-TABLE_ROWS:])
    )

    conversions = "\n".join(
        f"<tr><td>{en_number(amount, 0)} {code}</td>"
        f"<td>{en_number(amount * mid, 2)} EUR</td></tr>"
        for amount in AMOUNTS
    )

    structured = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "ExchangeRateSpecification",
            "currency": code,
            "currentExchangeRate": {
                "@type": "UnitPriceSpecification",
                "price": round(mid, 4),
                "priceCurrency": "EUR",
            },
            "url": f"https://currencypilot.io/en/{slug}",
        },
        ensure_ascii=False,
    )

    return PAGE_EN.format(
        code=html.escape(code),
        slug=slug,
        name=html.escape(name),
        name_title=html.escape(name[:1].upper() + name[1:]),
        country=html.escape(country),
        note_block=f"<p>{html.escape(note)}</p>" if note else "",
        mid=en_number(mid),
        effective=en_date(effective),
        change=change_html,
        rows=rows,
        conversions=conversions,
        chart=sparkline(series_eur),
        structured=structured,
    )


PAGE_EN = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name_title} to euro ({code}) — {mid} EUR · CurrencyPilot</title>
<meta name="description" content="{name_title} to euro on {effective}: 1 {code} = {mid} EUR. ECB reference rate, history and a converter.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://currencypilot.io/en/{slug}">
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

<p class="back"><a href="/en/">← CurrencyPilot</a> · <a href="/en/">all currencies</a> · <a href="/">Polski</a></p>

<h1>{name_title} to euro ({code})</h1>

<div class="now">
  <div class="rate">1 {code} = {mid} EUR</div>
  <p class="meta">ECB reference rate · {effective}</p>
  {chart}
</div>

{change}
{note_block}
<p>
  The {name} is the currency of {country}. The European Central Bank publishes
  a reference rate against the euro on business days at around 16:00 CET.
</p>

<h2>How much is it in euro</h2>
<table>
  <thead><tr><th>Amount</th><th>Value in euro</th></tr></thead>
  <tbody>
{conversions}
  </tbody>
</table>
<p class="meta">Converted at the reference rate from {effective}.</p>

<h2>Recent quotes</h2>
<table>
  <thead><tr><th>Date</th><th>Rate (EUR)</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>

<div class="cta">
  <p>
    <strong>The rate changes every day.</strong> This page shows the quote from
    {effective} and is refreshed every business day after the ECB publishes.
  </p>
  <p>
    Want the live rate with a calculator and chart on your phone —
    <a href="/">get the CurrencyPilot app</a>. It works offline too, on the
    last downloaded rates.
  </p>
</div>

<h2>FAQ</h2>
<p>
  <strong>Is this the rate I get at a bank or exchange office?</strong><br>
  No. The ECB reference rate is a benchmark used for accounting and reporting.
  Banks and exchange offices add their own margin, so buying costs more and
  selling pays less.
</p>
<p>
  <strong>When does a new rate appear?</strong><br>
  The ECB publishes reference rates on business days at around 16:00 CET. On
  weekends and holidays the last published rate applies.
</p>

<footer>
  Data: European Central Bank, euro reference rates. CurrencyPilot is not
  affiliated with the ECB. Rates are informational — not an offer or financial
  advice.
</footer>

</body>
</html>
"""


INDEX_EN = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Euro exchange rate — ECB rates from {effective} · CurrencyPilot</title>
<meta name="description" content="Euro reference rates from the ECB, {effective}. 1 EUR to USD, GBP, CHF and more, each with history and a converter.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://currencypilot.io/en/">
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
  h2 {{ font-size:1.2rem; margin:2.5rem 0 .75rem; letter-spacing:-.02em; }}
  .meta {{ color:var(--soft); margin:0 0 2rem; }}
  table {{ width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; }}
  th, td {{ text-align:left; padding:.6rem .5rem; border-bottom:1px solid var(--line); }}
  th {{ color:var(--soft); font-weight:600; font-size:.85rem;
       text-transform:uppercase; letter-spacing:.05em; }}
  td:last-child, th:last-child {{ text-align:right; }}
  td a {{ text-decoration:none; }}
  .code {{ color:var(--soft); font-size:.85rem; }}
  footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line);
           color:var(--soft); font-size:.85rem; }}
</style>
</head>
<body>

<p class="back"><a href="/en/">← CurrencyPilot</a> · <a href="/">Polski</a></p>

<h1>Euro exchange rate</h1>
<p class="meta">ECB reference rates · {effective}</p>

<h2>1 EUR in other currencies</h2>
<table>
  <thead><tr><th>Currency</th><th>Rate</th></tr></thead>
  <tbody>
{hub_rows}
  </tbody>
</table>

<h2>All currencies to euro</h2>
<table>
  <thead><tr><th>Currency</th><th>Value in euro</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>

<footer>
  Data: European Central Bank, euro reference rates. Refreshed every business
  day after publication. CurrencyPilot is not affiliated with the ECB.
</footer>

</body>
</html>
"""


def merge_sitemap(slugs, effective):
    """Add the English URLs to sitemap.xml.

    The Polish generator rewrites sitemap.xml fresh (Polish only) each run, so
    we strip any stale /en/ entries and append the current ones before the
    closing tag. The workflow runs the Polish step first, then this one.
    """
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r"  <url>\n    <loc>https://currencypilot\.io/en[^<]*</loc>\n"
        r"    <lastmod>[^<]*</lastmod>\n    <priority>[^<]*</priority>\n  </url>\n",
        "",
        text,
    )

    entries = [("https://currencypilot.io/en/", "0.8")] + [
        (f"https://currencypilot.io/en/{slug}", "0.7") for slug in slugs
    ]
    body = "".join(
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{effective}</lastmod>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>\n"
        for loc, priority in entries
    )

    path.write_text(text.replace("</urlset>", body + "</urlset>"), encoding="utf-8")
    return len(entries)


def main():
    today = fetch_days(DAILY)[-1]
    effective, rates = today
    history = fetch_days(HIST)

    def series_for(code):
        points = [
            (day, 1 / day_rates[code])
            for day, day_rates in history
            if code in day_rates and day_rates[code]
        ]
        return points[-HISTORY_DAYS:]

    written = 0
    index_rows = []

    for code, (slug, name, _country) in CURRENCIES_EN.items():
        per_eur = rates.get(code)
        if per_eur is None:
            print(f"  skipped {code} — not in today's ECB table")
            continue

        page = build_currency_page(code, per_eur, series_for(code), effective)
        directory = ROOT / "en" / slug
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(page, encoding="utf-8")
        written += 1

        index_rows.append(
            (name, f'<tr><td><a href="/en/{slug}">{html.escape(name)}</a>'
                   f' <span class="code">{code}</span></td>'
                   f'<td>{en_number(1 / per_eur)} EUR</td></tr>')
        )

    hub_rows = "\n".join(
        f'<tr><td>{html.escape(CURRENCIES_EN[code][1])} '
        f'<span class="code">{code}</span></td>'
        f"<td>{en_number(rates[code])}</td></tr>"
        for code in HUB
        if code in rates
    )

    index = INDEX_EN.format(
        effective=en_date(effective),
        hub_rows=hub_rows,
        rows="\n".join(row for _, row in sorted(index_rows)),
    )
    (ROOT / "en").mkdir(parents=True, exist_ok=True)
    (ROOT / "en" / "index.html").write_text(index, encoding="utf-8")

    slugs = [CURRENCIES_EN[c][0] for c in CURRENCIES_EN if c in rates]
    urls = merge_sitemap(slugs, effective)

    print(f"  ECB reference rates from {en_date(effective)}")
    print(f"  wrote {written} English currency pages + /en/ hub")
    print(f"  English URLs added to sitemap.xml: {urls}")


if __name__ == "__main__":
    main()
