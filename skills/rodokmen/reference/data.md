# Formát dat projektu

Všechna data jsou v `data/`. Web se z nich generuje (`npm run data`), nikdy needituj `web/src/data/site.json` ručně.
Po změnách spusť `python3 -I tools/kontrola.py`. Ukázku vyplněných dat má `SKILL_DIR/template/ukazka/`.
Položky do JSON souborů přidávej a měň přes `python3 -I tools/zapis.py` (zachová formát souboru, viz SKILL.md).

## `osoby.py` – předci
Kekulého čísla: 1 = výchozí osoba, otec osoby n = 2n, matka = 2n+1.
| číslo | kdo |
|---|---|
| 1 | výchozí osoba (u ženy `sex="F"`) |
| 2, 3 | otec, matka |
| 4–7 | prarodiče (4, 5 otcovi rodiče; 6, 7 matčini) |
| 8–15 | pradědečci a prababičky = **8 rodů** (`LINES`) |
| 16–31, 32–63 … | každá další generace dvojnásobek |

Otec předka 22 je 44, matka 45; dítě předka 45 je 22 (45 // 2). Muži mají sudá čísla.

```python
P = {
 8: dict(n="Jan Novák", y="1890–1944", st="doc",
         f=["* 14. 2. 1890 Holice čp. 112", "kovář", "× 20. 6. 1919 Holice Josefa Pokorná", "† 1944 Holice"],
         r=["holice_krest_jan_novak_1890", "holice_snatek_jan_novak_josefa_pokorna_1919"],
         note="Proč nejistota / rozpor / odkud údaj"),
 9: dict(n="Josefa Pokorná", y="* 1895", st="doc", f=[...], r=[...]),
 33: dict(n="otec neuveden", st="unk", f=[], note="Nemanželský syn; otec v matrice není."),
}
```
- `n` jméno (ženy rodným příjmením), `y` roky pro přehledy (`"* 1895"`, `"1890–1944"`, `"asi 1720–1785"`, `"1680 – před 1740"`,
  `"† 1940"` když známe jen úmrtí; nic nevíme → `""`).
- `zap` (volitelné) – tvary jména, jak stojí v zápisech: `zap=["Catharina Nowakin", "Kateřina Nováková"]`.
  Na stránce osoby se ukážou jako „V zápisech zapsána jako …“; s `"puvodni_jmena": true` ve `web.json` se jimi osoba
  i jmenuje (web, vějíř, mapa domů, statistiky). Adresa stránky zůstává podle `n`.
- `f` fakta: začínají `*` (narození), `×` (sňatek), `†` (úmrtí) nebo jsou volný text (řemeslo, bydliště).
  Názvy obcí ve faktech používá mapa (`mista.json` → `re`).
- `r` klíče zápisů ze `zaznamy.json`. `st` viz `matriky.md`: `doc` přečteno v matrice, `prob` pravděpodobné,
  `fam` od rodiny (i strom, který si rodina vede sama, např. GEDCOM z jejího MyHeritage), `mh` cizí strom z internetu, `unk`.
- `vyz` (volitelné) – krátký popis, proč je předek významný (farář, starosta, legionář…); jde na stránku „Osobnosti“ nahoru.
  Bez něj stránka vybírá osobnosti sama podle slov ve faktech (`tools/osobnosti.py`).
- `LINES = {8: ("Novákové", "Kováři z Holic…"), …}` – jen čísla 8–15; název rodu = příjmení v množném čísle.
- `RODINA` – osoby mimo přímou linii (sourozenci předků, jejich partneři a děti, předci partnerů):
  `"zkratka": dict(n="Marie Nováková", y="1892–1970", sex="F", otec=16, matka=17, partner=[...], st="doc", f=[...], r=[...], note="…")`.
  `otec`/`matka` = číslo přímého předka nebo zkratka jiné osoby z RODINA; sourozenec předka 8 má `otec=16, matka=17`
  i když 16/17 ještě neznáme. `partner` jen pro partnery bez společného dítěte. Stromový graf (`/strom/`) z nich skládá
  rozklikávací větve – od sourozence předka třeba až do 20. století; na stránce osoby se ukážou jako příbuzní.
  Žijící jen jménem a rokem narození. U předka v `P` lze zapsat `sour="hotovo"` / `"částečně"` (stav hledání sourozenců).
- `SIDE` – jen poznámky, které do RODINA nejdou (nejistý vztah, celá větev jednou větou):
  `dict(k=<číslo předka>, n="…", v="příbuzný (?)", y="…", t="text", r=[klíče])` – ve stromu jako „pozn.“ u předka.
  Nedoloženou samostatnou rodinu nepřipojuj do hlavního stromu (ani do `RODINA`); jako `SIDE` ji veď jen jako
  výslovně označenou stopu u konkrétního možného příbuzného. Jinak ji ponech odděleně v deníku.
- `ISSUES` – dvojice `("Otázka", "Vyřešeno: … / Hypotéza: … / Otevřené: …")` → stránka „Co hledáme“ (vyřešené se skryjí).
  Nebo `dict(otazka="…", stav="Otevřené: …", osoby=[12, 13], prosle=[41, 57])`: `osoby` = čísla osob, kterých se otázka týká,
  `prosle` = čísla řádků deníku s už prověřenými (i neúspěšnými) cestami – export je přidá k otázce (`site.json`: `people`,
  `checked`), `kontrola.py` ohlídá, že osoby i řádky existují. Po neúspěšném hledání k otevřené otázce přidej číslo řádku.
  Jde na web – nepiš sem citlivé věci (příčiny úmrtí, rodinné spory) bez souhlasu.
- `HYPOTEZY` – `dict(rod=8, nadpis="…", text="…", polozky=[("jméno", "text")], zaznamy=[klíče])` → stránka rodu.
- `SAME = {350: 140}` – předek, který je v rodokmenu dvakrát (alias → hlavní číslo; alias v `P` může mít `f=["TÁŽ OSOBA jako 140"]`,
  ale nemusí). Předky nad aliasem (700, 701 …) znovu nezapisuj – vějíř, rodokmen na úvodu i rody je ukážou na obou místech
  podle hlavního čísla (`tools/implex.py`).

## `zaznamy.json` – zápisy
```json
[{"klic": "holice_krest_jan_novak_1890", "svazek": "1a0b2337", "snimek": 57, "druh": "N",
  "datum": "14. 2. 1890", "nazev": "Křest Jana Nováka",
  "shrnuti": "Jan, syn Václava Nováka, kováře v Holicích čp. 112, a Barbory roz. Malé z Ostřetína.",
  "odkaz": "https://aron.vychodoceskearchivy.cz/apu/…/dao/…/file/…"}]
```
- `klic`: malá písmena bez diakritiky, `obec_druh_kdo_rok` (druh: krest, snatek, umrti, index, scitani…). Je to i název obrázku.
- `druh`: N, O, Z, I (index/rejstřík), S (sčítání), J (jiný pramen – noviny, vojenské databáze, gruntovní knihy, ale i
  doklady z rodiny: výpis z matriky, úmrtní list, dopis, odpověď archivu). U rodinného dokladu `snimek` a `odkaz` vynech
  a ve `svazky.json` ho veď jako „rodinný archiv“ bez `url`; výřez udělej ze skenu dokladu. Upozornění `kontrola.py`
  „chybí odkaz na snímek“ je u takového zápisu v pořádku.
- `datum` jako v češtině („14. 2. 1890“, „3/1867“, „1797“) – web podle něj řadí.
- `shrnuti` je stručný obsahový souhrn, ne doslovný přepis. Při předání výzkumu bez originálního snímku nepřepisuj
  souhrn jako `orig` v `prepisy.json` a nevyráběj výřez ani rámeček; chybějící podklady výslovně poznamenej.
  `kontrola.py` má dál hlásit chybějící výřez nebo přepis.
- `"bez_vyrezu": true` – zápis záměrně bez obrázku (licence DNNT, doklad, který na web nesmí); kontrola výřez nehlásí.
- Rodinné doklady (výpis z matriky, dopis, osvědčení) nemají odkaz na portál: dej jim svazek bez `url`
  (např. `"rodina": {"archiv": "Rodinný archiv", "svazek": "doklady rodiny Novákových"}`) – kontrola pak odkaz nechce.

## `svazky.json`
`{"1a0b2337": {"archiv": "SOA Zámrsk – Sbírka matrik…", "portal": "ARON", "svazek": "N Holice 1880–1900, sign. …",
"popis": "obce", "url": "odkaz na svazek"}}` – u ARON zapisuje `aron_img.py <apu> svazek`.

## `prepisy.json`
`{"<klic>": {"orig": "[Datum] 14. února 1890\n[Dům] 112\n[Otec] …", "cs": "Český překlad celou větou…"}}`
- `orig` věrný přepis po sloupcích, `[Název sloupce]` v hranatých závorkách, nejisté „(?)“, nečitelné „[…]“, zkratky ponechat.
- `cs` srozumitelný překlad pro rodinu; vysvětli staré pojmy (domkář, podruh).
- Souhrn nalezený v předaných poznámkách není originál ani přepis. Bez snímku ponech `orig` nedoplněné a zdrojovou mezeru popiš.

## `zvyrazneni.json`
`{"<klic>": {"boxes": [[x0, y0, x1, y1]], "status": "ok", "note": ""}}` – zlomky šířky/výšky obrázku `vyrezy/<klic>.jpg`.
Zapisuje `ramecek.py`. Rámeček má obepnout celý čtený zápis (ne jen jméno).

## `mista.json`
`{"Holice": {"re": "Holic", "dotaz": "Holice, Česko", "lat": 50.066, "lon": 15.986}}` – `re` je regulární výraz hledaný
ve faktech osob (kmen slova, aby sedělo skloňování: „Holic“ najde Holice i v Holicích). Spravuje `mista.py`.
Pozor na kolize (Hradec Králové × Nový Hradec Králové – použij `(?<!Nový )Hradec`; krátká jména jako `\bBuku?\b`).
Hypotéza: `"hypoteza": true, "rod": 8`. Zkratky obce, které se objevují ve faktech nebo souhrnech zápisů
(„HL čp. 12“), přidej jako `"zkratky": ["HL"]` – použije je stránka Domy. Stránka Domy bere vzory `re` z `mista.json`
přednostně, i k rozhodnutí, co je táž obec (vzor „Řetov“ spojí Řetovou i Velkou Řetovou) – u stejnojmenných
obcí (Lhota × Dolní Lhota) proto vzor zúži, jinak se domy obou obcí slijí. Když OpenStreetMap obec nenajde („Žár“, malé osady), zkus třetí parametr – dotaz: `mista.py pridej "Žár" "Žár" "Žár, Zdíkov, okres Prachatice"`
nebo dotaz s větší obcí či okresem. U **víceznačných názvů** (Podolí, Dub, Lhota) vezme OpenStreetMap kteroukoli ves
(„Podolí, Česko“ = Podolí u Brna) – v posledním sloupci výpisu zkontroluj okres a dej dotaz se sousední obcí
(`mista.py pridej "Podolí" "Podol" "Podolí, Odlochovice"`). Místopis nejlíp zná rodina – když si nejsi jistý, zeptej se.

## `domy/` – domy předků na mapě (volitelné)
`data/domy/domy.geojson` a `data/domy/vyrezy/` jsou výstup skillu **stare-adresy** (`mapa.py`, polohy domů „obec čp.“
podle stabilního katastru). Export z nich udělá stránku `/domy/` a propojí domy s osobami a zápisy podle zmínek
„Obec čp. N“ ve faktech, poznámkách, `SIDE` a souhrnech zápisů. Adresy, které na mapě chybí, zapíše do
`data/domy/chybi.txt` – podklad pro další kolo geokódování. Bez `domy.geojson` se stránka v menu neukáže.

## `dokumenty.json` – rodinné fotky a dokumenty na webu
`[{"img": "foto_svatba_1919", "popis": "Svatba Jana a Josefy, Holice 1919.", "osoby": [8, 9]}]`
Obrázek ulož přes `vyrez.py dokumenty/<sken>.jpg foto_svatba_1919` (vznikne `vyrezy/` i `zdroje/`).
Na stránce osoby se dokument ukáže u každé osoby z `osoby`. Na stránce příběhu podle klíče `pribeh`: `true` = u všech
příběhů, `"slug"` nebo `["slug", …]` = jen u těchto příběhů z `data/pribehy/`, `false` = u žádného. Bez klíče: u příběhu
s rodem (`rod` ve frontmatter, u `pribeh.md` v `web.json` → `pribeh.rod`), když se dokument týká někoho z toho rodu;
jediný příběh bez rodu ukáže všechny dokumenty.
**Nahrávky a PDF:** `{"typ": "audio", "soubor": "media/vypraveni_1.mp3", "prepis": "media/vypraveni_1.txt", "popis": "…",
"osoby": [4]}` (u PDF `"typ": "pdf"`). Soubor leží v `media/` v kořeni projektu, export ho zkopíruje do `web/public/media/`;
`img` není potřeba. Web má pak stránku **Fotky** (`/fotky/`) se všemi dokumenty; její texty jdou změnit ve `web.json`
→ `"fotky": {"uvod": …, "pdf_nadpis": …, "pdf_popis": …}` (např. že PDF jsou životopisy vygenerované umělou inteligencí).
Velké nahrávky do gitu nedávej (`media/*.mp3` do `.gitignore`), když projekt sdílíš.

## `portrety.json` – profilové fotky osob (volitelné)
`{"8": {"img": "portret_jan_novak"}}` – číslo osoby → výřez ve `vyrezy/` (čtvercový, obličej uprostřed; `vyrez.py`).
Fotka se ukáže v záhlaví stránky osoby a jako malé kolečko v rodokmenu.

## `vetve.json` – vedlejší linie z rodinného stromu (volitelné)
Sourozenci předků a jejich potomci (i manželé) z rodinného GEDCOM: `python3 -I tools/vetve_import.py` (jen výpis),
`--zapsat` zapíše `data/vetve.json`. Import u každého předka ověří, že ve stromu jde o tutéž osobu jako v `osoby.py`
(jméno, rok ±2); kde nesedí, nad ní nepokračuje. Formát je v hlavičce nástroje (`rodice`: `"k16"` = předek, `"g123"` = osoba
z větví). Všechny osoby mají stav `fam` – jsou to údaje rodinného stromu, ne matrik. Karta ze `SIDE`, která odpovídá osobě
z větví (stejný rodič-předek, jméno, rok ±1), se k ní na webu připojí jako „z výzkumu“.
Web pak na stránkách rodin ukáže rozbalovací větve (sourozenci přímé linie a jejich potomci, děti z dalších manželství),
na stránce výchozí osoby její děti a stránku **DNA shody** (`/dna/`): hledání podle příjmení nebo obce mezi předky,
větvemi a přiženěnými, s příbuzenským vztahem k výchozí osobě a očekávaným podílem sdílené DNA (% a cM).
`kontrola.py` hlídá odkazy a upozorní, když se předek v `osoby.py` mezitím přejmenoval (větve pak mohou patřit jinam).

## `novinky.md` – co je nového (volitelné)
Krátký přehled po kolech hledání, nejnovější nahoře (`### Kolo 5 – 2. 11. 2026` + odrážky s odkazy na osoby).
Když soubor existuje, web má stránku **Novinky** v menu. Rodina se tak nemusí probírat celým deníkem.

## `web.json` – nastavení webu
Viz `web.md`.

## Markdown poznámky
- `research_log.md` – tabulka `| # | datum | zdroj | rozsah | hledáno | výsledek | citace |`, nové řádky na konec, i negativní.
  Web ji zobrazuje jako „Výzkumný deník“. První sloupec může mít číselné nebo textové ID (např. `BA-1`, `KA-1`,
  `STR-10`); při slučování deníků zachovej původní ID nebo je uprav tak, aby byla v celém výsledném deníku jedinečná.
- `zajimavosti.md` – `## Nadpis` + text, odkazy `[Jméno](/osoba/<slug>/)`.
- `pribeh.md` – původní jediný příběh: frontmatter `title`, `lead` + kapitoly `##`; pokud `data/pribehy/` neobsahuje
  Markdown příběhy, zůstává stránka `/pribehy/` zachována. Více příběhů ukládej jako `data/pribehy/<slug>.md` s frontmatter
  `title`, `lead` a číselným `rod` (8–15, volitelné); web vytvoří rozcestník `/pribehy/` a stránky `/pribehy/<slug>/`.
  Jak psát: `pribehy.md`.
- Poznámky pro Clauda v markdownu piš jako `<!-- … -->` – na web nejdou.
- `archivni_dotazy.md`, `udaje_od_rodiny.md` – volný text.

## Odkazy na osoby (slug)
Slug = jméno bez diakritiky + rok, např. `jan-novak-1890`; při kolizi přidá číslo osoby. Přesné slugy po `npm run data`
v `web/src/data/site.json` (`people`). Při přejmenování osoby se slug změní – oprav odkazy v textech.
Při přečíslování předků promítni změny do `SIDE.k`, klíčů `LINES`, číselných odkazů v `web.json` i odkazů na osoby
v příbězích; potom spusť kontrolu a znovu vytvoř web.
