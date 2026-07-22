"""English currency dictionaries: slugs, names, countries, notes.

English pages use ECB reference rates, so the base currency is the euro and
each page answers "how much is 1 X in euro" — the phrase people actually
search ("pound to euro", "swiss franc to euro"). The euro itself is the base,
so it gets its own hub page instead of an "X to euro" entry.

Kept separate from the generator: this is editorial data that changes for
different reasons than code.
"""

# ISO code -> (url slug, English name, country/area)
CURRENCIES_EN = {
    "USD": ("us-dollar-to-euro", "US dollar", "the United States"),
    "GBP": ("pound-to-euro", "pound sterling", "the United Kingdom"),
    "CHF": ("swiss-franc-to-euro", "Swiss franc", "Switzerland and Liechtenstein"),
    "JPY": ("japanese-yen-to-euro", "Japanese yen", "Japan"),
    "PLN": ("polish-zloty-to-euro", "Polish zloty", "Poland"),
    "CZK": ("czech-koruna-to-euro", "Czech koruna", "Czechia"),
    "SEK": ("swedish-krona-to-euro", "Swedish krona", "Sweden"),
    "NOK": ("norwegian-krone-to-euro", "Norwegian krone", "Norway"),
    "DKK": ("danish-krone-to-euro", "Danish krone", "Denmark"),
    "ISK": ("icelandic-krona-to-euro", "Icelandic krona", "Iceland"),
    "HUF": ("hungarian-forint-to-euro", "Hungarian forint", "Hungary"),
    "RON": ("romanian-leu-to-euro", "Romanian leu", "Romania"),
    "BGN": ("bulgarian-lev-to-euro", "Bulgarian lev", "Bulgaria"),
    "TRY": ("turkish-lira-to-euro", "Turkish lira", "Turkiye"),
    "AUD": ("australian-dollar-to-euro", "Australian dollar", "Australia"),
    "CAD": ("canadian-dollar-to-euro", "Canadian dollar", "Canada"),
    "NZD": ("new-zealand-dollar-to-euro", "New Zealand dollar", "New Zealand"),
    "SGD": ("singapore-dollar-to-euro", "Singapore dollar", "Singapore"),
    "HKD": ("hong-kong-dollar-to-euro", "Hong Kong dollar", "Hong Kong"),
    "CNY": ("chinese-yuan-to-euro", "Chinese yuan renminbi", "China"),
    "INR": ("indian-rupee-to-euro", "Indian rupee", "India"),
    "IDR": ("indonesian-rupiah-to-euro", "Indonesian rupiah", "Indonesia"),
    "KRW": ("south-korean-won-to-euro", "South Korean won", "South Korea"),
    "MYR": ("malaysian-ringgit-to-euro", "Malaysian ringgit", "Malaysia"),
    "PHP": ("philippine-peso-to-euro", "Philippine peso", "the Philippines"),
    "THB": ("thai-baht-to-euro", "Thai baht", "Thailand"),
    "ILS": ("israeli-shekel-to-euro", "Israeli new shekel", "Israel"),
    "MXN": ("mexican-peso-to-euro", "Mexican peso", "Mexico"),
    "BRL": ("brazilian-real-to-euro", "Brazilian real", "Brazil"),
    "ZAR": ("south-african-rand-to-euro", "South African rand", "South Africa"),
}

# A sentence that only makes sense for this one currency, so pages differ by
# more than numbers. Optional — only where there is something concrete to say.
NOTES_EN = {
    "USD": "The US dollar is the currency most international trade is settled "
           "in, so its rate against the euro is watched well beyond the "
           "United States.",
    "GBP": "Sterling and the euro are the two most-traded currencies for "
           "cross-Channel travel, shopping and payroll between the UK and the "
           "euro area.",
    "CHF": "The Swiss franc is treated as a safe-haven currency, so it often "
           "strengthens against the euro when markets turn nervous.",
    "JPY": "The ECB quotes the yen per one euro, so the euro value of a single "
           "yen is a small fraction — easy to misplace a decimal by hand.",
    "PLN": "Poland is in the EU but keeps the zloty rather than the euro, so "
           "the PLN/EUR rate matters for cross-border shopping and payments.",
    "CZK": "Czechia keeps the koruna rather than the euro; the rate is handy "
           "for weekend trips and online shopping across the border.",
    "SEK": "Sweden is an EU member that has not adopted the euro, so the krona "
           "floats freely against it.",
    "NOK": "Norway sits outside the EU, and the krone often tracks oil prices "
           "as much as it tracks the euro.",
    "DKK": "The Danish krone is pegged to the euro within a narrow band, so "
           "its rate barely moves compared with other currencies here.",
    "TRY": "The Turkish lira has lost value against the euro steadily for "
           "years, which shows up on the yearly chart more sharply than for "
           "most currencies.",
}
