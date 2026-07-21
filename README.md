# currencypilot.io

Strona wizytówka aplikacji **Konwerter walut** (marka CurrencyPilot) wraz
z polityką prywatności wymaganą przez Google Play.

Czysty statyczny HTML — bez builda, bez zależności, bez JavaScriptu. Otwórz
`index.html` w przeglądarce, żeby zobaczyć zmiany lokalnie.

```
index.html                 # strona główna
privacy/index.html         # polityka prywatności → /privacy
shots/*.webp               # zrzuty aplikacji (tools/prepare_shots.py)
favicon.svg                # ikona (te same strzałki, co ikona aplikacji)
og.png                     # obrazek do podglądu w social media (1024×500)
vercel.json                # czyste adresy URL + nagłówki bezpieczeństwa
.well-known/assetlinks.json  # weryfikacja App Links dla aplikacji
```

## App Links (`/kurs/<kod>`)

Aplikacja przechwytuje adresy `https://currencypilot.io/kurs/eur` i otwiera
na nich ekran waluty. Żeby Android otwierał je bez pytania użytkownika, musi
znaleźć pod `/.well-known/assetlinks.json` odcisk certyfikatu, którym
aplikacja jest podpisana.

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

Źródłem jest `store/privacy/index.html` w prywatnym repo aplikacji
(`currencyconverterplus`). Po zmianie tam trzeba skopiować plik tutaj —
adres `/privacy` jest wpisany w Google Play Console, więc treść musi się
zgadzać z tym, co robi opublikowana wersja aplikacji.

## Uwaga o treści

Strona nie może obiecywać więcej, niż aplikacja robi. Dopóki aplikacja nie
jest opublikowana, hero mówi „wkrótce w Google Play" — po publikacji trzeba
zamienić ten napis na odnośnik do sklepu.
