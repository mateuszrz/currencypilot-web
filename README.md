# currencypilot.io

Strona wizytówka aplikacji **Konwerter walut** (marka CurrencyPilot) wraz
z polityką prywatności wymaganą przez Google Play.

Czysty statyczny HTML — bez builda, bez zależności, bez JavaScriptu. Otwórz
`index.html` w przeglądarce, żeby zobaczyć zmiany lokalnie.

```
index.html                   # strona główna
privacy/index.html           # polityka prywatności → /privacy
kurs-euro/, kurs-dolara/…    # 32 strony kursów (generowane)
kursy-walut/                 # spis wszystkich walut (generowany)
shots/*.webp                 # zrzuty aplikacji (tools/prepare_shots.py)
favicon.svg                  # ikona (te same strzałki, co ikona aplikacji)
og.png                       # obrazek do podglądu w social media
vercel.json                  # nagłówki + przekierowania (generowane)
.well-known/assetlinks.json  # weryfikacja App Links dla aplikacji
tools/currencies.py          # słowniki: adresy, odmiana, opisy walut
```

## Strony kursów

`python tools/generate_currency_pages.py` pobiera tabelę A z NBP i buduje
stronę dla każdej waluty: aktualny kurs, wykres, tabelę ostatnich notowań,
gotowe przeliczenia i dane strukturalne schema.org. Wszystko w HTML-u, bez
JavaScriptu — wyszukiwarka widzi te same liczby co człowiek.

**Strony przebudowują się codziennie** (`.github/workflows/kursy.yml`,
11:00 i 13:00 UTC w dni robocze — dwie godziny, bo Polska zmienia czas,
a tabela wychodzi ok. 12:15). Gdy tabela się nie zmieniła, workflow nie
robi commita.

Adresy są frazami, których ludzie szukają (`/kurs-korony-czeskiej/`),
a nie kodami ISO. Mapowanie kod → adres siedzi w `tools/currencies.py`
i **musi zgadzać się ze słownikiem `slugs` w `lib/services/deep_links.dart`
w repozytorium aplikacji** — inaczej linki z aplikacji trafią w pustkę.
Przekierowania ze starych adresów `/kurs/<kod>` generują się do
`vercel.json` z tego samego słownika.

## Strony po angielsku (`/en/`)

`python tools/generate_en_pages.py` buduje angielski odpowiednik na danych
**EBC** (baza EUR) — spójnie z aplikacją, która dla języka angielskiego też
sięga po EBC. Strony to `/en/<waluta>-to-euro/` („1 X = Y EUR"), a `/en/`
jest hubem euro („1 EUR = Y X") i spisem. Słowniki w `tools/currencies_en.py`.

Źródłem jest oficjalny `eurofxref-daily.xml` (bieżący kurs) i
`eurofxref-hist-90d.xml` (historia). EBC publikuje ~16:00 CET, więc workflow
odświeża angielskie strony w osobnych porach (14:30 i 15:30 UTC) niż polskie.
Generator EN uruchamia się **po** polskim, bo dokłada swoje adresy do
`sitemap.xml` zapisanego przez tamten.

Polskie i angielskie strony **nie są tłumaczeniami** — mają inną walutę bazową
(PLN vs EUR), więc nie łączymy ich znacznikiem `hreflang`. Krzyżowe linki
językowe (PL↔EN) są tylko widoczne, w nagłówkach.

## App Links

Aplikacja przechwytuje adresy stron kursów i otwiera na nich ekran waluty.
Żeby Android robił to bez pytania użytkownika, musi znaleźć pod
`/.well-known/assetlinks.json` odcisk certyfikatu, którym aplikacja jest
podpisana.

**Po pierwszym wydaniu w Google Play trzeba dopisać tam drugi odcisk.**
Play App Signing podpisuje wydawaną aplikację własnym kluczem Google, innym
niż nasz klucz do wysyłki. Odcisk znajdziesz w Play Console → *Integralność
aplikacji → Podpisywanie aplikacji → Certyfikat klucza podpisywania*.
Do czasu dopisania tego odcisku App Links zadziałają tylko dla plików APK
instalowanych ręcznie, a nie dla wersji pobranej ze sklepu.

Weryfikacja po stronie telefonu:

```powershell
adb shell pm verify-app-links --re-verify io.currencypilot.app
adb shell pm get-app-links io.currencypilot.app
```

## Deploy

Hosting: Vercel, podłączony do tego repo. **Każdy push na `main` publikuje
produkcję**, push na inną gałąź tworzy podgląd pod tymczasowym adresem.

Ustawienia w panelu Vercela: Framework Preset **Other**, Build Command i
Output Directory puste — pliki idą na serwer takie, jakie są.

## Skąd bierze się polityka prywatności

Źródłem treści jest `store/privacy/index.html` w prywatnym repo aplikacji
(`currencyconverterplus`). Adres `/privacy` jest wpisany w Google Play Console,
więc treść musi się zgadzać z tym, co robi opublikowana wersja aplikacji.

**Nie kopiuj pliku 1:1.** Tutejsza wersja ma dodatkowy „chrome" strony,
którego źródło nie ma: inny `<title>` (CurrencyPilot, nie „Konwerter walut"),
`<link rel="canonical">`, favicon i link powrotny `← CurrencyPilot`. Nadpisanie
pliku źródłem skasowałoby te elementy. Przy zmianie polityki **nanieś te same
zmiany treści na oba pliki** (sekcje merytoryczne są identyczne), zostawiając
tutejszy chrome nietknięty. Pamiętaj też podbić numer wersji i datę w obu.

## Uwaga o treści

Strona nie może obiecywać więcej, niż aplikacja robi. Dopóki aplikacja nie
jest opublikowana, hero mówi „wkrótce w Google Play" — po publikacji trzeba
zamienić ten napis na odnośnik do sklepu.
