# Portály archivů a jak z nich dostat snímky

Matriky jsou online u osmi státních archivů (a židovské ještě v Národním archivu) – podle toho, **kde předci žili** (dnešní kraje zhruba odpovídají):

| Archiv | Oblast | Portál s matrikami | Vyzkoušeno se skillem |
|---|---|---|---|
| SOA Zámrsk | východní Čechy (Hradecký a Pardubický kraj) | ARON – aron.vychodoceskearchivy.cz | **ano – hotové nástroje** |
| SOA Praha | střední Čechy | eBadatelna – ebadatelna.soapraha.cz | **ano – nástroj `ebadatelna.py`** (i urbáře a gruntovní knihy) |
| SOA Plzeň | západní Čechy | Porta fontium – portafontium.eu | **ano – nástroj `portafontium.py`** |
| SOA Třeboň | jižní Čechy | digi.ceskearchivy.cz | **ano – nástroj `trebon.py`** |
| SOA Litoměřice | severní Čechy | Digitální badatelna – digi.soalitomerice.cz | **ano – nástroj `litomerice.py`** (limit portálu viz níže) |
| AHMP | hl. m. Praha | katalog.ahmp.cz (Pragapublica) | **ano – `ahmp_search.sh`, `ahmp_scan.py`** |
| MZA Brno | jižní Morava, Vysočina z části | Acta Publica – www.mza.cz/actapublica | **ano – nástroj `mza.py`** (bez prohlížeče) |
| ZA Opava | severní Morava a Slezsko, Olomoucko a Litovelsko | Digitální badatelna – digi.archives.cz/da/ | **částečně – `soal_zoomify.py`** (jen s prohlížečem, CAPTCHU řeší uživatel) |
| Národní archiv | židovské matriky 1784–1949 (HBMa, HBM) | Archivní VadeMeCum – vademecum.nacr.cz | **ano – `vademecum.py`** |
| Národní archiv | pražské policejní přihlášky 1850–1914 | digi.nacr.cz/prihlasky2 | **ano – `policie_prihlasky.py`** |
| Památník Terezín | čeští vězni v táborech (Buchenwald, Dachau, Mauthausen, Flossenbürg…), Malá pevnost, ghetto | pamatnik-terezin.cz/databaze | **ano – `vezni.py`** |
| Arolsen Archives | vězni, oběti a nuceně nasazení, vysídlené osoby (DP) – desítky milionů jmen | collections.arolsen-archives.org | **ano – `arolsen.py`** |
| Archiv města Brna | Encyklopedie dějin města Brna (osobnosti, ulice, hroby) | encyklopedie.brna.cz | **ano – `brno_encyklopedie.py`** |
| Matricula Online | církevní matriky Rakouska (i Vídně), Německa, Polska, Srbska… | data.matricula-online.eu | **navigace ano – `matricula.py`**; obrázky v prohlížeči |
| Mauthausen Memorial | zemřelí v Mauthausenu a pobočkách | raumdernamen.mauthausen-memorial.org | **ano – `mauthausen.py`** |
| Terezínská iniciativa | oběti nacistické perzekuce (Židé z českých zemí) | holocaust.cz/databaze-obeti | **ano – `obeti.py`** |
| VÚA–VHA, VHÚ | legionáři, padlí 1. a 2. sv. války, vojenské matriky, válečné hroby | vuapraha.cz, kramerius.army.cz, valecnehroby.army.cz | částečně – bez nástroje, viz „Vojáci a války“ |

**Hranice archivů neodpovídají dnešním krajům přesně.** Moravské obce v dnešním Pardubickém kraji (Svitavsko) mají
matriky v SOA Zámrsk (ARON), město Turnov a fara Vyskeř také v ARON, ač okolní fary jsou v SOA Litoměřice. Když obec
v „jejím“ archivu není, zkus hned sousední archiv a obce se stejným jménem (Choteč, Brloh – vždy ověř okres).

Adresy u nevyzkoušených portálů ověř při prvním použití (portály se mění). Když nástroj selže, spusť `python3 -I tools/smoke_test.py`
(nebo jen `smoke_test.py <nástroj>`): jedním bezpečným dotazem ověří všechny síťové nástroje a řekne, jestli portál neodpovídá (NEDOSTUPNÉ),
nebo se změnil (CHYBA) – pak je třeba opravit nástroj i tento návod. Pro pohraničí a mimo ČR viz `playbook.md` §2
(Matricula pro Rakousko/Německo, Geneteka pro Polsko, FamilySearch pro Slovensko) a níže.

## ARON (SOA Zámrsk) – hotové nástroje
- **Hledání svazků:** `python3 -I tools/aron_search.py "Holice"` → řádky `apu_id | signatura, roky | druh, obce`.
  Popis obsahuje druh knihy (NAROZENÝCH / ODDANÝCH / ZEMŘELÝCH, index) a všechny obce farnosti.
- **Informace o svazku:** `python3 -I tools/aron_img.py <apu_id> info` → název a počet snímků.
- **Stažení snímku:** `python3 -I tools/aron_img.py <apu_id> <snímek> 1 pracovni/holice_n_57.jpg`
  (úroveň 1 = poloviční rozlišení – stačí na orientaci; 0 = plné rozlišení – na čtení a výřez).
  Jen část stránky v plném rozlišení: `… <snímek> 0 pracovni/detail.jpg 0.0,0.4,1.0,0.7`.
- **Odkaz na snímek** (pole `odkaz` v `zaznamy.json`): `python3 -I tools/aron_img.py <apu_id> link <snímek>`.
  Odkazy z dřívějších verzí (id souboru PUBLISHED) otevřou knihu na prvním snímku – najde je
  `aron_img.py odkazy`, opraví `aron_img.py odkazy --opravit` (v `data/`, pak znovu `npm run data`).
- **Svazek do dat:** `python3 -I tools/aron_img.py <apu_id> svazek` (klíč = prvních 8 znaků apu_id → pole `svazek` v zápisu).
- V ARON jsou i další fondy (sčítání lidu, některé gruntovní knihy, kroniky) – `aron_search.py "Obec" "název fondu"`.
- Stejnojmenných obcí bývá víc (Vinice u Hořic × Vinice u Velké Jesenice). Výsledky jsou seřazené podle farnosti;
  zúžit jde víc slovy oddělenými čárkou, která musí být v popisu všechna: `aron_search.py "Vinice,Hořice"`
  (nebo hledej sousední obec či farní obec).
- U starých far hledej nejdřív **souhrnné indexy** (popis „index NAROZENÝCH…“ přes mnoho let), často sahají do 17. století.
- Obec nenalezena? Zkus název **bez přívlastku** („Lhota“ místo „Horní Lhota“) a starý název. Starší matriky
  (před ~1784) bývají ve faře sousedního města; indexy fary mají oddíly po vesnicích
  („Copulati Gross Lhota“).
- Rejstříky ARON bývají neúplné (pod písmenem jen pár jmen za desítky let) – při negativním výsledku projdi oddíl obce v knize.
- ARON bývá chvílemi velmi pomalý (desítky sekund až minuty na snímek, občas timeout). Stahuj na pozadí a mezitím
  dělej jinou práci; víc souběžných stahování ARON nezrychlí, ale přetíží (vrací 503).
- Ber ohled na server: stahuj jen to, co čteš; žádné hromadné stahování celých svazků.

## SOA Třeboň (digi.ceskearchivy.cz) – `tools/trebon.py`, bez prohlížeče
- `trebon.py misto "Obec"` → id místa. Diakritiku a mezery nástroj odstraní sám (portál zná jen „RatiborskeHory“).
  Portál vrátí vždy jen jedno místo – **zkontroluj vypsaný název a okres**: u stejnojmenných obcí jinou (Buk → Bukovka),
  u měst i okres nebo synagogu (Jindřichův Hradec → okres 1949–1960). Správné id pak najdi na portálu a pracuj s ním.
  Název sídla farnosti sám neurčuje, které obce svazek pokrývá: porovnej popis a seznam obcí u konkrétní knihy,
  případně její úvodní snímky. Malé osady portál jako místo nezná vůbec (Malá Chyška) – hledej farní nebo sousední
  obec (Chyšky) a osadu v popisu knih.
  Občasná chyba 500 bývá výpadek portálu – nástroj zkouší znovu; když trvá, zkus to později.
- `trebon.py svazky <id|"Obec">` → knihy místa (id knihy, druh, roky, obce).
- `trebon.py rejstrik <id_knihy> <písmeno>` → **dobrovolnický jmenný rejstřík** knihy se snímkem, obrovská úspora.
  Ne každá kniha ho má; prázdný výsledek nebo chybějící písmeno **nedokazuje, že osoba v matrice není**.
  Rejstřík je pomůcka k nalezení zápisu, který pak ověř v samotné matrice.
- `trebon.py snimek <id_knihy> <snímek> pracovni/x.jpg [nahled]`, `trebon.py svazek <id_knihy>` (do `svazky.json`).
- Trvalý odkaz: `https://digi.ceskearchivy.cz/<id_knihy>/<snímek>`.
- Některé fary mají knihy po vesnicích, které nejsou v seznamu svazků místa (Vacov → Žár) – hledej podle titulků knih fary.
- **Civilní matriky (1920–1945) lidí bez vyznání** jsou v knihách okresních úřadů (např. Tábor, kniha 12304) a mají
  dobrovolnický rejstřík (`trebon.py rejstrik 12304 N`). Dobrá cesta, když farní matrika mlčí. V `svazky "Obec"`
  se neukážou (patří okresu, ne obci) – id knihy najdi na portálu.
- U oddacích rejstříků zkus při neúspěchu hledat také pod příjmením ženicha; řazení se může lišit. Číslo folia
  z rejstříku nepřeváděj pevným offsetem na snímek: najdi folio v knize a ověř okolní strany podle číslování a roku.
- `misto` zná osady často pod jiným tvarem jména (Ouřice → Uhřice, Bohonice → Bohunice, Nekvasovice → Nakvasovice) –
  zkoušej varianty Ou-/U-/Au-, -onice/-unice a dnešní jméno. Malá osada patří často k jiné faře, než napovídá jméno.
- `rejstrik` vrací u části knih prázdno (např. jižní Šumava) a nevidí novodobé rejstříky ženichů na konci oddacích
  knih – ty najdeš náhledy od konce knihy.
- **Za koncem online části** portál vrací pořád stejný snímek (zadní desku) – shodné obrázky po sobě = konec knihy.
- Kromě matrik jsou na portálu (stejným `snimek <id_knihy>`, id z adresy na portálu) i **kroniky** (stránka místa
  `https://digi.ceskearchivy.cz/<id místa>-<Obec>/kroniky`; položky s `menu=4` online nejsou), **pozemkové knihy**,
  **urbáře** (Vimperk, Netolice od 16. století – most přes začátek matrik) a **vrchnostenská registra** s ročními
  soupisy poddaných (dům po domu s věkem). `svazek` u nich zapíše chybně „Sbírka matrik“ – popis oprav ručně.
  „Knihy instrumentů“ a „knihy záznamní“ velkostatku jsou opisy kupních a svatebních smluv a kvitancí z celého panství
  podle data předložení, bez rejstříku: rok odhadni z matrik (sňatek, převzetí statku), kalibruj náhledy po ~10 snímcích
  a hledej na okraji „Vide Grundbuch <ves> N° I fol. N“ – folio statku je stálé a vede k dalším listinám k domu.

## SOA Plzeň (Porta fontium, portafontium.eu) – `tools/portafontium.py`, bez prohlížeče
- `portafontium.py fara <fara>` → knihy fary: kniha | obce | roky a druhy (`*` N, `oo` O, `+` Z, `i` index) | popis.
  `<fara>` je název římskokatolické fary („Dolní Bělá“, „Mýto“ – diakritiku nástroj odstraní) nebo přímo část
  její adresy (`dolni-bela` =
  `…/contents/register/soap-pn/cirkev-rimskokatolicka/dolni-bela`). Obec → faru nástroj nehledá: faru zjisti ve vyhledávání
  matrik na portálu (pole Místo, v prohlížeči) nebo v popisech knih okolních far. Bez prohlížeče: stránka
  `https://www.portafontium.eu/searching/register?search_api_views_fulltext_1=<obec>` vypíše odkazy
  `/register/soap-pn/<kniha>` – `<kniha>` (např. `kdyne-29`) rovnou použij v `portafontium.py info`.
- `portafontium.py info <kniha>` (`dolni-bela-17`) → signatura, druh, text desky a **obsah** – u knih psaných po vesnicích
  vypíše, na kterých foliích je která obec („Ves X z let 1862–1901 = fol. 121–200“).
- `portafontium.py snimek <kniha> <snímek> pracovni/x.jpg [nahled] [x0,y0,x1,y1]` → celá stránka v plném rozlišení jedním
  požadavkem (IIIF), `nahled` = 1/4. Číslo snímku = pořadí náhledu v prohlížeči; soubory nesou číslo folia
  (`dolni-bela-17_0951` = fol. 95), takže u knih se souvislou foliací je **snímek ≈ folio**.
- `link <kniha> <snímek>` → trvalý odkaz, `svazek <kniha>` → `svazky.json` (klíč `pf_<kniha>`).
- Zaniklé obce (Slavkovský les, Doupovsko, pohraničí): stejné jméno má často víc vsí (Schönlind = Krásná Lípa u Kraslic
  i zaniklá Krásná Lípa u Sokolova). Rozhodne sousední obec z rodinných údajů a fara: např. Schönlind ve Slavkovském lese
  → fara Kostelní Bříza (`kostelni-briza`), Perlsberg/Lazy a Rockendorf/Žitná → fara Smrkovec (`smrkovec`). Svatby hledej
  i ve faře nevěsty (sousední fara), oddací rejstříky jsou v knihách `…ooi`.
- Bez prohlížečového User-Agentu portál vrací 403 (nástroj ho posílá). Jmenné hledání portál nemá – indexy jsou jen uvnitř knih
  (`*i`, `ooi`, `+i` v seznamu knih fary). Hledej i **souhrnné rejstříky sepsané v 19. století** pro starší knihy celé fary
  (např. `ledce-26` z r. 1858: N 1730–1769, O 1760–1804, česky s foliem) – rychlá cesta ke křtům a sňatkům před 1784.

## SOA Praha (eBadatelna, ebadatelna.soapraha.cz) – `tools/ebadatelna.py`, bez prohlížeče
- `ebadatelna.py hledat "Obec"` → celé názvy lokalit („Lhota - obec X - okres Y“); `matriky "Obec"` (nebo celý název)
  → matrikaId | kniha | druh | roky | fara | počet snímků. U stejnojmenných obcí vypíše možnosti.
- `ebadatelna.py info <matrikaId>` → obsah knihy včetně **rozvržení stran po vesnicích** (např. „1–48 Ves A, 49–82 Ves B,
  1–30 Ves C …“ – každá ves může mít vlastní stránkování) – u takových knih neodhaduj snímek podle roku, ale podle stran
  dané vsi (číslo strany je nahoře na snímku). Takové knihy bývají řazené po vsích, ne chronologicky – je-li rejstřík,
  začni jím.
- `ebadatelna.py snimek <matrikaId> <snímek> pracovni/x.jpg [nahled] [x0,y0,x1,y1]`; `link`, `svazek` (klíč `ebad_<id>`).
- Při přechodné chybě nástroj vypíše, že čeká na další pokus; konečné nedostupnosti odpovídá chybové hlášení,
  nikoli prázdný výsledek hledání.
- **Archiválie** (urbáře, gruntovní a pozemkové knihy velkostatků – most přes 17. století): `a-info <archivalieId>`,
  `a-snimek`, `a-link`, `a-svazek` (klíč `ebad_a_<id>`). Archiválii nástroj nehledá – najdi ji na portálu v prohlížeči;
  id je v adrese `…/pages/ArchivaliePage/archivalieId/<id>`.
- Starší snímky bývají z mikrofilmu nebo silně vybledlé – čti se zvýšeným kontrastem:
  `magick x.jpg -colorspace Gray -contrast-stretch 2%x30% x_k.jpg` (výřez pak dělej z kontrastní verze a poznamenej to v přepisu).
- Portál dává vždy celý snímek (nedlaždicuje); náhled a výřez dělá nástroj po stažení přes ImageMagick (`magick`).
  Denní údržba kolem 4:44 (asi 2 minuty).
- Pole „lokality“ u svazku bývá neúplné – `matriky "Obec"` pak knihu nevypíše; zkus faru, sousední obec nebo osadu
  (filiální kostely mají knihy pod jménem fary, např. Libice nad Cidlinou = „Poděbrady 28“). U rejstříků čti v `info`
  rozsah let po písmenech.

## AHMP Praha – `tools/ahmp_search.sh`, `tools/ahmp_scan.py`
- `bash tools/ahmp_search.sh "Smíchov"` → svazky Sbírky matrik: popis | farnost | (XID, id, počet snímků).
- `python3 -I tools/ahmp_scan.py <XID> <snímek> pracovni/x.jpg [1] [x0,y0,x1,y1]` → snímek (1 = poloviční rozlišení).
- Trvalý odkaz `https://katalog.ahmp.cz/pragapublica/permalink?xid=<XID>&scan=<N>`.
- Nový portál digi.ahmp.cz má ochranu proti robotům – nepoužívat. Pražské matriky 1890–1940 většinou **nemají rejstříky**
  a farností je mnoho – bez přesného data a farnosti (z úmrtí/sňatku nebo od rodiny) je hledání velmi drahé.
- **Civilní sňatky Magistrátu** (MAG O1–O118, 1871–1945): lidé bez vyznání (po 1920 časté) se brali na magistrátu. Každá
  kniha má na konci abecední rejstřík ženichů i nevěst. Konkrétní knihu najde `ahmp_search.sh "MAG O37"` (obecné
  hledání „Magistrát“ vrátí jen část).
- **Matriky ústavů**: např. Zemský ústav pro choromyslné v Bohnicích má vlastní úmrtní matriky do 1949
  (`ahmp_search.sh "CHORB"`, bez rejstříku).
- **Hroby v Praze**: vyhledávání Správy pražských hřbitovů (odkaz z hpspraha.cz → Hřbitovy a hroby) má bezpečnostní kód –
  hledá uživatel sám. Plánky hřbitovů s odděleními jsou na hpspraha.cz; pomohou u častých jmen, když si rodina pamatuje polohu hrobu.

## SOA Litoměřice (severní Čechy) – `tools/litomerice.py`, bez prohlížeče
- Digitální badatelna `https://digi.soalitomerice.cz/digitalnibadatelna/` – Sbírka matrik Severočeského kraje (NAD 856, farní i další matriky,
  často německé). Dřívější návod (CAPTCHA/„počítání“) při ověření v říjnu 2026 nevyšel: hledání i obrázky jdou bez prohlížeče.
- `litomerice.py hledat "Obec" [slovo…] [--stran N]` → `id | pořadí | druh • obce • roky • NAD • signatura`. Dotaz hledá jen mezi **matrikami**
  (99 knih na stránku); u velké obce přidej rok nebo farnost. `litomerice.py info <id>` → původce, roky, signatura, územní rozsah, počet snímků.
- `litomerice.py snimek <id> <snímek> pracovni/x.jpg [nahled] [x0,y0,x1,y1]`, `link`, `svazek` (klíč `soal_<id>`). Portál zobrazuje záznam
  podle pořadí ve výsledcích hledání, proto si nástroj u každého id pamatuje dotaz (`pracovni/litomerice_dotazy.json`) nebo zadej `--dotaz "Obec"`.
- **POZOR: po zhruba 100 rychlých požadavcích na stránky portálu archiv zablokuje přístup na 30 minut.** Každé `snimek`/`info`/`link`
  jsou ~4 požadavky (nástroj dělá pauzy). Nestahuj desítky snímků za sebou; obrázkový server images.soalitomerice.cz limit nemá. Pomocníkům to napiš do zadání.
- Starší návod přes prohlížeč (jen když nástroj selže): v síťovém provozu najdi `…/zoomify/cz/archives/CZ-214000010/matriky/<cesta>/ImageProperties.xml`
  a snímek stáhni `soal_zoomify.py <cesta> 0 pracovni/x.jpg`.
- **Když kniha N/O/Z pro daný rok online není**, bývá online rejstřík fary (I-N, I-O, I-Z; řazení písmeno → chronologicky,
  sloupce jméno, otec, datum, obec, svazek, list). Potvrdí datum a otce a dá přesný odkaz pro dotaz do archivu (stav `prob`).
- Katalog uvádí obce u knih občas chybně – ověř rejstříkem nebo úvodními snímky knihy.

### SOA Litoměřice – mimo matriky (sčítání, civilní matriky, pozemkové knihy) – přes prohlížeč
`litomerice.py` hledá jen matriky. Ostatní fondy najdi v Digitální badatelně v prohlížeči a snímky stáhni `soal_zoomify.py`.
- **Sčítání lidu 1869–1921** (filtr Operáty; hledej „<soudní okres>-<Obec>“ nebo „<obec> sčítání“, u 1921 sada
  `…-1921-<soudní okres>-<Obec>-…`): domácnost dům po domu s datem a místem narození, náboženstvím, povoláním, u 1921
  i **datem příchodu do obce** (ukáže stěhování rodiny); souhrnné archy domů mají jméno majitele bytu → rychlé nalezení
  domu. Na dům 2–4 snímky (obal, list osob, dobytek, přiložené křestní listy). Velká města mají domy přečíslované
  a neseřazené – hledej číslo domu v pravém horním rohu na náhledech (montáž výřezů po 4 v řádku je čitelná i ve ¼
  rozlišení). Zápis do dat jako druh `S`.
- **Civilní matriky (Standesamt) 1939–1945** v Sudetech: úmrtní zápis uvádí datum a místo narození, rodiče, manžela
  a oznamovatele (třeba zetě) – často jediný doklad mezi farními knihami a dneškem.
- **Pozemkové knihy a soupisy poddaných** (filtr Poz. knihy, kategorie Urbáře – Soupis poddaných), viz Starší prameny.
  Knihy domkářů bývají zvlášť a abecední rejstřík majitelů mají na konci. Soupisy často nemají obsah po obcích –
  obec najdi vzorkováním snímků.
- Adresa obrázku: na detailu záznamu jsou id snímků v `select.getScanSelect option`, pak
  `fetch('/digitalnibadatelna/showZoomify/<id záznamu>/<id snímku>')` vrátí HTML s cestou `…/ximage/<operaty|matriky|urbare>/zoomify/…/<uuid>.jpg`
  → `python3 -I tools/soal_zoomify.py "<celá adresa>" 0 pracovni/x.jpg`. **Po jednom s pauzou 4–5 s** (portál blokuje
  po ~100 rychlých požadavcích na 30 minut; obrázkový server je pomalý – desítky sekund na snímek). Když `showZoomify`
  vrátí místo cesty HTML stránku (vypršela relace), znovu načti detail záznamu (`entityDetail/<id>?actualDetailTab=attachmentsImg`).
  Trvalý odkaz `…/digitalnibadatelna/permalink/<id záznamu>/<id snímku>` (číslo stránky v adrese výsledků se mění s každým hledáním).

## ZA Opava (severní Morava, Slezsko, Olomoucko, Litovelsko) – `tools/soal_zoomify.py`
- Ověřeno v říjnu 2026: `digi.archives.cz` vrací jen kontrolní stránku Radware („Radware Page“, cookies `__uzm*`) – bez JavaScriptu se
  k hledání nedostaneš. **Ochranu neobcházej**; hotový nástroj pro hledání tu proto není (jen stahování snímků).
- **Co ZA Opava pokrývá** (podle její zprávy o činnosti za 2025; sídlo Opava, pobočka Olomouc): bývalý Severomoravský kraj, tedy státní okresní archivy
  **Bruntál, Frýdek-Místek, Jeseník, Karviná, Nový Jičín, Olomouc, Opava, Prostějov, Přerov a Šumperk**. Obce na Litovelsku a Olomoucku patří pod **ZA Opava**, ne pod MZA Brno.
  Např. Vrbno pod Pradědem (okres Bruntál, německy Würbenthal) je tedy v Opavě.
- **Valašsko** (Vsetín, Valašské Meziříčí, Rožnov, Krhová) leží v olomoucké arcidiecézi; farní matriky olomoucké arcidiecéze drží **ZA Opava** a FamilySearch uvádí
  jako původ snímků matrik Valašského Meziříčí právě Opavu. Okresní archiv Vsetín (úřední spisy) je ale pod Moravským zemským archivem (není v seznamu okresních archivů
  ZA Opava) a v Acta Publica (`mza.py`) Valašsko při zkoušce v říjnu 2026 není (část Zlínska tam je, např. Zlín-Malenovice). **Matriky Valašska tedy hledej nejdřív v Opavě**
  (digi.archives.cz) a spisy ve SOkA Vsetín; hranici si ověř u konkrétní farnosti v seznamu původců obou archivů.
- Katalogová obec sama o sobě nedokládá, že je online příslušná matrika ani že pokrývá hledanou dobu. Ověř konkrétní
  svazek a jeho popis v portálu.
- **Bez prohlížeče to nejde.** Badatelna `https://digi.archives.cz/da/` (stará adresa matriky.archives.cz jen přesměruje)
  má ochranu proti robotům – curl ani WebFetch se nedostanou ani na hledání. Potřebuješ připojený prohlížeč (Claude in
  Chrome – uživatel ho v Claude Code připojí příkazem `/chrome`; v Cursoru prohlížeč agenta; v OMP `browser` přes eval
  s `headed: true`, jinak je okno skryté – nebo Playwright); jinak ať knihu najde a snímky uloží uživatel.
  Úvodní ověření projde samo, ale hledání často skončí **CAPTCHou: tu vyřeší uživatel** v okně prohlížeče, ty nikdy.
  Vestavěný prohlížeč Claude desktop dostane stránku Radware „Anomaly detected“; uživatelův Chrome (Claude in Chrome)
  prošel (10/2026 i bez CAPTCHY). Vyplnění pole přes `form_input` hledání nespustí – klikni do pole a stiskni Enter
  (nebo `searchForm.requestSubmit()`).
- Filtr typů záznamů si badatelna pamatuje v relaci a filtry se sčítají (klik nefunguje jako přepínač) – u každého
  výsledku kontroluj ikonu typu (Matriky). **Než začneš listovat, otevři detail svazku**: v Technické poznámce stojí
  „Matrika je dosud uložena na matričním úřadě“, když není digitalizovaná – to rovnou patří do `archivni_dotazy.md`.
- Hledej obec a vyfiltruj Matriky (ikona, potom znovu lupa). Hledání vrací i civilní matriky (u obce stovky svazků) –
  filtr „Datum od – do“ (podle začátku svazku, např. 1680–1873) nechá jen církevní. Knihy bývají řazené po obcích
  a na konci mají rejstřík. Vedle farních knih bývají i **druhopisy** („T“ v signatuře, viz `matriky.md`).
- **Seznam svazků a ID snímků si hned ulož** do `pracovni/<svazek>/` – relace po pár hodinách vyprší a výsledky
  hledání platí jen v ní. Na detailu svazku: entita `document.querySelector('[entityuuid]').getAttribute('entityuuid')`
  (u svazků uložených v jiném archivu nemá tvar UUID – nehledej ji regexem), ID snímků jsou hodnoty
  `select.getScanSelect option` (tvar „N%20uuid“). Snímek pak otevřeš kdykoli bez hledání:
  `/da/showZoomifySeparate?imageNumberSeparate=N&myEntityUuid=<entita>&myImageUuid=<uuid>`.
- Adresa obrázku: `fetch('/da/showZoomify/<id svazku z URL>/<část option.value za „%20“>')` vrátí HTML s cestou
  `…/images/<složka>/<uuid>.jpg`. Cesta se u svazků liší (`…/CZ-217000010/NAD-165/dao/images/…`, `…/zao/matriky/dao/images/…`)
  a přípona bývá i `.JPG` – nástroji dej vždy **celou adresu z HTML**:
  `python3 -I tools/soal_zoomify.py "<adresa>" 2 pracovni/x.jpg` (2 = čtvrtinové rozlišení na orientaci podle záhlaví
  stránek, 0 = plné jen u nalezeného zápisu). Obrázkový server images.archives.cz neomezuje a cookies nepotřebuje.
- **POZOR na blokování** (jen stránky aplikace, obrázky ne): rychlé dotazy → CAPTCHA, „operace vyhodnoceny jako
  nestandardní“ nebo „Access blocked“ na 30 minut; po desítkách dotazů za den vrací showZoomify „Server Exception“
  (denní limit – pokračuj až další den). Pauza 3–6 s mezi stránkami, dávky do ~80 stránek, žádné rychlé `fetch` hned
  po hledání a stránky výsledků neprocházej za sebou. Delší smyčku pusť v prohlížeči na pozadí, výsledky ukládej do
  `window` nebo `localStorage` a vyzvedávej po částech (nástroj pro JavaScript má limit asi 45 s). Pomocníkům to napiš do zadání.

## MZA Brno (jižní Morava, Acta Publica) – `tools/mza.py`, bez prohlížeče
- Portál `https://www.mza.cz/actapublica/` je veřejný, bez přihlášení (v říjnu 2026 bez ochrany proti robotům). Adresa actapublica.eu
  bývá za Cloudflare zablokovaná („Sorry, you have been blocked“ – podle IP, i v běžném prohlížeči); nástroj ji nepoužívá.
  Když nejde ani mza.cz, ať uživatel vypne VPN nebo zkusí jinou síť.
- `mza.py hledat "Obec" [slovo…]` → knihy: `id | č. knihy | původce (typ) | N | O | Z | obcí | snímků`. Hledá v českém, německém
  i historickém jménu obce („Auspitz“ = Hustopeče). Další slovo výsledek zúží: čtyřmístné číslo = rok uvnitř rozsahu N/O/Z
  (`hledat Hustopeče 1850`), jiné slovo = text v řádku (farnost, sousední obec). U častých jmen („Lhota“ přes 600 knih) vždy
  přidej farnost nebo rok. `mza.py puvodce "Farnost" [typ]` hledá podle farnosti (typ = „římsko“, „evangel“, „civilní“…).
- **První sloupec (`id`) je interní číslo knihy** z adresy `…/matrika/detail/<id>` – to se zadává dalším příkazům, ne „č. knihy“.
- Obec mívá narození do určitého roku v samostatném svazku mimo knihy fary – hledej `mza.py hledat "<obec>"`, ne jen podle
  farnosti. Rejstříky 20. století jsou samostatné knihy („O - 1907 - 1949“) a rejstřík oddaných řadí ženichy a nevěsty zvlášť.
- `mza.py info <id>` → rozsahy, **všechny obce farnosti s okresy** (stejnojmenné obce rozliší okres), jazyk, poznámky.
  Starší knihy jsou latinsky (záhlaví sloupců) a **jména a kmotři často německy** (Hustopeče 1621) – jména čti v německém i českém tvaru.
- `mza.py snimek <id> <snímek> pracovni/x.jpg [nahled] [x0,y0,x1,y1]` – snímek v plném rozlišení; číslo snímku je pořadí
  v knize od 1. Výřez v relativních souřadnicích stáhne jen potřebné dlaždice. `link <id> <snímek>` dá trvalý odkaz
  (`…/matrika/detail/<id>?image=<soubor>`), `svazek <id>` zapíše knihu do `svazky.json` (klíč `mza_<id>`).
- Snímky jsou IIPImage/DeepZoom na `www.mza.cz/iipsrv/`. **Server přijímá jen HTTP/2** – Python ho neumí (HTTP 426), proto
  nástroj stahuje dlaždice přes příkaz `curl` (macOS i Windows 10+ ho mají).
- Rejstříky a „části matriky“ (záložka v prohlížeči) nástroj zatím nevypisuje; jsou-li u knihy, najdeš je na portálu
  a číslo snímku použiješ v `snimek`. Knihy bývají po farnostech a letech, indexy jsou v poli rejstříku u N/O/Z.
- `snimek` potřebuje ImageMagick (`magick`) a `curl`; hledání, `info`, `link` a `svazek` ne. Pomocníkům to napiš do zadání.
- **Ber ohled na server** (podmínky užití na portálu): MZA blokuje IP adresu (i celou síť na hodiny) už po desítkách rychlých
  dotazů nebo stovkách snímků za večer. Stahuj jen konkrétní snímky, které čteš, žádné předběžné stahování celých knih;
  na náhled stránky stačí `nahled`, na zápis výřez. Nástroj jde přes brzdu (`tools/slusne.py`) a celé snímky ukládá do sdílené
  cache, stejný snímek se podruhé nestahuje. Na MZA nejvýš jeden pomocník najednou.
- Když nástroj selže (403, změna portálu), čti přímo v prohlížeči: prohlížeč na celou obrazovku (tlačítko vpravo), lupa + dvakrát, pak
  kolečko myši nad místem zápisu (zvětšuje kolem kurzoru); velké tažení viewer resetuje, malé posuny fungují. Pole „Snímek“
  skáče přímo. **Rejstříky** (oddaní ~1890–1949) bývají na konci knihy a uvádějí stránku – stránka ≠ snímek, dohledej
  podle hlaviček. Sňatek bývá ve farnosti nevěsty. Výřez do dat = snímek obrazovky (odkaz na snímek knihy do `odkaz`).

## Po válce přistěhovaní, reemigranti, přesídlení (osídlování pohraničí 1945–1950)
Ověřené (2026-10): v Národním archivu je fond **Ministerstvo práce a sociální péče, Praha** (NAD 1028), inv. č. 655, sign. 3521: „Reemigrace – čs. reemigrační mise ve Vídni,
reemigrační střediska v Žatci, Berouně, Chebu, reemigrace z jednotlivých zemí (Argentina, Bulharsko, Čína, Francie, Německo, Polsko, **Rumunsko**…), 1946–1949“ – nezdigitalizováno
(0 snímků), jde o badatelnu (dotaz do `archivni_dotazy.md`). Další fondy hledej `vademecum.py hledat "reemigrace"` a podle obce. Zbytek postupu níže je z literatury (nevyzkoušeno):
Matriky tady nestačí: lidé, kteří přišli po 1945 do pohraničí (Volyňští Češi, reemigranti z Rumunska, Jugoslávie,
Polska, Slováci a Češi z vnitrozemí), mají v matrikách jen narození a sňatky *před* příchodem v jiné farnosti, často v zahraničí.
Skill pro ně zatím nemá hotový nástroj ani vyzkoušený portál. Postup, který je podle literatury rozumný, ale na skutečném případu
ho nikdo neověřil – vždy ho zapiš do `STAV.md` a výsledek do `poznamky_pro_skill.md`:
1. **Zeptej se rodiny**: odkud a kdy přišli, na jaké hospodářství/dům (číslo popisné!), jaké měli doklady (osídlenecký
   dekret, přídělová listina, domovský list, repatriační průkaz).
2. **Rodiště před příchodem** (matriky v cizině): Volyň – skeny jsou na Ukrajině a v Polsku, ne online; Rumunsko/Jugoslávie –
   FamilySearch a farní matriky v místě; Polsko – Geneteka, Matricula (viz níže). Mladší než 100/75/30 let jen na matričním úřadě.
3. **Úřední spisy o osídlení**: národní výbory (MNV, ONV), osídlenecké komise a Národní pozemkový fond; písemnosti IX. odboru
   ministerstva zemědělství jsou podle literatury v archivu Ministerstva zemědělství ČR a nejsou uspořádané, přehled pramenů
   k Volyňským Čechům v Národním archivu je v článku L. Kločkové (Sborník NM, 2015). Spisy konkrétního domu/hospodářství hledej
   ve **státním okresním archivu** (SOkA) podle obce, fond „Místní národní výbor <obec>“ a „Okresní národní výbor“. Online to
   většinou není – zapiš do `archivni_dotazy.md` (archiv, fond, obec, číslo domu, jméno) a pošli dotaz archivu.
4. **Evidence obyvatel do 1953** (Praha): podle webů zastupitelských úřadů se o ni žádá přes Národní archiv (zvláštní formulář),
   zatímco AHMP má pražské matriky. Pro 1850–1914 viz policejní přihlášky výše; ověř si aktuální postup u archivu.
5. **Německé obyvatelstvo, které odešlo** (odsun) – jeho matriky jsou v archivech pohraničí normálně (Litoměřice, Plzeň,
   Opava); osud po odsunu v Německu: Arolsen, Lastenausgleichsarchiv (Bayreuth) – nevyzkoušeno.
6. **Narození, sňatky a úmrtí českých občanů v cizině** zapisuje **Zvláštní matrika** (Úřad městské části Brno-střed, odbor matrika, Dominikánská 264/2, Brno; podle
   webu MV zápis podáš osobně, přes zastupitelský úřad nebo přes kterýkoli matriční úřad v ČR, se zahraničním dokladem; zápis je bez poplatku, stejnopis 300 Kč – údaje ověř,
   mění se). Pro starší události zjisti u úřadu, jestli a čím lze zápis doložit. Hodí se u předků narozených v zahraničí, kteří měli československé občanství.
7. **Evidence obyvatel a sčítání** (do 1946) jsou u okresních archivů; FamilySearch je katalogizuje jako „Czech Republic, <okres>, <obec>, census, 1869-1946“.
   Mohou ukázat předchozí (německé) obyvatele domu, kam se rodina přistěhovala. Rodina, která dorazila až 1947, v nich ještě být nemusí.
Žádný z těchto kroků nenahrazuje hledání v matrikách; je to jen cesta, jak zjistit, **odkud rodina přišla**, aby se mělo
kde matriky hledat.

## Židovské matriky 1784–1949 (Národní archiv) – `tools/vademecum.py`, bez prohlížeče
- **Pozor:** dřívější adresa `badatelna.eu` už s Národním archivem nesouvisí (v říjnu 2026 je to cizí web). Židovské matriky jsou
  v **Archivním VadeMeCum** `https://vademecum.nacr.cz` (NA se přestěhoval na na.gov.cz). Dva fondy: **HBMa** „Matriky židovských
  náboženských obcí v českých krajích“ (NAD 167, 1784–1949) a **HBM** „Židovské kontrolní matriky“ (NAD 144, opisy vedené u farních
  úřadů, 1780–1911 – dobré, když originál chybí). Knihy jsou po židovských obcích (např. „FÚ Dambořice“) a letech, ne po jménech.
- `vademecum.py hledat "Obec" [--jen-snimky] [--stran N]` → `xid | druh | inv. č. | NAD | roky | popis | počet snímků`. Hledá fulltextem, takže
  najde i obec, která je uvedena jen v rejstříkových heslech spádových obcí. **Název židovské obce a seznam obcí v knize** vypíše
  `vademecum.py info <xid>` – tam ověř, že je to správná kniha. Roky v popisu bývají „(i)“ = s rejstříkem.
- `vademecum.py snimek <xid> <snímek> pracovni/x.jpg [nahled] [x0,y0,x1,y1]`, `link <xid> <snímek>` (trvalý odkaz na sken),
  `svazek <xid>` (do `svazky.json`, klíč `nacvm_<prvních 8 znaků xid>`). Snímek vyžaduje ImageMagick; staví na `soal_zoomify.py`.
- Matriky jsou psané **německy** (kurent/latinka) a tištěné rubriky jsou německé (Der Verstorbenen, Der Geborenen…); jména se píší
  německy (Jakob, Moses), přijmení jednotlivých osob se v 19. století pravopisně liší.
- Lhůty jako u církevních matrik (narození 100, sňatky 75, úmrtí 30 let); mladší židovské matriky jsou na matričním úřadě.
- Oběti, jejichž rodiny jsou v těchto matrikách, najdeš i v `obeti.py` (viz níže). Stejné VadeMeCum má i další archivy,
  nástroj je zatím nastavený jen na Národní archiv.

## Databáze obětí nacistické perzekuce – `tools/obeti.py`
- `obeti.py hledat --prijmeni Neumannová [--jmeno Anna] [--bydliste Ostrava] [--misto-narozeni …] [--rok 1906]` → jméno, datum narození,
  transporty (Terezín → Osvětim…), osud, odkaz. `obeti.py detail <odkaz>` vypíše poslední bydliště, adresu v protektorátu a transporty.
  Příjmení hledej **v ženském tvaru** („Neumannová“, ne „Neumann“) a nejdřív jen příjmení.
- Je to vodítko k osudu osob a k tomu, **odkud rodina pocházela** (poslední bydliště před deportací). Citlivé údaje – na web jen se
  souhlasem rodiny (`soukromi.md`). Romové mají samostatnou databázi (odkaz na holocaust.cz).

## Vojáci a války (1. a 2. světová válka, legie) – bez hotového nástroje
**Kdy hledat:** u každého muže narozeného zhruba 1865–1900 (prošel 1. světovou válkou) a hned, když je úmrtí 1914–1918
mimo domov, „nezvěstný“, nebo rodina vypráví o frontě, zajetí či legiích. Vysvětlí to „zmizelé“ úmrtí mimo farnost
a dá příběh na web. V datech je to zdroj `J` (jiný pramen); do faktů osoby piš pluk, hodnost a osud slovy
(„voják c. a k. pěšího pluku 28, padl 1915 v Haliči“), legionáře označ `vyz` (stránka Osobnosti). Jména padlých
a obětí jsou citlivá – na web se souhlasem rodiny (`soukromi.md`). Síť jen přes `slusne.py`.
1. **Seznamy ztrát c. a k. armády** (Verlustlisten 1914–1919; jméno, hodnost, pluk, domovská obec, rok narození, stav –
   padl, raněn, zajat) jsou v ANNO. Hledej podle **domovské obce v německém tvaru** – účinnější než příjmení:
   `ANNO_TITLE=vll python3 -I tools/anno.py '"Pietschnau"' 1914 1919 3 --snip` (seznamy ztrát mají v ANNO zkratky
   `vll`, `vlv`, `nvv`). Jsou i v Kramerius NK a v Digitální studovně MO; odkazy shrnuje VHÚ („Seznamy ztrát
   rakousko-uherské armády“, vhu.cz/knihovna).
2. **Databáze VÚA–VHA** (vuapraha.cz → databáze): legionáři, padlí v 1. a 2. světové válce, Čechoslováci v zahraničních
   armádách, bílá kartotéka padlých 1. sv. války (lístky jako obrázky; uvádějí „tom., fol.“ vojenské úmrtní matriky),
   RAF a další. Bez prohlížeče (vlastní skript přes `slusne.py`): `POST https://www.vuapraha.cz/wp-json/mo/v1/archive-database/html`,
   JSON `{"page":1,"name":"","surname":"Novák","place":"","date":"","database":"legio"}` (dále `fallen-first`,
   `fallen-second`, `abroad-second`); detail `…/legionari/<id>`, `…/padli-1-svetova/<id>`. Hledání příjmení je
   podřetězcové – ověř jméno, rok a místo narození.
3. **Vojenské úmrtní matriky 1. sv. války** (podle VHÚ přes 160 000 padlých) jsou v Digitální studovně MO, mj. pod
   „Matriky pěšího pluku N“ (N = číslo čs. pluku, který c. a k. pluk převzal – zjisti ho dřív). Studovna má rozhraní
   Kramerius 5 bez přihlášení: zkus `kramerius.py '<dotaz>' 10 --server https://kramerius.army.cz` (nástrojem nevyzkoušeno;
   u digitalnistudovna.mo.gov.cz byl v 10/2026 nedůvěryhodný certifikát – **kontrolu certifikátu nevypínej**, použij prohlížeč).
4. **Kmenové listy** (VÚA–VHA, jen na písemnou žádost): dochované hlavně ročníky 1865–1886, ročníky 1887–1900 z velké
   části skartované (viz `playbook.md` §0.3); Slováci ročníků 1911–1920 ve VHA Bratislava. → `archivni_dotazy.md`.
5. **Kriegsarchiv Vídeň** (offline): Grundbuchblätter starších ročníků, vojenské matriky (vedené po plucích, 100letá
   lhůta), kartotéky ztrát a zajatců. Do `archivni_dotazy.md` napiš jméno, datum a místo narození, **domovskou obec**
   (Heimatrecht ≠ rodiště) a pluk – bez pluku se vojenská matrika hledat nedá (`playbook.md` §1 body 5–6, §9).
6. **Pomníky a hroby** (nevyzkoušeno): pomník padlých v obci bývá jediný záznam o nezvěstném – evidencevpm.cz, vets.cz
   (pietní místa, pamětní desky i s fotografiemi), Centrální evidence válečných hrobů valecnehroby.army.cz; příběhy
   legionářů legie100.com.
7. **2. světová válka**: databáze VÚA výše, Osobní věstník MNO 1945 (seznamy popravených vyznamenaných in memoriam;
   Kramerius), vězni a oběti viz „Vězni koncentračních táborů…“ níže.
Náměty na příběh (legionář v rodu, bratři na různých frontách): `pribehy.md`.

## Encyklopedie dějin města Brna (Archiv města Brna) – `tools/brno_encyklopedie.py`
- `brno_encyklopedie.py hledat "Novák klempíř Králova"` → až ~30 zásahů fulltextu (osobnost, ulice, objekt, spolek…) s úryvkem a odkazem; portál vrací jen první stránku,
  zužuj dalšími slovy (příjmení, ulice, povolání). `detail osobnosti:15` (nebo odkaz z výpisu) vypíše celé heslo: narození, úmrtí, **bydliště s adresou**, vzdělání,
  zaměstnání, **hrob (hřbitov, skupina, číslo hrobu)**, poznámky.
- Je to tištěná encyklopedie významných osob a míst, ne evidence obyvatel – běžní předkové tu být nemusí. U brněnských řemeslníků a úředníků ale často dá adresy,
  povolání a hrob na Ústředním hřbitově (a z toho pokračuj v matrikách MZA, `mza.py`). Zdroj cituj jako „Encyklopedie dějin města Brna“.

## Další pomůcky a zdroje (ověřeno 2026-10)
- **Historický lexikon obcí ČR 1869–2015** (ČSÚ, `csu.gov.cz` – web se přestěhoval z czso.cz; hledej „Historický lexikon obcí“): změny názvů, příslušnost obcí k okresům, počty
  obyvatel a domů při sčítáních. Pomůže, když obec zanikla, změnila jméno nebo okres.
- **GOV – Genealogisches Ortsverzeichnis** (gov.genealogy.net): historická německá a česká jména obcí a farní příslušnost (Würbenthal = Vrbno pod Pradědem). Portál je chráněný
  kontrolou prohlížeče (Anubis) – otevři ho **v prohlížeči uživatele**, nástrojem nejde.
- **Online-OFB** (online-ofb.de): přepsané německé farní knihy včetně sudetských obcí (rodiny po rodinách). Pro německé předchozí obyvatele pohraničí; hledej obec v seznamu.
- **JewishGen** (jewishgen.org/databases): databáze židovských rodin z Čech, Moravy, Rakouska, Maďarska; část vyžaduje bezplatnou registraci.
- **Kroniky obcí a školní kroniky**: bývají digitalizované ve fondech archivů (v ARON `aron_search.py "Obec" "kronika"`, v Porta fontium a eBadatelně podle fondu). Obecní kronika
  často popisuje osídlení po 1945 (odkud kdo přišel) a rodiny po jménech.
- **Digitální badatelna Národního archivu** (na.gov.cz → Badatelna → Digitální badatelna) zahrnuje též Knihy židovských familiantů, Desky zemské, Monasterium (listiny),
  Translokační plány židovských obydlí, Sbírku staničních kronik (železničáři) a Politické procesy 50. let; ve VadeMeCum je prohledá `vademecum.py hledat`.

## Pražské policejní přihlášky 1850–1914 (Národní archiv) – `tools/policie_prihlasky.py`
- Karty pražských rodin: hlava rodiny, manželka s rokem a místem narození, děti s roky, adresy, někdy místo sňatku.
  Výborné, když rodina žila v Praze a nevíš farnost (pražské matriky nemají rejstříky).
- `python3 -I tools/policie_prihlasky.py Kolar [Jan] [1850] [1870]` – příjmení bez diakritiky (začátek jména), jméno a roky
  narození volitelně. Bez prohlížeče vrátí jen prvních 20 výsledků, proto hledej co nejúžeji.
  Kartu stáhni `policie_prihlasky.py karta <pořadí> pracovni/karta.jpg Kolar [Jan] [1850] [1870]` (stejné hledání; jde i pořadí
  nad 20) – vypíše citaci a trvalý odkaz (`index.php?action=link&ref=czarch:CZ-100000010:874&karton=K&folium=F`).
- **Nepokrývá Smíchov, Vinohrady, Žižkov, Karlín a další předměstí před 1922** (byla to samostatná města) – tak to bylo zjištěno při
  hledání; Národní archiv na své stránce uvádí, že policejní rajon od 1853 zahrnoval i Karlín, Libeň, Smíchov a další, a jiný projekt
  našel po ~1900 i rodiny ze Žižkova a Vinohrad – u předměstí nehledej jistotu v žádném směru a zkus obě cesty. Náboženství karty neuvádějí.
- Ve výsledcích jsou i manželky a děti (často na téže kartě jako hlava rodiny). Příjmení zadávej bez diakritiky („Simek“).
  Má-li hledání přes 20 výsledků, rozděl ho podle let narození tak, aby každé mělo nejvýš 20.

## Matricula (Rakousko, Německo, Polsko, Itálie, Srbsko, Slovinsko; data.matricula-online.eu) – `tools/matricula.py`, `tools/matricula_*.sh`
- **`matricula.py` (bez prohlížeče, ověřeno)** najde farnost, knihu a číslo snímku: `oblasti [cesta]` (země a diecéze), `fary oesterreich/wien [slovo]`,
  `knihy oesterreich/wien/01-am-hof` (druh, roky, úložiště), `snimky oesterreich/wien/01-am-hof/01-01` (popisky snímků včetně rejstříků „Index“).
  Matricula nehledá podle obce ani jména – znáš-li farnost (z úmrtí, sňatku, od rodiny), ušetří to hodně času. **Obrázky ale chrání token počítaný
  JavaScriptem prohlížeče; nástroj ho nenapodobuje.** Snímek stáhne `node tools/matricula_snimek.js <cesta-knihy> <snímek> pracovni/x.jpg`: otevře knihu v pravém prohlížeči
  (Playwright: jednou `npm install playwright && npx playwright install chromium`), počká, až si stránka sama načte obrázek, a uloží ho (ověřeno na vídeňské knize, ~1,3 MB na snímek).
  Hlídá, aby číslo snímku nepřesáhlo počet snímků knihy (prohlížeč jinak tiše dá poslední snímek). Stahuj jen to, co čteš. Bez Playwrightu: Claude in Chrome nebo ruční uložení.
- **Vídeň:** 567 farností pod `oesterreich/wien/<obvod>-<farnost>` (např. `01-am-hof`). Podle přednášky FamilySearch (2023) jsou oddací a úmrtní knihy
  online do 1938 a křty do 1922, mladší se postupně otevírají – ověř na portálu. Židovské matriky Vídně: Israelitische Kultusgemeinde a mikrofilmy ve
  Wiener Stadt- und Landesarchiv (WStLA). Bydliště před 1976: dotaz WStLA (online formulář). Hřbitovní databáze **friedhoefewien.at → Verstorbenensuche**
  (nástroj nevznikl: widget volá bránu api.wstw.at přes zabezpečenou proxy portálu a samotná brána vyžaduje přihlášení, takže bez obcházení autentizace to nejde; hledej v prohlížeči). Vídeňští Češi: rodina se často „ztratí“ ve Vídni – hledej křest dětí a sňatek ve farnosti bydliště.
- **GenTeam.at** (zdarma po registraci – účet zakládá uživatel sám): dobrovolnický jmenný rejstřík vídeňských katolických
  křtů, sňatků a úmrtí a dalších rakouských pramenů. Během minut najde i další dítě téže matky; zápis pak ověř na Matricule.
  Pasti: aktivační odkaz v e-mailu otevřený přes Outlook (Safe Links) se „spotřebuje“ („Verification code not found“) –
  ať ho uživatel zkopíruje do prohlížeče; „Foundling Baptisms“ jsou jen nalezenci židovského původu, ne všichni nalezenci.
- **Srbsko (Matricula):** část Banátu a Vojvodiny (např. `serbien/subotica`) – ověř, jestli je tam hledaná fara. **Polsko** (Slezsko, Opolsko) viz Geneteka níže.
- Bez přihlášení. Seznam knih: `…/de/oesterreich/<diecéze>/<farnost>/?page=N`; snímek knihy `…/<id>/?pg=<snímek>`
  (zároveň trvalý odkaz).
- URL obrázku obsahuje `csrf` a `ctrl` počítané JavaScriptem → je potřeba prohlížeč (Playwright / Claude in Chrome / v Cursoru prohlížeč agenta / `browser` v OMP):
  otevři knihu, klikni na stránku (`.docview-pagelink`), URL obrázku vezmi z `performance.getEntriesByType('resource')`
  a stáhni `bash tools/matricula_dl.sh "<url>" pracovni/x.jpg`. Víc stránek: soubor řádků „<snímek> <url>“ → `matricula_batch.sh`.
- Rejstřík najdeš bez prohlížeče: HTML stránky knihy má seznam `labels` s popisky snímků („04-Index Taufe_0001“).
- Vojenské matriky (např. Štýrský Hradec) tam nejsou – jsou v Kriegsarchivu ve Vídni (offline).

## Slovensko, Maďarsko, Rumunsko (Banát, Sedmihradsko) – nevyzkoušeno, jen návod
Stav ověřený v říjnu 2026 ze zkušebního prostředí skillu: slovenské (archives.gov.sk), maďarské (adatbazisokonline.hu, Hungaricana, Arcanum) a rumunské
(arhivelenationale.ro) archivní servery byly **nedostupné nebo za Cloudflare (HTTP 403)**, proto nástroje nevznikly. Postup pro uživatele (přes jeho prohlížeč):
- **FamilySearch** (přihlášení zdarma; viz oddíl níže) je pro tyto země hlavní cesta: katalog podle místa → „Church Books / Anyakönyvek / Cirkevná matrika“.
  Kolekce 1554443 (Slovakia Church and Synagogue Books) má kromě křtů zindexované i sňatky a úmrtí (hledej s `q.spouseSurname`
  nebo datem úmrtí); sňatek najde index i ve farnosti nevěsty, kterou bys jinak neprocházel. Slovenské vesnice často nemají
  vlastní faru – katalog podle obce ukáže jen fary se sídlem v obci; faru poznáš ze sloupce bydliště v knihách okolních far.
  Maďarské matriky (1850–1895): Lakhely = bydliště, zsellér = domkář bez půdy, földész = rolník, telkes = sedlák, árva = sirotek,
  néhai = zesnulý, törv. = manželské, H. H. = reformovaný; Mihály = Michal, Pál = Pavel, Erzsébet = Alžběta, Borbála = Barbora, András = Ondřej.
  Slovensko: církevní matriky zhruba 1590–1895 (snímky online), jména často maďarsky/latinsky; **Maďarsko**: církevní matriky (rodné, oddací, úmrtní)
  do 1895, občanské matriky od 1895; **Rumunský Banát a Sedmihradsko**: farní matriky Banátu byly mikrofilmovány 1939–40 (rozsah zhruba 1760–1850), latinsky a německy.
- **Hranice a jména:** do 1918 byly Slovensko, Banát i Sedmihradsko v Uhrách – obce mají **maďarské názvy** (a německé, rumunské); hledej v matrikách pod tím, co platilo v době zápisu.
  Jména: Ferenc = František, József = Josef, János = Jan; příjmení Magyar je „Maďar“ (Madar).
- **Státní archivy** (Slovenský národný archív a štátne archívy; Magyar Nemzeti Levéltár; Arhivele Naționale – např. pobočka Timiș má občanské matriky
  1717–1951): většina knih není online, žádost o výpis podle obce a roku. Mladší matriky (do 100/75/30 let) jen na matričním úřadě.
- **Čeští reemigranti z Rumunska (Banát):** české obce v Banátu (Svatá Helena, Gerník, Eibentál, Bígr, Rovensko aj.) a jejich obyvatelé se po 1945 vraceli do
  Československa (zejména 1946–1950) a usazovali v pohraničí. K původu rodiny zapiš: obec v Banátu, vyznání, jméno rodiny v Banátu (často německy/česky pomaďarštěné). Cesta:
  rozhovor s rodinou → FamilySearch (farní matriky obce) → spisy o osídlení/reemigraci (viz „Po válce přistěhovaní“ výše).
- **Maďarsky/slovensky psané zápisy**: čti pomalu, tabulky mají rubriky (rodiče, kmotři, vyznání); Claude umí maďarštinu a slovenštinu, latinu a němčinu, ale u písma buď opatrný (označ nejistá místa „(?)“).

## Polsko – Szukaj w Archiwach a Geneteka
- **Szukaj w Archiwach** (szukajwarchiwach.gov.pl, polské státní archivy se skeny matrik): portál je chráněný systémem Imperva Incapsula (JavaScriptová kontrola
  prohlížeče), prostým HTTP nic nevrátí. Nástroj proto nevznikl; ochranu neobcházíme. Hledej v prohlížeči uživatele (jmenný index u části souborů, „Wyszukiwanie zaawansowane“).

## Polsko – Geneteka (geneteka.genealodzy.pl)
- Zdarma dobrovolnické indexy křtů, sňatků a úmrtí po farnostech; hledej ve webovém rozhraní (vojvodství → farnost →
  příjmení). Index je vodítko – skeny často online nejsou (farní nebo diecézní archiv), pak zápis žádej tam.
- **Farní příslušnost se měnila**: obec mohla patřit k sousední faře (Lipowa → Radziechowy do 1896) – hledej i tam.
- Nestahuj hromadně: PTG uvádí „linkujemy, nie pobieramy danych“ (odkazujeme, nestahujeme) a po desítkách rychlých dotazů
  server vrací nefiltrovaná data. Dotazy dávkuj, s pauzami, a výsledky si ověř.
- Jednotlivý dotaz jde i bez prohlížeče: `https://geneteka.genealodzy.pl/api/getAct.php?draw=1&start=0&length=10&bdm=B&rid=B&w=12sl&search_lastname=<příjmení>&search_name=&search_lastname2=&search_name2=&from_date=1850&to_date=1900&exac=1`
  (`bdm`/`rid` B křty, S sňatky, D úmrtí; `w` vojvodství, např. 12sl slezské, 08op opolské) → JSON. Past: `recordsTotal` > 0
  a prázdné `data` – zkus jen jedno příjmení bez křestního jména a užší roky. Stránkování opakuje řádky.
- Skeny některých polských far jsou i na Matricule (výše) nebo FamilySearch (níže).

## FamilySearch (přes uživatelův přihlášený prohlížeč)
- Přihlášení je potřeba i na hledání v indexech. České matriky tam skoro zindexované nejsou (Slovensko ano, hlavně křty).
- Jen když ho má uživatel otevřený a sám nabídne. Z kontextu stránky lze volat JSON API
  `https://www.familysearch.org/service/search/hr/v2/personas?q.surname=…&q.givenName=…&q.fatherGivenName=…&count=20`
  (`fetch(…, {credentials:'include'})`); výsledky v `entries[].content.gedcomx`.
- Užitečné na indexy matrik a hroby (BillionGraves, Find a Grave). Výsledek je vodítko – ověř v matrice.
- Neměň uživateli otevřené karty (po hledání vrať původní adresu). Stránky za Cloudflare neobcházej – ať je uživatel
  otevře sám a pošle snímek obrazovky.
- Snímky filmu (DGS): seznam přes `POST /search/filmdatainfo/image-data` s `{"type":"film-data","args":{"dgsNum":"00…","state":{"i":"0"},"locale":"cs"}}`
  (`images[]` = ARK). Snímek: `https://www.familysearch.org/service/records/storage/deepzoomcloud/dz/v1/<ARK 3:1:…>/$dist`
  (plné rozlišení), malé náhledy `…/image_files/8/0_0.jpg`. **Po ~1000 rychlých požadavcích přijde HTTP 429** a blokace
  na desítky minut – stahuj jen konkrétní snímky, nanejvýš pár za sekundu, hromadné procházení knih nedělej.
  U plných snímků přišla ochrana („Pardon Our Interruption“, místo JPEG stránka HTML) už po ~40 rychlých stažení –
  drž se pravidla prohlížeče ze SKILL.md (nejvýš 1 požadavek za 2 s, žádné smyčky) a nic neobcházej. Snímky omezené smlouvou vracejí 403 → `archivni_dotazy.md`.
- Obrázek z cizího webu přes prohlížeč na disk neuložíš bez souhlasu uživatele – zápis pak zapiš bez výřezu, s odkazem na
  ARK snímku (a výřez doplň, až snímek uloží uživatel).
- Indexátoři zaměňují role (rodiče × kmotři, „Other“ místo Father/Mother) – vždy ověř na snímku.

## Hroby a hřbitovy
- Kde jsou předci pohřbeni, víš z rozhovoru s rodinou (Fáze 1). Fotky náhrobků (jména, data, rodná příjmení) jsou
  cenný pramen hlavně pro 20. století, kde matriky ještě nejsou přístupné.
- Evidence hrobových míst: správa hřbitova (kdo je v hrobě uložen, kdo platí nájem – často žijící potomek);
  řada měst má online vyhledávání hrobů (Praha viz AHMP výše). Mezinárodně BillionGraves a Find a Grave.
- Datum z náhrobku (20. století) dovede k úmrtnímu zápisu; matrika zemřelých 1903–1949 pak uvádí i místo narození a sňatku,
  často s odkazem na knihu a stranu.
- **Parte známých osobností** (výtvarníci, historici umění, památkáři…): Archiv Národní galerie v Praze má Sbírku úmrtních
  oznámení (inventář jako PDF online, kopie na vyžádání).

## Vystěhovalci do USA
- Ptej se rodiny na výpisy, které má z Ancestry (placené – nestahuj nic hromadně, viz `soukromi.md`): seznam cestujících,
  odvodní karta z 1. světové války (WWI draft card – přesné datum narození), naturalizace.
- **Ellis Island** (statueofliberty.org → Passenger Search) jde bez přihlášení: výsledek dá věk, bydliště a loď, detail
  i snímek seznamu cestujících. Místa jsou často zkomolená („Senice“ místo Semice) – ověř podle věku a příbuzných na palubě.

## Noviny a ročenky – `tools/anno.py`, `tools/anno_snap.py`, `tools/kramerius.py`
**Kdy se vyplatí:** státní a vrchnostenští úředníci, soudci, učitelé, faráři, důstojníci, vojenští lékaři, notáři,
poštmistři, starostové, podnikatelé – noviny otiskovaly jmenování, přeložení, vyznamenání, penze, konkurzy, oznámení
sňatků a parte (zhruba od 1860). Z toho plyne, **kde člověk kdy žil** → kde hledat křty dětí, sňatek, úmrtí.
A když osoba „chybí“ v očekávaných matrikách (stěhovala se se službou). **Spíš ne:** sedláci a řemeslníci na vsi.
- ANNO (rakouské noviny 1700–1950, i Prager Zeitung, Wiener Zeitung): `python3 -I tools/anno.py '"Johann Nowak"' 1860 1915 [stran] [--snip]`
  – jména **německy** („Johann Nowak“, „Wenzel Dworschak“). Výřez místa: `tools/anno_snap.py <docId> "<dotaz>" pracovni/x.jpg`.
  ALEX a annoshow jsou za Cloudflare – neobcházet. Ze zkušebního cloudového prostředí ANNO spojení resetuje (nástroj je v pořádku, jde o síť).
- Kramerius NK ČR (české noviny, ročenky, adresáře): `python3 -I tools/kramerius.py 'text_ocr:"Jan Novák" AND datum_begin:[1900 TO 1910]'`.
  Text veřejné stránky: `…/search/api/v5.0/item/<uuid>/streams/TEXT_OCR` (přes `slusne.py curl`) – bývá v **UTF-16**
  (BOM FF FE); čtený jako UTF-8 nic nenajde. OCR adresářů slévá sousední jména na řádku → fráze v uvozovkách dává
  falešné shody, ověř na obrázku stránky. U vzácného příjmení ukážou adresáře a věstníky okresních hejtmanství (živnosti
  s čísly domů), odkud rod je. Panství obce rychle: Sommerův Popis království Českého (Kramerius, veřejný).
- **Díla nedostupná na trhu (DNNT)** čte jen přihlášený čtenář NK – v uživatelově prohlížeči, po jeho přihlášení, stránku
  po stránce. Celé stránky nestahuj ani nevytahuj jinou cestou (bezpečnostní kontrola to zablokovala jako obcházení
  přístupu). Licence je pro osobní potřebu: na web jen citace a krátký úryvek, bez výřezu.
- **knihovny.cz** (`https://www.knihovny.cz/api/v1/search?lookfor=…`) najde místní brožury (odboj, dějiny obce, spolky),
  které běžné hledání nenajde.
- Vojenské schematismy: fulltext na archive.org (např. `militrschematis13kriegoog` = 1850).
- **Rizika:** jména se opakují a fulltext šumí („Winter“ = i zima, „Novák“ = nový obyvatel). Ztotožni jen při shodě víc údajů (bydliště,
  funkce navazující na matriku, časová posloupnost). Zdroj je „J“ (jiný pramen) – vodítko a příběh, ne náhrada matriky.
- Výstřižky jsou skvělé na web: ulož do `dokumenty/noviny/`, přes `vyrez.py` a do `dokumenty.json`.
- Pořadí: nejdřív matriky; noviny, když chybí stopa kvůli stěhování, nebo když jde o úředníka/vojáka a chceme příběh.

## Ostatní portály – obecný postup
Nástroje pro ně hotové nejsou. Postupuj takto a výsledek zapiš do `STAV.md`, ať to příště víš:
1. Otevři portál v prohlížeči (Claude in Chrome / prohlížeč v Cursoru / `browser` v OMP / Playwright, pokud jsou k dispozici; jinak požádej uživatele).
   Najdi fond „Sbírka matrik“ / „Matriky“ a svazek podle obce a let.
2. **Snímek:** většina prohlížečů má tlačítko ke stažení obrázku – ulož do `pracovni/`. Když ne, podívej se v síťovém
   provozu, odkud se načítají dlaždice/obrázky (IIIF, DeepZoom, Zoomify), a stáhni celý obrázek touto cestou – jednotlivě,
   jen snímky, které čteš. Krajní možnost: požádej uživatele, ať snímek uloží a dá do `pracovni/`.
3. **Trvalý odkaz** na snímek (tlačítko „trvalý odkaz“/permalink, jinak URL svazku + číslo snímku) dej do `odkaz` v zápisu.
4. Svazek zapiš do `data/svazky.json` ručně: `"klic": {"archiv": "SOA Třeboň", "portal": "digi.ceskearchivy.cz",
   "svazek": "N Volary 1784–1820, sign. …", "popis": "obce…", "url": "<odkaz na svazek>"}`.
5. Dál stejně jako u ARON: `vyrez.py`, `ramecek.py`, přepis, osoby, deník.
6. Když se postup osvědčí, napiš pro portál vlastní malý nástroj podle `trebon.py` (bez prohlížeče, pokud to jde)
   a postup zapiš do `STAV.md`. Poznatek zapiš i do `poznamky_pro_skill.md` (pro správce skillu).

## Starší prameny (17.–18. století)
- **Soupis poddaných podle víry 1651** – celé rodiny s věkem, po krajích; edice Národního archivu jako PDF
  (nacr.cz, hledej „Soupis poddaných podle víry“ + kraj). Fulltext v PDF, příjmení často bez diakritiky / s jinou ortografií
  (Šaršoun → „Šaroun“, dlouhé ſ jako f). Ves je v rámci panství; poznamenej si stránku edice. Textová vrstva PDF
  má posunuté sloupce (věk a stav patří k jinému řádku) – text jen k hledání, čti vždy obraz strany; z PDF jde dělat výřezy.
- **Berní rula 1654** – jen hospodáři s půdou; edice a rejstříky v knihovnách (Kramerius/DNNT). Souhrnný svazek 2
  obsahuje i malé statky, které v krajských svazcích chybí.
- **Soupisy poddaných 18. století** (Mannschaftsbuch, Seelenliste, roční soupisy ve vrchnostenských registrech) – celé
  domácnosti s věkem, i podruzi, vojáci a nemanželské děti. Nejlepší **kontrola generace** před matrikami s čísly domů:
  když strom skáče mezi otcem a synem o 60 let, ověř věky v soupisu (1773, tereziánský katastr). Věk v soupisu bývá
  o 1–3 roky jinak než podle křtu – hledej křest ±3 roky. Rodina může být zapsaná u sousední vsi. SOA Litoměřice
  a SOA Třeboň je mají online (viz výše).
- **Gruntovní (pozemkové) knihy** – převody domů z otce na syna; online jen část (SOA Plzeň téměř vše, SOA Praha část,
  ostatní spíš badatelna). Fond „Velkostatek <panství>“. Dají vztahy otec–syn při předání („ujal grunt po otci svém“)
  i sourozence (dědické podíly, „za vystrojení svatby“); ceny do 1781 v kopách (ß), pak ve zlatých. Knihy řazené
  „po gruntech“ mají nadpis se jménem držitele z roku založení a statek vedou **pod stejným foliem** v navazujících
  knihách – z mladší knihy (nadpisy → folio) se dostaneš rovnou na stejné folio ve starší. Mladší kniha často opisuje
  starší zápisy („podle staré gruntovní knihy … na listu 162“). Posun snímek/folio se mění i uvnitř knihy (vložené
  lístky zakrývají stránku a list se snímá víckrát). Rejstříkové heslo může nést jméno vrchnosti, ne poddaného.
  Svatební smlouvy (věno, výminek rodičů, podpisy křížky) jsou výborný materiál na web (`pribehy.md`).
- **Urbáře 16.–17. století** (SOA Třeboň, SOA Praha, ARON) – most přes začátek matrik, jména hospodářů po vsích.
- **Další písemnosti vrchnosti (fond „Velkostatek <panství>“, do 1850)** – když matrika nestačí (původ přistěhovalce,
  vojáka, chybějící rodiče): soupisy poddaných (po letech, celé domácnosti s věkem), knihy svatebních smluv a kontraktů,
  sirotčí knihy a pozůstalostní spisy (dědici, jejich věk a bydliště), protokoly invalidů a propuštěných vojáků,
  výhostní (propouštěcí) listy, urbáře. Postup: najdi panství z matričního zápisu („poddaný panství X“) → kartu fondu
  v katalogu archivu (ARON / Digitální badatelna) → inventář otevři jako strom. Fond bývá i v **jiném** archivu než
  matriky; „Index ne“ v katalogu neznamená, že kniha nemá místní rejstřík (zkus začátek i konec knihy). Karta bez
  skenů neznamená, že kniha neexistuje → zapiš do `archivni_dotazy.md`. Stopu na vrchnostenský soud dávají i výzvy
  dědicům v novinách (ANNO, Prager Zeitung: „Edikt … Herrschaft X“).
- **Zemské desky** (Národní archiv; Morava MZA Brno) – evidence **deskových statků**: šlechta, svobodníci, majitelé
  deskových dvorů a některá města. Pro poddané sedláky a chalupníky v nich nic nebude (ti jsou v gruntovních knihách).
  Vyplatí se jen u předka-svobodníka nebo majitele statku; středověké a raně novověké zápisy částečně jako edice
  v Czech Medieval Sources (sources.cms.flu.cas.cz, kategorie „Desky zemské“). Originály jen v badatelně.
- **Mlýny a mlynáři – vodnimlyny.cz** (pozor: `databaze.vodnimlyny.cz` neexistuje, databáze je na
  `www.vodnimlyny.cz/mlyny/objekty/`). Karta mlýna má sekci **Historie** s držiteli mlýna v chronologickém sledu
  (často z gruntovních knih, urbářů, katastrů), prameny a fotky. Vyplatí se, když je předek mlynář nebo se narodil
  „ve mlýně“ / v čp. mlýna: potvrdí rod na mlýně přes generace, dá příběh a obrázky na web. Hledá se podle obce,
  katastru, toku i jména mlynáře (pole jsou dobrovolně vyplněná – „nenalezeno“ nic nedokazuje). Bez prohlížeče:
  GET `/mlyny/objekty/` (cookies), pak POST tamtéž s hlavičkou `X-Requested-With: XMLHttpRequest` a poli
  `_do=filter-form-submit`, `city=<Obec>` (nebo `miller=<Příjmení>`), `send=Filtrovat` → JSON, výsledky v
  `snippets["snippet--items"]` (bez té hlavičky vrátí nefiltrovaný seznam); přesný název obce dá
  `?do=citySuggestions&q=<Obec>`. Stránky „Prameny k poznávání vodních mlýnů“ na témže webu popisují, kde hledat dál
  (soupis mlýnů 1704, vodní knihy, kroniky mlynářských rodů). Údaje z karty ber jako odkaz na pramen, ne jako doklad –
  předka ověř v matrice / gruntovní knize.
- **Mapy stabilního katastru (1824–43)** – kde stál dům s číslem popisným: archivnimapy.cuzk.cz (Archiv ČÚZK).
  Na **císařských otiscích** chybí u části listů barvy a čísla domů. Lepší jsou **indikační skici**: mají čísla domů
  a u pozemků jméno majitele („N. 13“ = patří k domu čp. 13). Dům bez pozemků mimo ves = domkář bez polí.
  Jméno majitele samotného domu bývá jen v písemném operátu (archiv, ne online). Výřezy map patří na web k rodině.
  Na skice jsou černě čísla stavebních parcel a červeně čísla popisná (čp. ≠ st. p.); listy skici jsou číslované jinak
  než listy mapy – nejdřív si prohlédni náhledy po řadách. V prohlížeči (ags.cuzk.gov.cz/archiv): obec → klik do mapy →
  „1 mapa“ u Indikačních skic → odkaz `openmap.html?typ=skicic&idrastru=<ID>` (hodí se jako trvalý odkaz do zápisu;
  přístupový token aplikace pro vlastní dotazy nepoužívej). Polohy domů pro web dohledá skill **stare-adresy**
  (`web.md` → Domy); otázky „kde stál dům předků / kdo statek koupil“ řeší skill **Dějiny domu**
  (github.com/vzoha/dejiny-domu-skill – stabilní katastr bez prohlížeče, pozemkové knihy, sčítání a urbáře SOA Třeboň).
  Jeho nástroje mají vlastní brzdu se samostatným stavem – v projektu rodokmenu je spouštěj přes `tools/slusne.py`,
  ať se limity obou skillů nesčítají.
- **Dnešní adresa domu** podle čísla popisného: RÚIAN (ČÚZK, vrstva AdresniMisto). Pozor, staré centrum mívá od 19. století
  stejná čp., ale předměstí a vesnice čísla přečíslovávaly. Hodí se na „procházku po stopách předků“.
  Stavbu podle obce a čísla popisného najde i nahlizenidokn.cuzk.gov.cz (ověření adresy z dokladu); vlastník je za
  CAPTCHou a je to údaj o žijícím člověku – nezjišťuj ho.

## Vězni koncentračních táborů, oběti, nuceně nasazení, vysídlení (2. světová válka a po ní)
**Postup:** nejdřív česká databáze (`vezni.py` – má i rodiště a transporty), pak Arolsen (nejširší), pak tábor, kde člověk zemřel.
Shoda jména není ztotožnění – jména se v táborových dokumentech píší různě (Novák/Nowak/Novak) a datum narození tam bývá chybné; ověř
datum a místo narození na kartě a v rodině. Údaje jsou citlivé – na web jen se souhlasem rodiny (`soukromi.md`).
- **Památník Terezín – databáze politicky a rasově pronásledovaných osob** – `tools/vezni.py`: `hledat --prijmeni Novák --jmeno Josef [--narozeni "15. 3. 1910"]`,
  `detail <odkaz>`. Čeští vězni v Buchenwaldu, Dachau, Flossenbürgu, Mauthausenu, Ravensbrücku, Malé pevnosti, na Pankráci, v ghettu a internačním táboře.
  Detail uvádí bydliště, kdo vězně předal, transporty a čísla, a **kde je originál** (často Národní archiv).
  Stejná jména mají v adrese karty pořadové číslo (`…-karel`, `…-karel-3`) – vždy porovnej datum narození.
- **Gedenkstätte Plötzensee – Häftlingskartei** (gedenkstaette-ploetzensee.de): online karty vězňů berlínské trestnice
  a „Totenbuch“ s životopisy popravených. U dokumentů „od archivu“ v rodině porovnej sken se signaturou, kterou archiv
  opravdu poslal (rodinný popis bývá nepřesný).
- **Arolsen Archives** – `tools/arolsen.py`: `hledat "Příjmení Jméno 1905"` (spojení „a zároveň“, hláskové varianty; portál dává po 1000 záznamech, další přes `--od 1000`),
  filtry `--misto-narozeni Praha`, `--rodne`, `--cislo <číslo vězně>`, `--narodnost Czech`, `--vyznani Jewish` (národnost a vyznání jen přesným názvem z portálu; při chybě nástroj vypíše nabídku),
  `--podrobne` (otec, matka, vyznání, povolání, místo věznění, poslední bydliště), `karta <id> pracovni/x.jpg`
  stáhne kartotéční kartu nebo dokument. Obsahuje kartotéky Dachau, Mauthausenu, Buchenwaldu, Flossenbürgu, Terezína, **část Osvětimi**, seznamy
  transportů, nuceně nasazené a poválečné **vysídlené osoby (DP)**. Datum narození je v databázi měsíc/den/rok (nástroj převádí). U Osvětimi
  (a dalších) chybějí v databázi zápisy, které se nedochovaly; nenalezení neznamená, že tam člověk nebyl.
- **Mauthausen – Raum der Namen** – `tools/mauthausen.py hledat "Novak"`: jen zemřelí v Mauthausenu a pobočkách (Gusen, Ebensee, Melk…), často s fotografiemi a životopisem.
- **Židé z českých zemí** – `tools/obeti.py` (holocaust.cz, Terezínská iniciativa): jméno, narození, poslední bydliště před deportací, transporty.
- **Osvětim**: databáze Muzea Auschwitz (victims.auschwitz.org) má na serveru neúplný certifikát, ze skillu proto nejde; ověř ji v prohlížeči.
  Pro české oběti: holocaust.cz, Památník Terezín (rodinný tábor Terezín v Birkenau) a Arolsen.
- **Dachau**: Gedenkstätte Dachau odpovídá na písemné dotazy o vězních (`kz-gedenkstaette-dachau.de` → Forschung und Sammlung → Anfrage zu Häftlingen);
  online kartotéka je v Arolsenu. **Další tábory** (Buchenwald, Flossenbürg, Ravensbrück, Sachsenhausen): Arolsen a stránky pamětníků jednotlivých táborů.
- **Vysídlení a odsun**: Arolsen (DP, nuceně nasazení – vyhledej v `arolsen.py`), Národní archiv (fondy o odsunu a o uprchlících z pohraničí 1938 – v katalogu
  na na.gov.cz), **Lastenausgleichsarchiv Bayreuth** a **Sudetendeutsches Archiv München** (kartotéky odsunutých, vyplácení náhrad – nevyzkoušeno,
  weby ze zkušebního prostředí nedostupné), **Paměť národa** (memoryofnations.eu – vzpomínky pamětníků na osídlování, odsun, tábory; nevyzkoušeno).
- **Popravení, vězni gestapa, odboj**: Národní archiv (fondy Policejní ředitelství, Gestapo, Mimořádný lidový soud), Památník Terezín (Malá pevnost), Ústav pro studium
  totalitních režimů (ustrcr.cz). Katalogy a kartotéky jsou jen částečně online – zapiš dotaz do `archivni_dotazy.md`.

## Příjmení dnes a DNA
- **Rozšíření příjmení dnes**: kdejsme.cz (počty nositelů po okresech). Rychle ukáže, jestli je příjmení vzácné a kde
  jsou jeho „hnízda“. Při hledání vzdálených příbuzných vyškrtni vlastní rodinu.
- **DNA** (jen když o to uživatel stojí, a jeho rozhodnutí): autosomální test (MyHeritage, Ancestry) najde bratrance
  do ~5. kolene. **Y-DNA** (FamilyTreeDNA, Y-37 až Big Y) se dědí po meči beze změny. Ověří, jestli dvě linie stejného
  příjmení mají společného předka, a u nemanželského dítěte může shoda s jiným příjmením ukázat otce. Kontakt se žijícími
  příbuznými vždy jen přes uživatele.
Všechno, co jde jen v badatelně, zapisuj do `data/archivni_dotazy.md` (archiv, fond, inventární číslo, co hledat).
