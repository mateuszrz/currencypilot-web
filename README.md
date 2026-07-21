# currencypilot.io

Strona wizytówka aplikacji **Konwerter walut** (marka CurrencyPilot) wraz
z polityką prywatności wymaganą przez Google Play.

Czysty statyczny HTML — bez builda, bez zależności, bez JavaScriptu. Otwórz
`index.html` w przeglądarce, żeby zobaczyć zmiany lokalnie.

```
index.html          # strona główna
privacy/index.html  # polityka prywatności → /privacy
favicon.svg         # ikona (te same strzałki, co ikona aplikacji)
og.png              # obrazek do podglądu w social media (1024×500)
vercel.json         # czyste adresy URL + nagłówki bezpieczeństwa
```

## Deploy

Hosting: Vercel, podłączony do tego repo. **Każdy push na `main` publikuje
produkcję**, push na inną gałąź tworzy podgląd pod tymczasowym adresem.

Ustawienia w panelu Vercela: Framework Preset **Other**, Build Command i
Output Directory puste — pliki idą na serwer takie, jakie są.

## Skąd bierze się polityka prywatności

Źródłem jest `store/privacy/index.html` w prywatnym repo aplikacji
(`currencyconverterplus`). Po zmianie tam trzeba skopiować plik tutaj —
adres `/privacy` jest wpisany w Google Play Console, więc treść musi się
zgadzać z tym, co robi opublikowana wersja aplikacji.

## Uwaga o treści

Strona nie może obiecywać więcej, niż aplikacja robi. Dopóki aplikacja nie
jest opublikowana, hero mówi „wkrótce w Google Play" — po publikacji trzeba
zamienić ten napis na odnośnik do sklepu.
