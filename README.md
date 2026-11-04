# Cairn – spolszczenie

Nieoficjalne, fanowskie tłumaczenie gry Cairn (The Game Bakers) na język polski, razem z dodatkiem *On the Trail*.

- przetłumaczone ok. 3800 tekstów: interfejs, samouczki, przedmioty, przepisy, notatki, dialogi, osiągnięcia, napisy końcowe;
- dorobione polskie znaki (ą ć ę ł ń ó ś ź ż, wielkie litery oraz „ ‚) we wszystkich pięciu krojach czcionki gry;
- celowo bez tłumaczenia zostały imiona, nazwy własne, marki w napisach końcowych i teksty debugowe.

Polski zastępuje w grze **język włoski** – gra nie pozwala dodać nowego języka bez zmian w kodzie. Po instalacji wybierz w grze: **Ustawienia → Język → Polski**.

Repozytorium nie zawiera żadnych plików gry. Skrypty modyfikują pakiety z Twojej własnej instalacji.

## Instalacja

Wymagania: Python 3 i Bash (np. Git Bash na Windows).

```bash
pip install -r requirements.txt
```

```bash
./install.sh "C:/Program Files (x86)/Steam/steamapps/common/Cairn"
```

Skrypt przy pierwszym uruchomieniu zapisuje kopię oryginalnych pakietów włoskich w `backup/`, buduje polskie pakiety w `build/` i kopiuje je do gry. Po aktualizacji gry ze Steama, która nadpisze pliki, uruchom go ponownie.

Usunięcie spolszczenia (przywrócenie włoskiego):

```bash
./restore.sh "C:/Program Files (x86)/Steam/steamapps/common/Cairn"
```

Po aktualizacji gry kopia w `backup/` może być nieaktualna – wtedy zamiast `restore.sh` użyj w Steamie opcji „Zweryfikuj spójność plików gry”.

## Struktura

| Ścieżka | Zawartość |
| --- | --- |
| `translation/pl/000–024.txt` | tłumaczenie: `@@N` w osobnej linii, pod nim tekst; N to numer unikalnego angielskiego tekstu w kolejności z pakietu `localizationen` |
| `tools/patch_loc.py` | sprawdza tagi, zmienne `{0}` i dozwolone znaki, a potem buduje pakiet `localizationit` z polskimi tekstami (brakujące zostają po angielsku) |
| `tools/patch_fonts.py` | dopisuje polskie glify do pakietu `dynamicfontsit` |
| `tools/pl_glyphs.pkl.xz` | gotowe glify SDF |
| `tools/build_fonts.py`, `sdflib.py`, `synth.py` | generowanie glifów (wymaga czcionek i atlasów wyciągniętych z gry do `fontsx/`) |

Sprawdzenie tłumaczenia bez budowania pakietów:

```bash
python -X utf8 tools/patch_loc.py "<gra>/Cairn_Data/StreamingAssets/aa/StandaloneWindows64/localizationen_assets_all.bundle"
```

## Uwagi do tłumaczenia

- Ozdobna czcionka nagłówków ekranu podsumowania (`Cairn_LogoFont`) jest wspólna dla wszystkich języków i nie ma polskich liter, dlatego te nagłówki („gratulacje”, „Omdlenie”, „Fatalny upadek”) są dobrane tak, by ich nie zawierały.
- Aava mówi w formie żeńskiej; w dodatku *On the Trail*, gdzie można grać Markiem, komunikaty systemowe są neutralne.

Cairn jest znakiem towarowym The Game Bakers. Projekt nie jest powiązany z twórcami gry.
