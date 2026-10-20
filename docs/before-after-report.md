# Week 7 — zajednički izvještaj prije/poslije

M1 je implementiran i provjeren 20. oktobra 2026. Svi testovi prolaze **30/30**, a fiksni eval je poboljšan sa **6/12 na 9/12**. E04 i E09 sada citiraju cijelu činjenicu o roku zamjene laptopa. Nema regresija prolaz → pad, ali E06 uprkos prolazu sadrži i zastarjelo pravilo. Elena je pregledala završne nalaze; komentar drugog para još nije dokumentovan, a demonstrator se dogovara.

## Cilj i početno stanje

Cilj weekly assignmenta je izmjeriti početni RAG sistem na fiksnom skupu, dokumentovati propuste, izvesti jednu kontrolisanu promjenu i uporediti stanje prije i poslije. Početni kod je sačuvan u commitu `c233b11f7a7faa8986236732de54be9453909d44`. Sistem radi lokalno nad deset dokumenata priručnika. Početna konfiguracija koristi chunkovanje po karakterima (`CHUNK_SIZE=140`, `CHUNK_OVERLAP=30`), `TOP_K=2` i ne filtrira zastarjele verzije. Potpuna podešavanja su u [početnim nalazima](baseline-findings.md) i izvornom [before rezultatu](../results/before.json).

Okruženje: lokalni `.venv` s Pythonom **3.12.14** i `pytest` **8.3.3**, sa zavisnostima iz neizmijenjenog `requirements.txt`. Komanda `.venv/bin/python -m pytest` prošla je **18/18** početnih testova, status 0. Početni eval pokrenut je komandom `.venv/bin/python -m src.eval_runner --out results/before.json`, status 0. Otisak eval skupa je `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

## Početni rezultati i propusti

| Metrika | Prije | Poslije | Promjena |
| --- | ---: | ---: | ---: |
| Prošla pitanja | 6/12 (50%) | 9/12 (75%) | +3 pitanja; +25 procentnih poena |
| Tačnost odluke odgovor/odbijanje (`behaviour_accuracy`) | 0.8333 | 0.8333 | 0.0000 |
| Pogodak očekivanog dokumenta kod podržanih pitanja (`retrieval_hit_rate`) | 0.7778 (7/9) | 0.8889 (8/9) | +0.1111 |
| Srednja preciznost citata među datim odgovorima | 0.4545 | 0.5455 | +0.0910 |

**E04** i **E09** traže rok zamjene laptopa. Oba citiraju očekivani `hb-01`, ali izabrani chunkovi ne sadrže „5 business days”; oba padaju uprkos `citation_precision=1.0`. **E06** citira pravilo iz 2024. sa „2 days per week”, iako važeći izvor iz 2026. kaže „3 days per week”. Tabela svih pitanja, citati i skorovi su u [početnim nalazima](baseline-findings.md) i [sačuvanim CLI provjerama](baseline-cli-checks.txt).

`citation_precision` računa udio citata iz očekivanog **dokumenta**, a ne potvrđuje da citirani chunk sadrži traženu činjenicu. `behaviour_accuracy` mjeri odluku odgovor/odbijanje, a ne sadržinsku tačnost. Isti fiksni skup koristimo za dijagnostiku i mjerenje, pa rezultat poslije promjene sam po sebi ne dokazuje generalizaciju na nova pitanja.

## Izabrana intervencija

Izabrana je jedna intervencija, **M1 — sentence-aware chunking**. [Specifikacija](change-spec.md) sadrži ugovor funkcije, hipotezu i način provjere. Početni dokazi motivišu M1, ali ne garantuju da će se potrebni chunk naći među prva dva rezultata.

## Implementacija

Implementacija i testovi su u commitu **`5481a9e` — `Implement M1 sentence-aware chunking`**. Pregled tačne izmjene: `git show 5481a9e -- src/chunking.py src/config.py tests/test_sentence_chunking.py`.

| Fajl | Izmjena / dodatak / uklanjanje |
| --- | --- |
| `src/chunking.py` | Dodat standardni modul `re`. U postojećoj funkciji `split_text_by_sentences` uklonjen je samo privremeni `NotImplementedError` i zamijenjen validacijom limita, normalizacijom razmaka i pohlepnim pakovanjem cijelih rečenica. |
| `src/config.py` | Jedina promijenjena postavka je `CHUNK_STRATEGY`: `chars` → `sentences`. |
| `tests/test_sentence_chunking.py` | Dodat novi fajl sa 12 test slučajeva: pohlepno pakovanje i granična dužina sa separatorom; preduga rečenica kao zaseban chunk; prazan/bijeli tekst; nulti i negativni limit, uključujući prazan ulaz; normalizacija i očuvanje sadržaja; `.`, `?`, `!` i završni tekst bez interpunkcije; odsustvo granice bez razmaka; nezavisnost od overlap postavke; redoslijed, ID-jevi i metapodaci kroz `build_chunks`. |
| `docs/before-after-report.md` | Dopunjene implementacija, okruženje, mjerenje, svih 12 pitanja, ručne provjere, regresije, ograničenja, zaključak, doprinos i status pregleda. Dodati popis fajlova i dokazi ponovljivosti. |
| `results/after.json` | Dodat izvorni završni rezultat eval runnera, bez ručnog uređivanja, sa konfiguracijom, otiskom i svim pitanjima. |
| `results/comparison.txt` | Dodat kompletan izlaz uspješnog poređenja prije/poslije. |
| `docs/after-cli-checks.txt` | Dodati puni CLI transkripti za E04, E09, E06 i sva tri preostala pada: E05, E10 i E11; uključuju komande, odgovore, citate, skorove, verzije i statuse izvora. |
| `docs/after-test-results.txt` | Dodat puni izlaz završnog pokretanja svih 30 testova. |

Granica rečenice je razmak nakon `.`, `?` ili `!`, uz zadržavanje interpunkcije. Uzastopne rečenice se spajaju jednim razmakom dok ukupna dužina ne pređe 140 znakova. Preduga rečenica ostaje cjelovita i samostalna. Nema overlapa, preskakanja ni dupliranja. `build_chunks` i postojeća `chars` strategija nisu mijenjani. Broj chunkova nad korpusom promijenjen je sa **23 na 26**; `hb-01-chunk-1` ima **163 znaka**, što je dozvoljeno ugovorom za pojedinačnu predugu rečenicu. Provjereno je očuvanje cijelog normalizovanog sadržaja svih deset dokumenata.

Nijedan postojeći test ni fajl nije uklonjen. Korpus, retrieval, formiranje odgovora, metrike, zavisnosti i ostala podešavanja nisu mijenjani. `CHUNK_SIZE=140` i `CHUNK_OVERLAP=30` ostaju zapisani; overlap se ne koristi u `sentences` grani. Specifikacija, handoff i početni nalazi ostavljeni su kao zapisi stanja prije implementacije.

Završna provjera je rađena na Windowsu uz **Python 3.12.14** i **pytest 8.3.3**. Pošto su početno bili dostupni samo Python 3.13.3 i nijedan lokalni `.venv`, lokalno je pripremljen `uv 0.13.3` u ignorisanom `.tools`, preuzet Python 3.12.14 u privremeni direktorijum i napravljen `.venv`. `requirements.txt` i globalni paketi nisu mijenjani. Komande pripreme iz PowerShella:

```powershell
python -m pip install --target .tools uv
$env:UV_PYTHON_INSTALL_DIR = Join-Path $env:TEMP 'week7-python'
$env:UV_CACHE_DIR = Join-Path $env:TEMP 'week7-uv-cache'
.\.tools\bin\uv.exe python install 3.12.14
.\.tools\bin\uv.exe venv --python 3.12.14 .venv
.\.tools\bin\uv.exe pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -m pytest --basetemp=.tools/pytest-final
```

Prvo pokretanje bez `--basetemp` imalo je 29 prolaza i jednu grešku pri pripremi postojećeg testa zbog nedozvoljenog pristupa sistemskom pytest privremenom direktorijumu. Izbor lokalnog privremenog direktorijuma riješio je okruženje bez izmjene testova: **30/30 prolazi, status 0**. Od toga je 18 postojećih i 12 novih test slučajeva. Puni uspješni izlaz je u [zapisu testova](after-test-results.txt).

## Završno mjerenje i poređenje

Prije prvog evala potvrđeno je da `results/after.json` ne postoji. Prvi rezultat otkrio je razliku u bajtovima eval skupa: Windows checkout koristio je CRLF (`3c2a2b3a09169f42b31cd9dbe0403250561a72e745642baa598300ab47a6a883`), a početni rezultat i Git blob koriste LF. `src.eval_compare` je ispravno odbio takvo poređenje. Taj rezultat je sačuvan bez prepisivanja kao lokalni, ignorisani `results/after-crlf-checkout.json`; nije korišćen za završno poređenje niti dodat u commit.

Fajl `eval/eval_set.json` je zatim vraćen na **tačne bajtove postojećeg Git bloba**, bez promjene pitanja, sadržaja ili logike metrika. `git diff -- eval/eval_set.json` nema sadržinske izmjene. Novi `after.json` je generisan runnerom. Oba važeća rezultata sada imaju identičan otisak:

`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

Predati `results/before.json` (Git fajl sa LF završecima redova) ima SHA-256 `41138967ae31b2c1d22fbdccd7bff326c8563620bfd8aaa61be12092459d29d0`. Lokalna Windows kopija istog JSON sadržaja sa CRLF završecima redova imala je SHA-256 `c5eb4fc3cb96586c2de9ca812e6b8d3270972b1d38d04f01698b712ddf341c2a`. Razlika u završecima redova mijenja bajtovski otisak, dok je sadržaj početnog rezultata očuvan; predati fajl nije prepisivan ni ručno uređivan.

Komande iz korijena projekta, obje sa statusom 0:

```powershell
.venv/Scripts/python.exe -m src.eval_runner --out results/after.json
.venv/Scripts/python.exe -m src.eval_compare results/before.json results/after.json
```

Puni stdout poređenja sačuvan je u [results/comparison.txt](../results/comparison.txt). [Završni JSON](../results/after.json) ima `created_at=2026-10-20T14:10:05+00:00` (16:10:05 po lokalnom vremenu Europe/Budapest). Zabilježena konfiguracija:

```text
CHUNK_STRATEGY=sentences
CHUNK_SIZE=140
CHUNK_OVERLAP=30
TOP_K=2
RETRIEVAL_MIN_SCORE=0.01
STOPWORDS_ENABLED=False
CURRENT_ONLY=False
REFUSAL_THRESHOLD=0.02
CITATION_MIN_SCORE=None
```

Tabela svih pitanja: `Hit`, `Fact` i `CitPrec` prikazuju prije → poslije. `—` znači da metrika nije primjenjiva. Očekivano i stvarno ponašanje odnose se na odluku odgovor/odbijanje.

| ID | Pitanje | Očekivano | Stvarno prije → poslije | Hit | Fact | CitPrec | Prolaz prije → poslije |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | How many days of annual leave do employees get? | odgovor | odgovor → odgovor | da → da | da → da | 0.50 → 0.50 | da → da |
| E02 | How often do passwords need to be changed? | odgovor | odgovor → odgovor | da → da | da → da | 0.50 → 0.50 | da → da |
| E03 | What is the yearly training budget per employee? | odgovor | odgovor → odgovor | da → da | da → da | 0.50 → 1.00 | da → da |
| E04 | How many business days does a laptop replacement take? | odgovor | odgovor → odgovor | da → da | ne → da | 1.00 → 1.00 | ne → da |
| E05 | How long until I get a new notebook computer? | odgovor | odgovor → odgovor | ne → ne | ne → ne | 0.00 → 0.00 | ne → ne |
| E06 | How many days per week can I work remotely? | odgovor | odgovor → odgovor | ne → da | ne → da | 0.00 → 0.50 | ne → da |
| E07 | What are the IT support hours? | odgovor | odgovor → odgovor | da → da | da → da | 1.00 → 1.00 | da → da |
| E08 | By when must travel receipts be submitted? | odgovor | odgovor → odgovor | da → da | da → da | 0.50 → 0.50 | da → da |
| E09 | Where do I request a replacement laptop and how long does it take? | odgovor | odgovor → odgovor | da → da | ne → da | 1.00 → 1.00 | ne → da |
| E10 | What is the current company stock price? | odbijanje | odgovor → odgovor | — | — | 0.00 → 0.00 | ne → ne |
| E11 | What is the parental leave policy? | odbijanje | odgovor → odgovor | — | — | 0.00 → 0.00 | ne → ne |
| E12 | Who won the 1958 football world cup? | odbijanje | odbijanje → odbijanje | — | — | — | da → da |

Kompletan izlaz poređenja:

```text
Fixed (fail -> pass): E04, E06, E09
Regressed (pass -> fail): none
Unchanged: E01, E02, E03, E05, E07, E08, E10, E11, E12

Summary:
  passed: 6 -> 9 (+3)
  total: 12 -> 12 (+0)
  behaviour_accuracy: 0.8333 -> 0.8333 (+0.0)
  retrieval_hit_rate: 0.7778 -> 0.8889 (+0.1111)
  mean_citation_precision: 0.4545 -> 0.5455 (+0.091)

Changed settings:
  CHUNK_STRATEGY: 'chars' -> 'sentences'
```

`Unchanged` ovdje znači nepromijenjen status prolaza; tekst chunkova, skorovi i citati mogu biti drugačiji. E03 ima dodatno poboljšanje preciznosti citata iako je prolazio i prije. E01 mijenja sporedni citat iz `hb-02` u `hb-03`, E08 iz `hb-03` u `hb-05`, a E10 mijenja redoslijed dva nepovezana izvora. Isti ID chunka između strategija ne garantuje isti sadržaj.

## Ručna provjera

Puni odgovori i citati za šest pitanja sačuvani su u [docs/after-cli-checks.txt](after-cli-checks.txt). Sve CLI komande završile su statusom 0. Sistem i dalje prikazuje doslovni tekst citiranih chunkova uz prefiks, bez generisanja sažetog odgovora.

**E04 — potvrđena ciljna promjena:**

```powershell
.venv/Scripts/python.exe -m src.cli --question "How many business days does a laptop replacement take?" --show-retrieved
```

Odgovor sadrži `[hb-01-chunk-1] After manager approval, a replacement laptop is set up by IT staff with your files, accounts, email and access rights, and handover can take up to 5 business days.` Drugi citat je `hb-01-chunk-0`, o mogućnosti zamjene izgubljenog, ukradenog ili pokvarenog laptopa. Oba izvora su *Equipment replacement*, verzija **2026**, status **current**. Skorovi su 0.2069 i 0.2000. I odgovor i citirani chunk sada sadrže **5 business days**; `Fact` i `Pass` prelaze iz `false` u `true`.

**E09 — potvrđen potpuniji odgovor:**

```powershell
.venv/Scripts/python.exe -m src.cli --question "Where do I request a replacement laptop and how long does it take?" --show-retrieved
```

Odgovor prvo citira `hb-01-chunk-2`: `Report lost or stolen devices to security first. Request a replacement laptop in IT portal under Hardware.` Zatim citira cijelu rečenicu iz `hb-01-chunk-1` sa **5 business days**. Oba su verzija **2026**, **current**; skorovi su 0.2941 i 0.2414. Sada su pokriveni i mjesto podnošenja zahtjeva i rok.

**E06 — metrika prolazi, odgovor ostaje kontradiktoran:**

```powershell
.venv/Scripts/python.exe -m src.cli --question "How many days per week can I work remotely?" --show-retrieved
```

Prvi citat je `hb-03-chunk-0`, verzija **2026**, **current**, skor 0.5833: `Remote work: employees can work remotely up to 3 days per week.` Drugi je `hb-02-chunk-0`, verzija **2024**, **superseded**, skor 0.4545: `Remote work: employees can work remotely up to 2 days per week. Remote days per week are agreed with your team lead.` Prisustvo važeće činjenice i `CitPrec=0.50` dovoljno je za prolaz, ali korisnik dobija oba suprotna pravila. Ovo nije potpuno riješen problem verzionisanja.

## Regresije i preostala ograničenja

**Regresije:** nema pitanja koje je prešlo iz prolaza u pad; nijedna od pojedinačnih evaluiranih metrika po pitanju nije pogoršana. Nema pada zbirnih metrika. To ne znači da je svaki prikazani odgovor sadržinski ispravan.

- **E06:** ručno je potvrđeno istovremeno citiranje važećeg pravila od 3 dana i zastarjelog od 2 dana. Ovo ostaje stvarna kontradikcija iako eval sada označava prolaz. `CURRENT_ONLY=False` je ostao neizmijenjen.
- **E05 i dalje pada:** za „notebook computer” odgovor citira onboarding i godišnji odmor, bez roka zamjene računara. `Hit=false`, `Fact=false`, `CitPrec=0.00`. M1 nije riješio sinonime.
- **E10 i E11 i dalje padaju:** umjesto odbijanja daju sadržaj o MFA/parkingu, odnosno godišnjem odmoru. Najbolji skorovi su 0.0769 i 0.2222, iznad neizmijenjenog praga 0.02. Za E10 nije izmišljena cijena akcije; vraćen je nepovezan sadržaj. Za E11 nisu date informacije o roditeljskom odsustvu.
- **Šum u citatima:** E01, E02 i E08 zadržavaju `CitPrec=0.50`; svaki ima jedan citat iz drugog dokumenta. E03 je poboljšan na 1.00.
- **Granice rečenica:** pravilo nije jezički parser i može razdvojiti skraćenice iza kojih slijedi razmak. Pojedinačna rečenica može biti duža od limita, što je namjerno ponašanje ugovora, a ne greška.
- **Ograničenje mjerenja:** samo 12 fiksnih pitanja korišćeno je i za dijagnostiku i za mjerenje. `Fact` traži doslovnu normalizovanu frazu u jednom citatu, a `Pass` može tolerisati nevažan ili kontradiktoran drugi citat. Rezultat 9/12 ne dokazuje generalizaciju niti pouzdanost svih odgovora.
- **Ponovljivost na Windowsu:** raw-byte otisak eval skupa zavisi od završetaka redova; za poređenje moraju biti korišćeni izvorni LF bajtovi, što je ovdje provjereno.

Nisu podešavane druge opcije da bi se uklonili preostali propusti; sačuvan je obim jedne intervencije.

## Zaključak

Hipoteza M1 potvrđena je za ciljana pitanja E04 i E09 na ovom fiksnom skupu: cijela rečenica sa „5 business days” sada ulazi u top 2 i odgovor je citira. Prolaznost raste sa **50% na 75%**, pogodak očekivanog dokumenta sa **7/9 na 8/9**, a srednja preciznost citata sa **0.4545 na 0.5455**. Tačnost odluke odgovor/odbijanje ostaje **10/12**. Nema zabilježenih regresija prolaza.

Treći dodatni prolaz, E06, treba tumačiti oprezno: promjena rangiranja donijela je važeći izvor, ali nije uklonila kontradiktoran zastarjeli izvor. M1 je poboljšao dostupnost cjelovitih činjenica, dok sinonimi, odbijanje nepodržanih pitanja i dosljedno korišćenje važećih verzija ostaju ograničenja potvrđena završnim dokazima.

Dokazi su sačuvani u izvornom `after.json`, kompletnom poređenju, CLI transkriptima i zapisu testova; kod i testovi imaju zaseban commit `5481a9e`. Za uključivanje ignorisanog rezultata u dokumentacijski commit koristi se isključivo `git add -f -- results/after.json`, bez dodavanja ostalih ignorisanih fajlova. Završni rad je objavljen na udaljenom `main`; pregledani vrh je `c229233`.

## Najveća ograničenja i prijedlog zasnovan na literaturi

Ovaj odjeljak dodat je 20. oktobra 2026. na Isidorin zahtjev, poslije završenog M1 mjerenja. **Prijedlog nije implementiran niti evaluiran.** Jedini izmjereni rezultati ostaju 6/12 prije M1 i 9/12 poslije M1. Novi ugovor za budući rad je u [docs/spec.md](spec.md); postojeća [M1 specifikacija](change-spec.md) ostaje neizmijenjena.

### Prioriteti prema dokazima iz ovog projekta

| Prioritet / problem | Dokaz prije → poslije M1 | Posljedica i predloženi odgovor |
| --- | --- | --- |
| 1. Važeći izvor i kontradikcija | E06: prije samo 2024/2 dana; poslije i 2026/3 dana i 2024/2 dana. Eval sada daje prolaz. | Za pitanja o važećim pravilima filtrirati `status=current` prije rangiranja i posebno mjeriti zastarjele citate i kontradikcije. Ovo je projektna odluka o autoritetu izvora; embedding model sam ne određuje koje pravilo važi. |
| 2. Nepodržana pitanja i slabi dokazi | E10/E11 padaju u oba mjerenja; tačnost odluke ostaje 10/12. Poslije M1 najbolji skorovi su 0.0769 i 0.2222. | Uvesti selekciju citata i kalibrisano odbijanje; terminološka sličnost nije dokaz da tekst odgovara na pitanje. Posebno provjeriti negativne primjere bliske temi, npr. roditeljsko naspram godišnjeg odsustva. |
| 3. Leksičko poklapanje bez semantike | E05 i dalje ne pronalazi `hb-01` za „notebook computer”. | Dodati semantički retrieval i provjeriti parafraze koje nisu korišćene za podešavanje. Ne unositi ručno pravilo za jedan poznati eval upit. |
| 4. Gubitak konteksta i osjetljivost na veličinu | M1 popravlja E04/E09; postoji dozvoljeni chunk od 163 znaka. Skor u `lexical_score` je broj poklopljenih tokena podijeljen dužinom chunka, pa promjena dužine mijenja rang i prag prihvatanja. | Zadržati cijele rečenice i probati kontekstualne chunk embeddinge. Ne tvrditi da M1 ima dokazan problem sa zamjenicama: to je rizik koji treba posebno testirati. |
| 5. Svi pronađeni rezultati postaju citati | E01/E02/E08 ostaju na `CitPrec=0.50`; E06 prikazuje i kontradiktoran rezultat. | Razdvojiti veći skup kandidata od najviše dva konačna, provjerena citata. Samo povećavanje `TOP_K` može povećati šum. |
| 6. Nedovoljno stroga evaluacija | Samo 12 poznatih pitanja; E06 prolazi uz kontradikciju; E09 provjerava rok, ali ne zahtijeva i mjesto podnošenja zahtjeva. | Sačuvati stare metrike radi poređenja i dodati odvojene provjere svih traženih činjenica, autoriteta izvora, odbijanja i potpunosti citata na novim pitanjima. |

`lexical_score` nije BM25: ne koristi IDF, već ponovljena poklapanja u tekstu dijeli brojem tokena chunka. Zbog toga jedan zajednički čest izraz može dati dovoljno visok skor. Kraći chunkovi nisu automatski bolji. Postojeći sistem prikazuje izvučeni tekst, bez generativnog LLM-a; glavna greška je pogrešan izbor i prihvatanje dokaza, a ne izmišljanje novih činjenica.

### Šta literatura podržava, a šta je naš prijedlog

| Rad / primarni izvor | Nalaz ili metoda relevantna za ovaj rad | Primjena i ograničenje |
| --- | --- | --- |
| Günther et al., *Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models*, arXiv:2409.04701, v3 (2025; prvi preprint 2024). [Rad](https://arxiv.org/html/2409.04701v3), [kod autora](https://github.com/jina-ai/late-chunking). | Kontekstualizuje tokene dokumenta prije poolinga po granicama chunkova. | Glavni eksperiment za očuvanje konteksta uz kratke citate. Zadržati M1 granice i porediti nezavisno i kontekstualno enkodiranje istim modelom. Nije samo promjena regexa i zahtijeva embedding model. |
| Karpukhin et al., *Dense Passage Retrieval for Open-Domain Question Answering*, EMNLP 2020. [Rad](https://aclanthology.org/2020.emnlp-main.550/). | Pokazuje retrieval zasnovan na gustim reprezentacijama pitanja i pasaža. | Motivacija za semantičku granu koja može pomoći E05. Ne treniramo DPR na 12 pitanja niti prenosimo procente iz njihovih eksperimenata na ovaj korpus. |
| Cormack, Clarke i Büttcher, *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods*, SIGIR 2009. [Rad autora](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf). | Spaja liste prema recipročnim rangovima, bez poređenja različitih skala skorova. | Spojiti postojeći leksički retrieval i novu dense granu. RRF je samo rangiranje; njegov pozitivan skor nije dokaz odgovorivosti. |
| Nogueira i Cho, *Passage Re-ranking with BERT*, arXiv:1901.04085 (2019, preprint). [Rad](https://arxiv.org/abs/1901.04085). | Model zajednički obrađuje pitanje i pasaž radi ponovnog rangiranja. | Ispitati cross-encoder za uklanjanje tematski sličnih, ali nerelevantnih citata. Relevance skor nije logička provjera tvrdnje. |
| Kamath, Jia i Liang, *Selective Question Answering under Domain Shift*, ACL 2020. [Rad](https://aclanthology.org/2020.acl-main.503/). | Istražuje odluku o odbijanju i kalibraciju uz pitanja izvan domena. | Prag selekcije podesiti na posebnom razvojnom skupu sa podržanim i nepodržanim pitanjima. Naš jednostavni prag nad rerankerom je prilagođavanje ideje, ne reprodukcija njihovog treniranog kalibratora. |
| Gao et al., *Enabling Large Language Models to Generate Text with Citations* (ALCE), EMNLP 2023. [Rad](https://aclanthology.org/2023.emnlp-main.398/). | Razdvaja tačnost odgovora i kvalitet citiranja. | Dodati procjenu pokrivenosti činjenica i relevantnosti citata. Predložene lokalne provjere nisu zvanični ALCE skorovi. |
| Es et al., *RAGAs: Automated Evaluation of Retrieval Augmented Generation*, EACL 2024, demonstracijski rad. [Rad](https://aclanthology.org/2024.eacl-demo.16/). | Evaluira različite komponente kvaliteta RAG-a. | Odvojeno izvještavati retrieval, podržanost odgovora i relevantnost. Pošto naš sistem kopira tekst, sama vjernost izvoru može biti visoka i kada je izvor zastario ili ne odgovara pitanju. RAGAs nije zamjena za ljudsku provjeru autoriteta. |

Preporuka je **fazni eksperiment: provjera važećeg izvora → leksički i semantički kandidati → late chunking → reranking → kalibrisana selekcija citata i odbijanje**. To je naša sinteza navedenih metoda. Svaka faza ima zasebno mjerenje u [novoj specifikaciji](spec.md), da se poboljšanje od boljeg chunk embeddinga ne pomiješa sa učinkom filtera ili novog praga.

Za prvi embedding eksperiment predložen je lokalni `jinaai/jina-embeddings-v2-small-en`, čija [kartica autora](https://huggingface.co/jinaai/jina-embeddings-v2-small-en) opisuje engleski model sa mean poolingom i kontekstom do 8192 tokena. Za reranking je kandidat `cross-encoder/ms-marco-MiniLM-L6-v2`, prema [kartici izdavača](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2). Njihove tačne revizije i verzije biblioteka moraju se zaključati pri implementaciji; sada nisu preuzeti niti pokrenuti. Za 26 chunkova nije potrebna vektorska baza: dovoljna je iscrpna pretraga u memoriji.

Očekivani pravac koristi je bolji recall za parafraze, manje nevažnih citata i bolje odbijanje nepodržanih pitanja. **To su hipoteze, bez novih izmjerenih skorova.** Late chunking može dodati malo koristi na ovako kratkim dokumentima; zato je obični dense retrieval obavezan kontrolni eksperiment. Ne rješava sam zastarjele politike, a dodatni modeli povećavaju vrijeme i memoriju. Ako skuplja varijanta ne poboljša kvalitet, prednost ima jednostavnija varijanta.

U ovoj dopuni izmijenjen je samo ovaj izvještaj i dodat `docs/spec.md`. Izvršni kod, zavisnosti, početni i završni rezultati i originalni eval skup nisu mijenjani. Literatura je provjerena putem primarnih izvora; prijedlog i specifikaciju pripremio je Codex na Isidorin zahtjev. Ne predstavlja dodatni ljudski ili partnerski pregled.

## Pregled drugog para

Prema izjavi Isidore Popović, završna evaluacija poslata je Eleni na pregled. Elena je obavila interni pregled Isidorinog rada uz pomoć AI asistenata; to nije obavezni pregled drugog para. Komentar drugog para i odgovor na njega još nisu dokumentovani.

**Status pregleda drugog para:** čeka stvarni komentar. Ime para, komentar i postupanje po njemu treba dopisati kada budu dostupni.

## Doprinos članica i korišćenje AI-ja

**Elena:** evaluirala je početni kod bez izmjene njegove implementacije, analizirala propuste, odabrala M1 i pripremila specifikaciju promjene. Početna dokumentacija bilježi korišćenje AI asistenata u toj fazi.

**Isidora Popović:** prema svojoj izjavi pročitala je specifikaciju i proslijedila je Codexu za implementaciju; nakon toga ponovila je evaluaciju sistema i poslala rezultate Eleni na pregled.

**Elenin završni pregled:** Nakon Isidorine implementacije pregledala sam njene izmjene, rezultate testova i evaluacije, sačuvane CLI provjere i dopunjenu dokumentaciju. Zaključila sam da implementacija odgovara prethodno napisanoj specifikaciji i da je zadržan obim jedne promjene — M1 chunkovanja po rečenicama. Rezultati pokazuju napredak sa 6/12 na 9/12 prolaza, bez regresija prolaz → pad, uz svih 30 prolaznih testova. Za ciljana pitanja E04 i E09 citati sada sadrže traženu činjenicu, što podržava početnu hipotezu. Izdvojila sam i ograničenje E06: iako pitanje prolazi evaluaciju, odgovor citira i važeće i zastarjelo pravilo, pa prolaz metrike ne znači potpuno ispravan odgovor. Na osnovu pregleda usmjerila sam završne ispravke dokumentacije.

Pri pregledu koristila sam ChatGPT i Codex kao pomoć u analizi i tehničkoj provjeri. Codex je izvršio ponovno pokretanje testova i evaluacije, a ja sam pregledala nalaze i na osnovu njih procijenila rezultat. Naknadna tehnička revizija zabilježena je u razgovoru; zaseban zapis te revizije nije sačuvan u repozitorijumu.

**Korišćenje AI-ja u ovoj fazi:** Codex je na Isidorin zahtjev implementirao funkciju i promjenu strategije, dodao ciljane testove, pripremio lokalno okruženje, izvršio testove, eval i CLI provjere, provjerio otiske, sačuvao dokaze, dopunio ovaj izvještaj i napravio Git commit implementacije. Kod i rezultati nisu predstavljeni kao ručno napisani ili nezavisno pregledani od strane druge osobe. Završna dokumentacija i dokazi čuvaju se u zasebnom commitu sa opisom rezultata.

**Demonstrator:** Dogovara se.
