"""Slowniki walut: adresy, odmiana, opisy.

Trzymamy je osobno od generatora, bo to dane redakcyjne — zmieniaja sie
z innych powodow niz kod i latwiej je przejrzec w jednym miejscu.

Slug jest fraza, ktorej ludzie faktycznie szukaja ("kurs euro",
"kurs korony czeskiej"), a nie kodem ISO. Kod zostaje w adresie tylko
tam, gdzie nazwa nic nie mowi (SDR).
"""

# kod ISO -> (slug adresu, dopelniacz, mianownik do naglowka tabeli)
CURRENCIES = {
    "EUR": ("kurs-euro", "euro", "euro"),
    "USD": ("kurs-dolara", "dolara amerykańskiego", "dolar amerykański"),
    "GBP": ("kurs-funta", "funta szterlinga", "funt szterling"),
    "CHF": ("kurs-franka", "franka szwajcarskiego", "frank szwajcarski"),
    "CZK": ("kurs-korony-czeskiej", "korony czeskiej", "korona czeska"),
    "NOK": ("kurs-korony-norweskiej", "korony norweskiej", "korona norweska"),
    "SEK": ("kurs-korony-szwedzkiej", "korony szwedzkiej", "korona szwedzka"),
    "DKK": ("kurs-korony-dunskiej", "korony duńskiej", "korona duńska"),
    "ISK": ("kurs-korony-islandzkiej", "korony islandzkiej", "korona islandzka"),
    "JPY": ("kurs-jena", "jena", "jen"),
    "CAD": ("kurs-dolara-kanadyjskiego", "dolara kanadyjskiego", "dolar kanadyjski"),
    "AUD": ("kurs-dolara-australijskiego", "dolara australijskiego", "dolar australijski"),
    "NZD": ("kurs-dolara-nowozelandzkiego", "dolara nowozelandzkiego", "dolar nowozelandzki"),
    "SGD": ("kurs-dolara-singapurskiego", "dolara singapurskiego", "dolar singapurski"),
    "HKD": ("kurs-dolara-hongkongu", "dolara Hongkongu", "dolar Hongkongu"),
    "HUF": ("kurs-forinta", "forinta", "forint"),
    "UAH": ("kurs-hrywny", "hrywny", "hrywna"),
    "TRY": ("kurs-liry", "liry tureckiej", "lira turecka"),
    "RON": ("kurs-leja", "leja rumuńskiego", "lej rumuński"),
    "ILS": ("kurs-szekla", "nowego izraelskiego szekla", "nowy izraelski szekel"),
    "CLP": ("kurs-peso-chilijskiego", "peso chilijskiego", "peso chilijskie"),
    "PHP": ("kurs-peso-filipinskiego", "peso filipińskiego", "peso filipińskie"),
    "MXN": ("kurs-peso-meksykanskiego", "peso meksykańskiego", "peso meksykańskie"),
    "ZAR": ("kurs-randa", "randa", "rand"),
    "BRL": ("kurs-reala", "reala brazylijskiego", "real brazylijski"),
    "MYR": ("kurs-ringgita", "ringgita", "ringgit"),
    "IDR": ("kurs-rupii-indonezyjskiej", "rupii indonezyjskiej", "rupia indonezyjska"),
    "INR": ("kurs-rupii-indyjskiej", "rupii indyjskiej", "rupia indyjska"),
    "KRW": ("kurs-wona", "wona południowokoreańskiego", "won południowokoreański"),
    "CNY": ("kurs-yuana", "yuana renminbi", "yuan renminbi"),
    "THB": ("kurs-bata", "bata tajlandzkiego", "bat tajlandzki"),
    "XDR": ("kurs-sdr", "SDR", "SDR (MFW)"),
}

# Kraj lub obszar — konkret, ktory odroznia strony od siebie.
COUNTRY = {
    "EUR": "strefa euro (20 krajów, m.in. Niemcy, Francja, Włochy, Słowacja)",
    "USD": "Stany Zjednoczone",
    "GBP": "Wielka Brytania",
    "CHF": "Szwajcaria i Liechtenstein",
    "CZK": "Czechy",
    "NOK": "Norwegia",
    "SEK": "Szwecja",
    "DKK": "Dania",
    "ISK": "Islandia",
    "JPY": "Japonia",
    "CAD": "Kanada",
    "AUD": "Australia",
    "NZD": "Nowa Zelandia",
    "SGD": "Singapur",
    "HKD": "Hongkong",
    "HUF": "Węgry",
    "UAH": "Ukraina",
    "TRY": "Turcja",
    "RON": "Rumunia",
    "ILS": "Izrael",
    "CLP": "Chile",
    "PHP": "Filipiny",
    "MXN": "Meksyk",
    "ZAR": "Republika Południowej Afryki",
    "BRL": "Brazylia",
    "MYR": "Malezja",
    "IDR": "Indonezja",
    "INR": "Indie",
    "KRW": "Korea Południowa",
    "CNY": "Chiny",
    "THB": "Tajlandia",
    "XDR": "Międzynarodowy Fundusz Walutowy",
}

# Zdanie, ktore ma sens tylko dla tej jednej waluty. Bez niego strony
# roznilyby sie samymi liczbami, a to dla wyszukiwarek tresc przelotowa.
NOTES = {
    "EUR": "Euro jest najczęściej przeliczaną walutą w Polsce — od zakupów "
           "w zagranicznych sklepach internetowych po rozliczanie wyjazdów "
           "służbowych.",
    "USD": "W dolarze rozliczana jest większość handlu międzynarodowego, "
           "surowce i usługi chmurowe, dlatego jego kurs śledzą także firmy "
           "nieprowadzące sprzedaży w USA.",
    "GBP": "Funt jest jedną z najdroższych walut w tabeli NBP — jego kurs "
           "do złotego od lat utrzymuje się powyżej czterech złotych.",
    "CHF": "Kurs franka śledzą w Polsce przede wszystkim osoby spłacające "
           "kredyty hipoteczne indeksowane do tej waluty.",
    "CZK": "Korona czeska to jedna z najczęściej przeliczanych walut przy "
           "wyjazdach weekendowych. Kurs podawany jest za jedną koronę, "
           "więc kwoty w czeskich sklepach dzieli się mniej więcej przez sześć.",
    "JPY": "NBP podaje kurs jena za sto jednostek. Przy ręcznym przeliczaniu "
           "łatwo o tym zapomnieć i pomylić się stukrotnie.",
    "HUF": "Kurs forinta NBP podaje za sto jednostek — podobnie jak przy jenie "
           "warto na to uważać przy ręcznym liczeniu.",
    "NOK": "Koronę norweską przelicza w Polsce głównie kilkadziesiąt tysięcy "
           "osób pracujących w Skandynawii.",
    "UAH": "Hrywna jest walutą Ukrainy. Jej kurs w tabeli NBP bywa istotny "
           "przy rozliczeniach transgranicznych i przekazach pieniężnych.",
    "SEK": "Korona szwedzka jest walutą Szwecji — kraju, który mimo "
           "członkostwa w Unii Europejskiej nie przyjął euro.",
    "DKK": "Korona duńska jest powiązana z euro stałym kursem centralnym, "
           "więc jej notowania do złotego zmieniają się podobnie jak euro.",
    "TRY": "Lira turecka od lat systematycznie traci na wartości, co widać "
           "na wykresie rocznym wyraźniej niż przy większości walut z tabeli.",
    "CAD": "Dolar kanadyjski bywa nazywany walutą surowcową — jego kurs "
           "często podąża za cenami ropy naftowej.",
    "AUD": "Dolar australijski jest walutą surowcową, powiązaną z eksportem "
           "rud żelaza i węgla.",
    "CNY": "Kurs yuana ma znaczenie dla firm importujących towary z Chin, "
           "choć rozliczenia i tak najczęściej odbywają się w dolarze.",
}
