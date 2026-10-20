# Week 7 — zajednički izvještaj prije/poslije

Početna analiza i specifikacija su završene. Implementacija M1 i završno mjerenje slijede.

## Cilj i početno stanje

Cilj weekly assignmenta je izmjeriti početni RAG sistem na fiksnom skupu, dokumentovati propuste, izvesti jednu kontrolisanu promjenu i uporediti stanje prije i poslije. Početni kod je sačuvan u commitu `c233b11f7a7faa8986236732de54be9453909d44`. Sistem radi lokalno nad deset dokumenata priručnika. Početna konfiguracija koristi chunkovanje po karakterima (`CHUNK_SIZE=140`, `CHUNK_OVERLAP=30`), `TOP_K=2` i ne filtrira zastarjele verzije. Potpuna podešavanja su u [početnim nalazima](baseline-findings.md) i izvornom [before rezultatu](../results/before.json).

Okruženje: lokalni `.venv` s Pythonom **3.12.14** i `pytest` **8.3.3**, sa zavisnostima iz neizmijenjenog `requirements.txt`. Komanda `.venv/bin/python -m pytest` prošla je **18/18** početnih testova, status 0. Početni eval pokrenut je komandom `.venv/bin/python -m src.eval_runner --out results/before.json`, status 0. Otisak eval skupa je `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

## Početni rezultati i propusti

| Metrika | Prije |
| --- | ---: |
| Prošla pitanja | 6/12 |
| Tačnost odluke odgovor/odbijanje (`behaviour_accuracy`) | 0.8333 |
| Pogodak očekivanog dokumenta kod podržanih pitanja (`retrieval_hit_rate`) | 0.7778 |
| Srednja preciznost citata među datim odgovorima | 0.4545 |

**E04** i **E09** traže rok zamjene laptopa. Oba citiraju očekivani `hb-01`, ali izabrani chunkovi ne sadrže „5 business days”; oba padaju uprkos `citation_precision=1.0`. **E06** citira pravilo iz 2024. sa „2 days per week”, iako važeći izvor iz 2026. kaže „3 days per week”. Tabela svih pitanja, citati i skorovi su u [početnim nalazima](baseline-findings.md) i [sačuvanim CLI provjerama](baseline-cli-checks.txt).

`citation_precision` računa udio citata iz očekivanog **dokumenta**, a ne potvrđuje da citirani chunk sadrži traženu činjenicu. `behaviour_accuracy` mjeri odluku odgovor/odbijanje, a ne sadržinsku tačnost. Isti fiksni skup koristimo za dijagnostiku i mjerenje, pa rezultat poslije promjene sam po sebi ne dokazuje generalizaciju na nova pitanja.

## Izabrana intervencija

Izabrana je jedna intervencija, **M1 — sentence-aware chunking**. [Specifikacija](change-spec.md) sadrži ugovor funkcije, hipotezu i način provjere. Početni dokazi motivišu M1, ali ne garantuju da će se potrebni chunk naći među prva dva rezultata.

## Implementacija

**Čeka implementaciju.** Koleginica treba da implementira M1 u dozvoljenom obimu i doda ciljane testove prema [uputstvu za predaju](handoff.md). Ovdje zatim zabilježiti stvarni diff ili commit i rezultat svih testova.

## Završno mjerenje i poređenje

**Čeka završno mjerenje.** Ovdje unijeti komandu i `results/after.json`, otisak i postavke, metrike poslije, tabelu svih 12 pitanja, te izlaz `src.eval_compare` za iste eval podatke. Sačuvati izvorne rezultate i izlaz poređenja.

## Ručna provjera

**Čeka završno mjerenje.** Za pitanje čiji se ishod promijeni navesti CLI komandu s `--show-retrieved`, stvarni odgovor, citat, verziju i status izvora. Ako se nijedno pitanje ne promijeni, to izričito navesti.

## Regresije i preostala ograničenja

**Čeka završno mjerenje.** Navesti svaku regresiju i najmanje jedno preostalo ograničenje na osnovu after rezultata. Početni propusti se ne smiju unaprijed proglašavati preostalim poslije M1.

## Zaključak

**Čeka završno mjerenje.** Zaključak treba da uporedi dokaze prije i poslije, uključujući mogućnost da M1 ne potvrdi hipotezu.

## Pregled drugog para

**Čeka komentar drugog para.** Ovdje zabilježiti stvarni komentar i odgovor na njega.

## Doprinos članica i korišćenje AI-ja

Elena je vodila početnu analizu, pregled rezultata i pripremu specifikacije uz AI asistente. Codex je u ovoj fazi izvršavao komande i pripremao kodnu bazu, rezultate i dokumentaciju pod njenim uputstvima. Implementacija M1 i završno mjerenje planirani su za koleginicu; njen rad još nije izvršen niti je njeno ime ovdje potvrđeno.

**Demonstrator:** Dogovara se.
