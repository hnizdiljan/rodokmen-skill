# Zadání pomocníka (subagenta) – šablona a pravidla

Pravidla v SKILL.md (Pomocníci) platí dál; tady je, **co napsat do zadání**, aby výsledek šel ověřit. Osvědčilo se
na desítkách kol (kurent 18.–19. stol., latina, němčina). Společná pravidla dej do jednoho souboru
(`pracovni/ZADANI_POMOCNIK.md`) a v zadání každého pomocníka na něj jen odkaž.

## Šablona zadání
```markdown
# Pomocník <větev> – <co hledáš>
Píšeš jen do pracovni/pom_<větev>/ (do data/ nikdy). Pravidla: pracovni/ZADANI_POMOCNIK.md.

Cíl: <osoba, událost, odkud víme, co už v datech je (klíče zápisů)>
Svazky a snímky (uzavřený seznam – jiné neotevírej): <portál, id knihy, snímky od–do>
Rozpočet: nejvýš <N> obrázků, dávky po 20–25 snímcích.
Kontrolní zápis: <známý zápis ve stejné knize – klíč, snímek>. Najdi ho a přečti jako první.
  Když ho nenajdeš, napiš to a skonči – tvoje „nenalezeno“ by pak neplatilo.
Výsledek (vysledky.md, zapisuj průběžně po každém snímku/nálezu):
  1. tabulka snímků: snímek | stav (přečteno / nečitelné / nezobrazeno) | rok a první jméno na snímku
  2. nálezy: klíč | snímek | souřadnice zápisu (zlomky 0–1) | soubor výřezu, ze kterého jsi četl | přepis | jistota
  3. zjevně související výskyty (stopy, ne doklady)
  4. řádky do deníku – každé hledání vlastní řádek s rozsahem, i negativní
```

## Co musí být v pravidlech (`ZADANI_POMOCNIK.md`)
- **Nezobrazený snímek není negativní výsledek.** Nástroj na čtení obrázků občas místo obrázku vrátí „request limit“,
  „media removed“ nebo nic. Takový snímek zapiš jako „nezobrazeno“ a **nikdy o něm nepiš nic jiného** (ani „nic tam není“).
  Skutečně se stalo, že pomocník vyplnil „nálezy“ ze snímků, které neviděl; odhalila to až tabulka „co jsi na snímku přečetl“.
- Obrázek ke čtení zmenši na 1500–2000 px (větší se nezobrazí); jemné písmo čti z výřezu sloupce v plném rozlišení, ne
  z celé stránky (kurent na šířce ~1500 px celé stránky spolehlivě nepřečte nikdo).
- U každého čísla napiš, ze kterého sloupce je (číslo domu × pořadové číslo zápisu × folio).
- Souřadnice nálezu ověř výřezem z celého snímku – jinak ukazují na sousední zápis na téže stránce.
- U sňatků výslovně přečti stav snoubenců (svobodný / vdovec) a věk.
- Nejistá místa označ „(?)“ a podklad dokonči. Nečekej na pomoc se čtením – rozhodne hlavní sezení.
- Síť jen přes `tools/slusne.py`; při hlášce „zastavený“ (nebo 503/timeout bez brzdy) skonči s celým archivem a ohlas to.
- Technické pasti systému (Windows: `python -I -X utf8`, `magick`; macOS: zsh) – viz `matriky.md`.

## Jak výsledek přebírat
- Výsledek **přerušeného nebo obnoveného běhu** ber jako neověřený celý – i nálezy, které vypadají hotově.
- Bez nalezeného kontrolního zápisu neplatí „nenalezeno“. Ani s ním ho neber jako konečné u kurentu 18. a 1. poloviny
  19. století: levnější model tam přehlíží zápisy a vybírá kandidáty jen podle čísla domu. Silnější model s výřezem vzoru
  písma (stejné slovo od téhož písaře) uspěl tam, kde levnější selhal.
- Každý nález před zápisem ověř sám (`overit.py`); souřadnice pomocníků jsou někdy jen odhad – po kole udělej ke všem
  zápisům rámečky (`ramecek.py`) a projdi kontrolní obrázky najednou (rámeček o řádek vedle je častá chyba).
- Sporná slova dej **nezávislému druhému čtení** (viz `matriky.md` → Ověřování).
- Velký balík rodinných dokumentů (spis o stovkách snímků, PDF, překlady) rozděl mezi pomocníky po částech a chtěj jen
  údaje **nové nebo odlišné** proti datům, s cestou ke snímku. Rodinné překlady mívají chyby ve jménech a datech.
- Pomocníci, kteří mají „nejdřív hloubku, pak detaily“, na detaily (gruntovní knihy, noviny) nedojdou – zadej je jako
  samostatné kolo.
