# Week 7 — radni nacrt zajedničkog izvještaja prije/poslije

**Status:** radni nacrt. Originalni tutorov šablon još nije dostupan; sadržaj treba prenijeti u njega kada bude dostavljen. Ovdje su popunjene samo potvrđene informacije.

## Cilj i početno stanje

Zadatak je izmjeriti početni RAG sistem nad fiksnim skupom, dokumentovati propuste, izvesti tačno jednu kontrolisanu promjenu i uporediti rezultat prije i poslije. Početni kod je sačuvan u commitu `c233b11f7a7faa8986236732de54be9453909d44`. Sistem radi lokalno nad deset dokumenata priručnika. Početna konfiguracija koristi chunkovanje po karakterima (`CHUNK_SIZE=140`, `CHUNK_OVERLAP=30`), `TOP_K=2`, bez filtriranja zastarjelih verzija. Sva podešavanja su u [početnim nalazima](baseline-findings.md) i izvornom [before rezultatu](../results/before.json).

Okruženje: lokalni `.venv` s Pythonom **3.12.14** i `pytest` **8.3.3**, zavisnosti iz neizmijenjenog `requirements.txt`. Početna komanda `.venv/bin/python -m pytest` prošla je **18/18** testova, status 0. Početni eval pokrenut je sa `.venv/bin/python -m src.eval_runner --out results/before.json`, status 0. Otisak eval skupa: `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

## Početni rezultati

| Metrika | Prije |
| --- | ---: |
| Prošla pitanja | 6/12 |
| Tačnost odluke odgovor/odbijanje (`behaviour_accuracy`) | 0.8333 |
| Pogodak očekivanog dokumenta kod podržanih pitanja (`retrieval_hit_rate`) | 0.7778 |
| Srednja preciznost citata među datim odgovorima | 0.4545 |

Dokazani primjeri: **E04** i **E09** traže rok zamjene laptopa. Oba citiraju očekivani `hb-01`, ali izabrani chunkovi ne sadrže „5 business days”; zato oba padaju uprkos `citation_precision=1.0`. **E06** citira pravilo iz 2024. sa „2 days per week”, iako važeći izvor iz 2026. kaže „3 days per week”. Za sva pitanja, stvarne citate, skorove i detalje vidi [početne nalaze](baseline-findings.md) i [sačuvane CLI provjere](baseline-cli-checks.txt).

Ograničenje metrika: `citation_precision` računa udio citata iz očekivanog **dokumenta**, ne potvrđuje da citirani chunk sadrži traženu činjenicu. `behaviour_accuracy` mjeri samo odluku odgovor/odbijanje, ne sadržinsku tačnost. Isti fiksni skup služi za dijagnostiku i mjerenje, pa rezultat poslije promjene sam po sebi neće dokazati generalizaciju na nova pitanja.

## Izabrana promjena

Izabrana je jedna intervencija, **M1 — sentence-aware chunking**. [Specifikacija prije implementacije](change-spec.md) određuje ugovor funkcije, neizmijenjene postavke, hipotezu i način provjere. Implementacija: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.

## Završno mjerenje i poređenje

- Testovi poslije promjene: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- `results/after.json`, otisak skupa, postavke i metrika poslije: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- Tabela svih pitanja poslije i promjene po pitanju: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- Popravljena pitanja, regresije i nepromijenjeni neuspjesi: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- Ručna provjera odgovora i citata nakon promjene: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- Zaključak o učinku M1 i najmanje jedno preostalo ograničenje nakon promjene: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.

Postojeći početni propusti ne smiju se unaprijed označiti kao dokazano preostali poslije M1; to zahtijeva novo mjerenje.

## Doprinos i preostale obaveze

- Elena vodi početnu analizu, pregled rezultata i pripremu specifikacije uz AI asistente. Kod, komande i dokumentaciju u ovoj fazi izvršavao/pripremao je Codex.
- Implementacija M1 i završno mjerenje planirani su za koleginicu; **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**. Njeno ime ovdje nije potvrđeno.
- Pregled drugog para: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- Demonstrator: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- Usklađivanje s originalnim tutorovim šablonom: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
