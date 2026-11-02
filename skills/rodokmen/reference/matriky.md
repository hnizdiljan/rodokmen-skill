# Jak číst matriky – praktický návod

## Druhy knih
| Zkratka | Kniha | Co v ní je | Proč je cenná |
|---|---|---|---|
| **N** | narození (křty), *Liber natorum / baptisatorum*, *Geburtsbuch* | datum narození a křtu, dům (čp.), dítě, rodiče (od ~1784 i jejich rodiče a bydliště), kmotři, porodní bába | pohlaví, legitimita, rodiče matky → další generace |
| **O** | oddaní (sňatky), *Liber copulatorum*, *Trauungsbuch* | datum, dům, ženich a nevěsta (věk, stav, náboženství), jejich rodiče, svědci | **nejlepší první cíl** – otevírá dvě rodiny naráz |
| **Z** | zemřelí, *Liber defunctorum*, *Sterbebuch* | datum úmrtí a pohřbu, dům, jméno, věk, příčina | věk → odhad roku narození, stav (vdova po…) |
| **I** | index (rejstřík) k N/O/Z | jméno → datum / strana | rychlé hledání; **index bývá neúplný**, negativní výsledek v indexu nic nedokazuje |

Další prameny: sčítání lidu (1857–1921; domácnosti s daty narození), soupis poddaných 1651 (celé rodiny s věkem),
berní rula 1654 (jen hospodáři), gruntovní/pozemkové knihy (kdo vlastnil který dům – propojí generace přes dům),
vojenské záznamy, domovské listy, parte. Viz `portaly.md` a `playbook.md` §2.

## Lhůty (zákon 301/2000 Sb.)
Do archivu (a tedy online) jde svazek, až od jeho **posledního** zápisu uplyne: narození **100 let**, sňatky **75**, úmrtí **30**.
Mladší knihy jsou na matričním úřadě obce s rozšířenou působností / pověřeném úřadě – výpis dostane přímý příbuzný
(žádost + doklady o příbuzenství). Zapiš do `archivni_dotazy.md`.

**Žádost na matriční úřad** (pro předky narozené po ~1920 často jediná cesta dál):
- Žádej **doslovný výpis** (opis celého zápisu), ne jen matriční list – farní zápisy do 1949 uvádějí rodiče i prarodiče.
- Kdo může žádat a s jakými doklady, určuje zákon 301/2000 Sb. (§ 25 a § 25b; ověř aktuální znění). Přímý příbuzný
  dokládá vztah matričními doklady (rodný list svůj a rodičů…). Zápis starší než 100 let (§ 25b) ve svazku, který
  kvůli mladším zápisům ještě není v archivu, úřad podle zkušenosti vypíše i bez dokládání příbuzenství.
- Podání: poštou s ověřeným podpisem, **datovou schránkou** uživatele nebo e-mailem s uznávaným elektronickým
  podpisem. Identitu schránky úřadu ověř ve veřejném Seznamu datových schránek (mojedatovaschranka.cz → vyhledání
  schránky, bez přihlášení). Ty připravíš text žádosti (úřad, osoba, datum a místo události, jména rodičů, účel
  „genealogický výzkum“, vztah žadatele) do `archivni_dotazy.md`; odešle ho uživatel sám. Poplatek a lhůtu ověř na webu úřadu.
- Zápis o úmrtí přímého předka ve 20. století zná i rodina (parte, náhrobek) – i to pomůže úřadu zápis najít.
- Než napíšeš do archivu nebo na úřad, zkus **oklikou online**: křty sourozenců a mladších dětí uvádějí rodiště
  rodičů i prarodiče, poznámka „křestní list vydán …“ ukáže přibližné datum sňatku, fondy obecních archivů (domovské
  listy, matriky příslušníků) najdeš v katalogu archivu i bez filtru „Sbírka matrik“. Seznam `archivni_dotazy.md`
  po několika kolech zastará: před odesláním projdi každý bod proti `zaznamy.json` a deníku (odeslat / jen potvrzení /
  už vyřešeno jinou cestou).

## Jak vypadá hledání v praxi
1. **Obec → farnost.** Malé vesnice patřily k faře v sousední obci; popis svazku vyjmenovává všechny obce farnosti.
   Hledej obec v popisu svazku (`aron_search.py "Obec"`), ne jen v názvu – a hledej i podle obce, ne jen podle fary
   z pozdějšího zápisu: obec mohla mít vlastní matriku (filiální kostel, lokálie), i když list vydala mateřská fara.
   Obec rozdělená mezi dvě fary má dvě řady knih, každou jen pro „svá“ čísla domů.
2. **Svazek podle roku a druhu.** Pozor na překryvy: jedna kniha pro více obcí, zvláštní knihy pro jednotlivé obce.
   **Druhopisy** (duplikáty pro děkanát nebo úřad, např. „T“ svazky v ZA Opava) mívají N, O a Z jednoho roku u sebe –
   hodí se, když originál chybí, je nečitelný nebo velký.
3. **Index, pak kniha.** Index řazený po písmenech a letech dá stránku/folio; číslo folia nepřeváděj pevným offsetem
   na číslo snímku. Najdi folio podle číslování přímo v knize a zkontroluj okolní strany – vložené, chybějící nebo
   nečíslované listy mohou vztah mezi folií a snímkem změnit.
   Posun „snímek – strana“ se v knize mění (vložené listy, chybějící strany) – přečti číslo strany na náhledu a dopočítej.
   U starých far se vyplatí nejdřív najít **souhrnný index** přes víc desetiletí (např. N/O/Z 1636–1746) – dovede
   rychle až do 17. století. Rejstříky bývají podle **německého pravopisu**: česká jména na O a V hledej i pod W
   (Otava = Wotawa, Vávra = Wawra). Knihy pro více obcí bývají řazené po obcích, rejstřík na konci.
   Velké fary mají rejstříky i jako **samostatné svazky** (např. rejstřík oddaných přes 300 let) – hledej je nejdřív.
   **Když matrika chybí** (není online nebo se nedochovala), zkus rejstřík – bývá vedený zvlášť a přežil i tam, kde kniha
   ne. Zápis v rejstříku dokládá datum, místo a otce; zapiš ho jako `prob` (opis, ne originál) a matriku zkus později.
4. **Bez indexu: listuj chronologicky.** Odhadni pozici podle let na prvních a posledních snímcích svazku (půlení intervalu),
   ne procházením po deseti snímcích. U knih, kam se vracíš, si veď **mapu knihy** v `pracovni/<svazek>/mapa.md`
   (snímek | folio/pagina | obec | druh | roky) – ušetří další hledání i zadání pomocníkům. Rychle ji uděláš z náhledů:
   ořízni horní pruh se záhlavím (roky, obec; ořez v pixelech, procentní posun v IM7 nefunguje spolehlivě), připiš číslo
   snímku a slep 6–10 pod sebe (`magick … -append`). Pozor: „fol.“ v rejstříku bývá ve skutečnosti pagina (strana);
   eBadatelna v `info` uvádí strany, ne snímky (snímek ≈ dvojstrana). Knihy řazené po vsích mívají oddíl pod starším
   jménem vsi (záhlaví stránek ho prozradí) a první strana oddílu bývá na snímku s předsádkou.
   Staré knihy svázané z **ročních výtahů** (Extractus, Consignatio, 18. stol.) nemusí jít po sobě a ročníky chybí;
   rok bývá jen v nadpisu výtahu. Než napíšeš „zápis tam není“, ověř hlavičky ročníků.
   **Nejisté datum** (číslice z pozdější poznámky): nejdřív projdi všechny možné roky v domovské farnosti, teprve pak
   okolní fary. (Skutečná chyba: „9?“ přečteno jako 97, prošlo se pět okolních far; sňatek byl doma o pět let dřív.)
5. **Přečti celý zápis**, pak se podívej i na okolí (dvojčata, další děti stejných rodičů).
6. **Sňatek se obvykle konal ve farnosti nevěsty** (v jejím bydlišti) – hledej ho nejdřív tam, pak ve faře ženicha.
   Když oddací rejstřík pod nevěstiným příjmením nic neukáže, zkus také příjmení ženicha; rejstříky se mohou lišit
   způsobem řazení.
   Nedaří se? Ve křtu dítěte bývá (Praha ~1880–1890) připsané datum a místo sňatku rodičů – ověř ho v oddaných.
7. **Rodina v katolické matrice chybí? Zkus evangelickou nebo židovskou.** Po toleranci (1781) vedly vlastní matriky
   evangelické sbory (a. v. i h. v.), jeden sbor pokrýval desítky obcí; v ARONu mají signatury „R …“ a `aron_search.py`
   je najde podle obce. Ve východních Čechách časté (Rychnovsko, Dobrušsko, Opočensko). Židovské matriky (Národní archiv, nástroj `vademecum.py`) viz `portaly.md`.
   Ve 20. století (1920–1945) zkus i **civilní matriky** lidí bez vyznání u okresních úřadů (vyzkoušeno v SOA Třeboň, viz `portaly.md`),
   v Praze civilní sňatky Magistrátu (AHMP), v Sudetech 1939–1945 německé civilní matriky (Standesamt, SOA Litoměřice).
   Evangelíci v katolických knihách: 1782–1800 zapisoval katolický farář i křty provedené pastorem (sloupec křtícího,
   „in Oratorio Helvetico“), knihy 1782–1784 mívají na konci oddíl „Consignatio baptizatorum acatholicorum“ (v rejstříku
   nebývá), pohřeb „sepult. in illorum loco“ = na nekatolickém hřbitově. Matriky tolerančních sborů jsou česky a tabulkově
   (čitelnější než katolický duplikát se zkomolenými jmény); jejich rejstříky bývají řazené podle křestního jména dítěte.
   Filiální kostely mívají vlastní knihy pod jménem fary – hledej podle osady i podle fary.
8. **Sňatek v knize řazené po vsích** bývá v oddílu vsi nevěsty, někdy ženicha – projdi obě. Křestní list zmíněný
   v oddacím zápisu („z fary v …“) vede ke křtu nevěsty v cizí farnosti (začni rejstříkem té fary).
9. **Odkazy mezi zápisy ve 20. století** ušetří listování: oddací zápisy po 1918 mívají „Dle Can. 1103 § 2 poznačeno …
   T. XI pag. 453“ = svazek a strana křtu, křestní zápisy „viz matriku oddaných tom IV pag. 314“, úmrtní zápisy po ~1920
   uvádějí datum a místo narození i sňatku. Okrajová poznámka „list vydán <datum>“ u křtu (19. století) ukazuje přibližné
   datum sňatku a sedí s přílohou oddacího zápisu jinde. Stačí přepočítat stranu na snímek.

## Čtení písma
- Kurentový rejstřík: stáhni plné rozlišení a rozřež stránku na čtvrtiny (sloupec jmen + data),
  `magick f.jpg -crop 1250x1650+X+Y +repage ctvrt.jpg`. **Dopisované řádky** se snadno přečtou špatně (Franziska × Heinrich,
  strana 131 × 151) – údaj z rejstříku vždy ověř v matrice.
- **Kniha bez rejstříku** (hledáš rodiče podle příjmení): stáhni jen sloupec otce (nebo matky) z mnoha snímků
  v nízkém rozlišení (`aron_img.py <apu> <n> 2 pracovni/x/o<n>.jpg x0,y0,x1,y1` – výřez nastav podle sloupce na jednom snímku, víc
  najednou přes `xargs -P 4`) a slož je po osmi vedle sebe (`magick montage o1.jpg … o8.jpg -tile 8x1 -geometry +4+0 m.jpg`).
  Úroveň 2 na čtení příjmení stačí, menší ne. Nalezený zápis pak stáhni celý v úrovni 1 nebo 0 (0 = plné rozlišení).
  Nezapomeň na nemanželské děti – otec je prázdný a příjmení je ve sloupci matky.
- Do ~1780 latina nebo čeština, pak hodně němčina (kurent), od ~1860 často čeština, ve 20. století čeština.
- Česká jména v němčině/latině: Johann/Joannes = Jan, Wenzel/Wenceslaus = Václav, Joseph = Josef, Franz/Franciscus = František,
  Maria = Marie, Anna, Katharina = Kateřina, Barbara = Barbora, Magdalena = Majdalena/Magdaléna, Theresia = Terezie,
  Ludmilla = Lidmila, Dorothea = Dorota, Apollonia = Apolena, Georg/Georgius = Jiří, Matthias = Matěj, Adalbert = Vojtěch.
- Příjmení se píše foneticky a mění se (Šaršon/Scharschon/Šaršoun, Kroupa/Kraupa). Hledej všechny varianty.
- Ženská příjmení v němčině bez „-ová“ (Maria Novak = Marie Nováková).
- Názvy obcí mívají staré tvary, třeba s předsunutým „V“ („Volešnice“ = Olešnice); při hledání obce zkus i ty.
- Kurent: dlouhé „ſ“ vypadá jako „f“, „e“ jako „n“, „h“ s kličkou dolů. Při nejistotě porovnej se stejným písmenem
  jinde na stránce stejné ruky – i u „divného“ příjmení (koncové „k“ psané skoro jako „r“: „-ek“ vypadá jako „-er“).
  Slovo rozdělené přes konec řádku („Urlau-“ / „ber“) dočti na začátku dalšího řádku.
  Další záměny z praxe: „h“ s kličkou čtené jako „š“ (Wohanka → „Wošatka“), „k“ jako „lb“, „G“ = J („Gerzabek“ = Jeřábek),
  „er/el/ir“ splývá v jeden tah, „A“ s kroužkem nad „u“ (Aůdrnice = Údrnice) vypadá jako „K“. Jména psaná jinou
  počáteční hláskou (Gabrhel → „Kabriel“) chybí v rejstříku pod očekávaným písmenem; u neznámé obce zkus vynechat
  první písmeno a varianty Ou-/U-/Au-, W/V/O.
- Zápis přes dvě strany (dva snímky): slep oba kusy (`magick a.jpg b.jpg -append x.jpg`) a výřez dělej z něj.
- Bledé snímky: `magick x.jpg -colorspace Gray -normalize -level 15%,75% x_k.jpg` (velmi bledé knihy až `-level 30%,85%`);
  u nich nejdřív najdi číslo domu v úzkém sloupci přes celou výšku, teprve pak čti jména.
- Daty bývají svátky (*Dominica*, *festum S. Joannis*) – v nejasných případech dopočítej.

### Slovníček (lat. / něm. → česky)
| výraz | význam |
|---|---|
| *natus / geboren*, *baptisatus / getauft* | narozen, pokřtěn |
| *copulati / getraut*, *sponsus / Bräutigam*, *sponsa / Braut* | oddáni, ženich, nevěsta |
| *mortuus, sepultus / gestorben, begraben* | zemřel, pohřben |
| *legitimus / ehelich*, *illegitimus / unehelich* | manželský, nemanželský |
| *viduus, vidua / Witwer, Witwe* | vdovec, vdova |
| *filius, filia / Sohn, Tochter* | syn, dcera |
| *patrini / Pathen*, *testes / Zeugen*, *obstetrix / Hebamme* | kmotři, svědci, porodní bába |
| *agricola, rusticus / Bauer* | sedlák, rolník |
| *Häusler*, *casarius* | domkář |
| *Inwohner / inquilinus*, *podruh* | podruh (bydlel v cizím domě) |
| *Gärtner* (na vsi) | zahradník = malý usedlík, ne nutně pěstitel |
| *Inleute*, *Taglöhner* | podruzi, nádeníci |
| *Bürger*, *civis* | měšťan |
| *Schneider / sartor*, *Schuhmacher / sutor*, *Weber / textor*, *Schmied / faber*, *Müller / molitor* | krejčí, švec, tkadlec, kovář, mlynář |
| *N.* / *No.* / *Haus Nr.* | číslo domu (popisné) |
| *ex*, *aus*, *von* | z (obce) |
| *Lungensucht*, *Abzehrung* | souchotiny (TBC) |
| *Cholera*, *Blattern* | cholera, neštovice |
| *Fraisen* | křeče (časté u kojenců) |

## Odhad roků
- Věk při úmrtí/sňatku je často zaokrouhlený o ±2–5 let. Uváděj „asi 1756“ a hledej křest v širším okně.
  I přesné datum narození v oddacím zápisu mívá špatný měsíc: když křest v něm není, projdi celý rok ±1 a farnost
  matky (dítě se často narodilo u jejích rodičů).
- Nevěsta mívala 18–28, ženich 22–32; děti po 1,5–3 letech.
- „Vdovec“ u ženicha = hledej první manželství a děti z něj.
- Při přepisu křtu ověř měsíc podle záhlaví příslušného sloupce a nepopleť číslo domu porodní báby
  (*obstetrix*, *Hebamme*) s rodištěm dítěte.

## Stavy údajů v datech
| stav | kdy |
|---|---|
| `doc` | přečteno přímo na snímku zápisu, který osobu jednoznačně identifikuje |
| `prob` | silná shoda (jméno, doba, místo, dům, řemeslo), ale bez přímého zápisu; vždy `note` proč |
| `fam` | od rodiny / z rodinného dokumentu |
| `mh` | jen z cizího stromu na internetu |
| `unk` | známe jen místo v rodokmenu |

## Ověřování: od zápisu k závěru
- **Zápis doložen × vazba doložena.** U každého ztotožnění rozliš dvě věci: (1) zápis existuje a čteš ho správně,
  (2) zápis patří právě této osobě v rodokmenu. `doc` chce obojí. Rejstřík, index sčítání, cizí strom nebo shoda
  jména a čísla domu jsou **kandidát**, ne doklad vazby. V poznámce (`note`) napiš, čím je vazba doložená
  (rodiče v zápisu, dům + manželka, věk…). Nezávislá kontrola závěrů (jiný model nebo čerstvé sezení, které dostane jen
  data a zápisy) najde přehnané formulace („syn“, kde je doložený jen „Jan Novák téhož roku“).
- **Nezávislé druhé čtení sporného slova:** dej výřez druhému čtenáři (pomocníkovi, jinému modelu) **bez svého čtení
  v zadání** – jinak ho jen potvrdí. Pak srovnej se stejným slovem nebo písmenem od **téhož písaře na téže stránce**
  (výřezy vedle sebe). Tak se rozhodla sporná jména, kde se kurentní „k“ čte jako „lb“.
- **Genealogický důkazní standard (GPS)** – mezinárodní měřítko spolehlivého závěru (BCG). Ve skillu ho plníš takto:
  1. *Důkladné hledání* – všechny dostupné prameny k otázce, ne první shoda (matrika, rejstřík, sourozenci, sčítání,
     gruntovní knihy); deník s rozsahem i u negativních výsledků.
  2. *Přesná citace* – svazek, snímek, trvalý odkaz, výřez (`zaznamy.json`, `svazky.json`).
  3. *Rozbor a korelace* – originál × opis/rejstřík, kdo údaj nahlásil a jak dlouho po události (věk při úmrtí
     hlásí pozůstalí); ztotožnění na dva nezávislé údaje (`playbook.md` §5.4).
  4. *Řešení rozporů* – rozpory nezamlčuj, zapiš do `ISSUES` a rozhodni podle spolehlivějšího pramene.
  5. *Zdůvodněný závěr* – stav `doc`/`prob` + `note` proč; u nepřímého závěru (nikde nestojí výslovně, skládá se
     z víc zápisů) napiš krátký důkazní rozbor podle `playbook.md` §5.2.5 do poznámky nebo `HYPOTEZY`.

## Typické pasti (ze skutečného výzkumu)
- Písař spletl jméno dědečka (Josef místo Václava) – rozhodne více zápisů téže rodiny.
- Dítě zapsané pod jiným křestním jménem, než jakým ho volala rodina (Františka → v rodině Anna).
- Sňatek pár měsíců před porodem nebo po něm – není chyba, jen „svatba na poslední chvíli“; zajímavost pro web.
- Nemanželské dítě nese příjmení matky; otec chybí nebo je dopsán později (legitimace na okraji).
- Stejný předek dvakrát v rodokmenu (vzdálení příbuzní se vzali) – v datech `SAME`.
- Index nenašel ≠ zápis neexistuje. Zapiš, co přesně jsi prošel.
- Farnost má pro každou obec **vlastní knihu**, ale čísla zápisů v roce jsou společná pro celou farnost – v knize
  jedné obce proto čísla „chybí“. Nejsou to chybějící strany; zbytek je v knihách ostatních obcí.
- Pomocníci (subagenti) a OCR/AI čtou historické písmo chybně – vždy ověř sám (viz `playbook.md` §1 bod 10).
  U německých tištěných formulářů (Vídeň a další města, 2. polovina 19. století) bývají chybně hlavně **roky, stav
  (ledig × Witwer), povolání, adresy a jména svědků** – ty ověř na výřezu vždy, i když pomocník hlásí „jisté“.
- Velké kolo s pomocníky: šablona zadání a pravidla (kontrolní zápis, tabulka přečtených snímků, „nezobrazeno“ není
  negativní výsledek) jsou v `pomocnici.md`. Kurent 1. poloviny 19. století ve středním rozlišení ARON (úroveň 1)
  spolehlivě nepřečte nikdo – chtěj plné rozlišení a výřez sloupce. Víc pomocníků na jednom archivu ho přetíží
  (snímek pak trvá minuty) – rozlož je mezi archivy (ARON, Porta fontium, eBadatelna).
- **Dva muži stejného jména v jedné vsi** jsou běžní (i čtyři Janové téhož příjmení v okruhu 5 km). Před přiřazením
  křtu nebo sňatku sepiš všechny páry „muž × manželka“ z křtů dětí a porovnej **číslo domu a jméno manželky**.
  Opačná past: „otec a syn“ stejného jména může být jeden muž se dvěma manželstvími (stejný dům, stejní kmotři u dětí
  z obou manželství, úmrtí první ženy těsně před druhým sňatkem, v úmrtní knize jen jeden muž toho jména).
- „Ideální“ křest může patřit dítěti, které brzy zemřelo; další sourozenec pak dostal stejné jméno (Anna 1795 † 1796 →
  Anna 1797). Vždy zkontroluj úmrtí dětí.
- **Chybné čtení se šíří**: jméno přečtené jednou nejistě si další čtenář „potvrdí“ v dalších zápisech, protože ho
  očekává. Ověř ho ve všech zápisech rodiny, hlavně v sňatku rodičů (bývá psaný nejpečlivěji).
- Kontroluj věk kmotrů a svědků – kmotr, kterému by bylo 7 let, nemůže být otec nevěsty.
- **Spor o rodné příjmení** rozhodnou křty vnuků (19. století uvádí rodiče obou rodičů, často s rodným příjmením
  a vsí – projdi všechny sourozence, ne jen přímého předka) a úmrtní zápisy manželek („manželka X., rozená Y“).
- Rejstříky (hlavně 18. století a novodobé ručně opisované) **vynechávají** křty i sňatky, mají posunuté sloupce dnů
  a stran o řádek, špatné roky, sloučená příjmení, chyby z „ditto“ (jméno otce opsané z řádku nad ním) a odkazují
  na stránku s posunem (str. 358 → zápis na 356). Na udané straně ± 2 čti všechny zápisy z dané vsi; rok vždy podle
  hlavičky v knize. Rejstříkový zápis může patřit kmotrovi, ne dítěti. Ztotožnění jen podle rejstříku se do dat
  nedostane – jednou tak do rodokmenu vlezla cizí rodina. Když rejstřík oddaných mlčí: z rejstříku narozených zjisti
  první dítě a projdi oddané 1–2 roky před ním.
- Rejstřík nemusí pokrývat všechny obce fary ani celé období (kombinovaný rejstřík 1784–1906 měl hlavní obec jen
  do ~1845) – nejdřív ověř, které obce a roky pokrývá.
- Tužkou připsaná data narození snoubenců u starých oddacích zápisů (pozdější badatel) vedou přímo ke křtům – přečti
  je, ale ber je jako stopu a ověř.
- Nemanželské dítě matky se stejným jménem: rodinný strom může „dosadit“ za rodiče prarodiče (nemanželská dcera
  svobodné matky vedená jako dcera matčina bratra). Rozhodne zápis o sňatku nebo úmrtí dítěte (uvádí matku) a to, zda je v matrice
  jiné dítě daného jména.

## Technické pasti (macOS, zsh) – napiš je i pomocníkům do zadání
- Čistý Mac: `python3` a `git` hlásí „You have not agreed to the Xcode license“ → uživatel spustí `sudo xcodebuild -license`.
  Po instalaci Homebrew bývá `/opt/homebrew/bin` mimo PATH shellu agenta (`node`, `magick` „not found“) – před příkazy
  `export PATH="/opt/homebrew/bin:$PATH"` a zapiš to do `AGENTS.md` projektu.
- Shell je zsh: `for a in "x y z"; do set -- $a` slova nerozdělí (v zsh `${=a}`); `ls F*` bez shody = chyba
  „no matches found“; `echo ====` je chyba (`=` na začátku slova). Složitější smyčky pouštěj přes `bash -c '…'`.
- ImageMagick: seznam souborů předávej jako jednotlivé argumenty, ne jednou proměnnou s mezerami.
  `-annotate` potřebuje písmo: `-font /System/Library/Fonts/Supplemental/Arial.ttf` (bez něj spadne na „unable to read
  font“; totéž `montage` s popisky) – pořadí výřezů raději vypiš zvlášť.
- Ověření čtení: `python3 -I tools/overit.py <snímek> x0,y0,x1,y1 pracovni/over [v]` (zlomky 0–1, ne pixely) – zápis rozdělený na dvě poloviny
  zmenšené na 1900 px (dvoustrana je jinak nečitelná).
- Výřez pro web (`vyrez.py`) dělej jen na **čtený zápis** (případně s hlavičkou sloupců), ne na celou dvoustranu –
  na webu by byl nečitelně malý. Celá stránka je v `zdroje/` a na portálu přes odkaz.

## Technické pasti (Windows) – napiš je i pomocníkům do zadání
(Nahrazují první dva body macOS sekce; body o `overit.py` a výřezu platí i tady.)
- Python: `python -I -X utf8 tools/<nástroj>.py` (ne `python3` – bývá to nefunkční alias z Microsoft Store). Bez `-X utf8`
  je výstup do roury v cp1250: čeština se rozbije a skripty spadnou na „≈“ a „→“ (nástroje skillu si výstup přepnou
  do UTF-8 samy, vlastní jednorázové skripty ne – `-X utf8` proto používej vždy). Totéž platí při
  přesměrování do souboru (soubor z `… --osoby > x.py` by jinak vznikl v cp1250; ve Windows PowerShellu 5.1 `>` dokonce
  zapisuje UTF-16 – přesměrovávej v Git Bash). Proměnná `PYTHONUTF8` s `-I` nefunguje.
- ImageMagick je `magick`, nikdy `convert` (`convert` je ve Windows systémový nástroj na převod disku z FAT na NTFS).
  Po instalaci přes winget je `magick` v PATH až po restartu Claude Code / Codexu / Cursoru / OMP. Písmo pro `-annotate`: `-font C:/Windows/Fonts/arial.ttf`.
- Limit délky příkazové řádky je 32 767 znaků – stovky souborů (dlaždic) v jednom příkazu `magick` neprojdou
  (WinError 206); skládej po řádcích.
- Skripty `.sh` přes Git Bash (`bash tools/…`). Markdown a JSON nikdy neupravuj `sed -i` (escapy v Git Bash rozbijí
  soubor) – data zapisuj podle pravidla „Zápis do dat“ v SKILL.md.
- Windows nerozlišuje velikost písmen v názvech (`o_29.jpg` = `O_29.jpg`) – náhled a plné rozlišení odliš předponou
  (`nahled_`, `plne_`), jinak se přepíšou.
- Git Bash převádí argument začínající `/` na cestu Windows (`/api/x` → `C:/Program Files/Git/api/x`). Cesty URL
  předávej celé (`https://…`) nebo bez úvodního lomítka.
- Datové soubory zapisuj v UTF-8 **bez BOM** (Windows PowerShell 5.1 s `-Encoding UTF8` přidá BOM a `osoby.py` pak nejde načíst).
