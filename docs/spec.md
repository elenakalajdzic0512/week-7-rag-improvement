# M7 — prijedlog narednog eksperimenta: kontekstualni chunk embedding i provjera dokaza

**Status:** specifikacija za buduću implementaciju, 20. oktobar 2026. Ništa iz ovog dokumenta još nije implementirano ili izmjereno. Ovo je novi, višefazni eksperiment izvan završenog M1 zadatka. M1 ostaje sačuvan kao kontrola; stara specifikacija se ne zamjenjuje.

## 1. Problem, cilj i izvori

M1 je podigao prolaz sa 6/12 na 9/12. Cilj narednog rada je bolji izbor dokaza za parafraze, odsustvo zastarjelih pravila u odgovorima o važećoj politici i pravilno odbijanje kada dokaz ne postoji. E04/E09 moraju zadržati cijelu činjenicu „5 business days”; E09 treba pokriti i IT portal / Hardware. E05, E10 i E11 i dalje padaju. E06 prolazi iako odgovor sadrži suprotna pravila iz 2024. i 2026.

Dokazi i pregled literature su u [izvještaju](before-after-report.md#najveća-ograničenja-i-prijedlog-zasnovan-na-literaturi). Primarni metodološki izvori:

- [Late Chunking, Günther et al., arXiv v3, 2025](https://arxiv.org/html/2409.04701v3) i [repozitorijum autora](https://github.com/jina-ai/late-chunking): tokeni se prvo enkodiraju uz kontekst dokumenta, a zatim se vektori grupišu po chunkovima.
- [DPR, Karpukhin et al., EMNLP 2020](https://aclanthology.org/2020.emnlp-main.550/): motivacija za dense retrieval.
- [RRF, Cormack et al., SIGIR 2009](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf): spajanje rangova.
- [Passage Re-ranking with BERT, Nogueira i Cho, preprint 2019](https://arxiv.org/abs/1901.04085): zajedničko ocjenjivanje pitanja i pasaža.
- [Selective QA, Kamath et al., ACL 2020](https://aclanthology.org/2020.acl-main.503/): motivacija za odbijanje i odvojenu kalibraciju.
- [ALCE, Gao et al., EMNLP 2023](https://aclanthology.org/2023.emnlp-main.398/) i [RAGAs, Es et al., EACL 2024](https://aclanthology.org/2024.eacl-demo.16/): motivacija za razdvajanje retrievala, kvaliteta odgovora i citata.

Ugovori, veličine skupova, pragovi prihvatanja i raspored faza ispod su **naš projektni dizajn**, a ne tvrdnje ili reprodukcije rezultata tih radova. Nijedan rad ne garantuje poboljšanje ovog korpusa.

## 2. Granice izmjene i zaštita postojeće kontrole

- Sačuvati `src/chunking.py::split_text_by_sentences` i njegov M1 ugovor. `CHUNK_SIZE=140`, `CHUNK_OVERLAP=30` i tekst za citiranje ostaju isti u glavnim ablacijsko-kontrolnim poređenjima.
- Ne mijenjati `src/corpus.py`, `eval/eval_set.json`, `results/before.json`, `results/after.json` ni stare definicije metrika. Ne unositi posebne sinonime ili pravila vezana za E05/E11.
- Nova logika se uključuje kroz zasebne profile; postojeći M1 profil mora raditi bez instaliranih ML zavisnosti. Novi importi modela su odloženi do pokretanja odgovarajućeg profila.
- Nema generativnog LLM-a, prepisivanja izvornih rečenica, automatskog proširivanja upita, fine-tuninga, eksternog vector servisa ni obaveznog LLM sudije. Dodavanje istorijskog QA režima je odvojena buduća funkcija.
- Zavisnosti za eksperimente zapisati u novi `requirements-research.txt`, uz provjerene fiksne verzije za Python 3.12; postojeći `requirements.txt` ostaje netaknut.

Predloženi fajlovi: `src/research_profiles.py`, `src/contextual_embeddings.py`, `src/research_retrieval.py`, `src/evidence_selection.py`, `src/research_eval.py`, `scripts/calibrate_evidence.py`, `eval/research-dev.json`, `eval/research-holdout.json`, `eval/research-labels.json`, `experiments/model-lock.json` i odgovarajući novi testovi. Postojeći CLI/eval mogu dobiti opcioni `--profile` koji podrazumijevano bira M1; izlazna stara polja i ponašanje ostaju kompatibilni. Novi profil i putanja novog skupa su eksplicitni argumenti. Ne koristiti postojeći `eval_compare` kao da su različiti skupovi uporedivi.

## 3. Kontrolisane faze

Sve varijante koriste iste granice i sadržaj M1 chunkova. Glavni izlaz ostaje najviše dva citata. Faze predstavljaju eksperimente; nijedna se automatski ne proglašava novim podrazumijevanim režimom.

| Profil | Jedina novina u odnosu na prethodni profil | Šta se mjeri |
| --- | --- | --- |
| `m1` | Postojeće stanje, commit `5481a9e` / dokaz `b3a64ee` | Reprodukcija 9/12 i postojećih ograničenja. |
| `current` | Filter `status == current` prije skoringa | Učinak autoriteta izvora, posebno E06. |
| `hybrid-naive` | Postojeći leksički i novi nezavisni chunk embedding retrieval, spojeni RRF-om | Učinak semantičke grane, posebno parafraze. |
| `hybrid-late` | Isti model i retrieval kao prethodno, samo kontekstualno enkodiranje prije poolinga | Doprinos late chunkinga bez zamjene granica. |
| `reranked` | Cross-encoder prerangira kandidate | Doprinos izbora relevantnih citata. |
| `evidence-gated` | Kalibrisan prag uklanja nedovoljne citate; odbijanje ako nema preživjelih | Učinak odbijanja i kompromis kvalitet/pokrivenost. |

Prelazak na hybrid mijenja skalu retrieval skora. Od `hybrid-naive` do `reranked`, radi dijagnostike retrievala, odgovoriti kada postoji kandidat i ne primjenjivati stari prag 0.02 na RRF. To je eksplicitni dio hybrid profila, ne skrivena kalibracija; zabilježiti da promjena ponašanja u toj fazi uključuje i uklanjanje neuporedivog starog praga. Za čisto poređenje poolinga koristiti `hybrid-naive` naspram `hybrid-late`, sa potpuno istom odlukom o odgovaranju. Poređenje ukupnog efekta raditi i sa `m1`.

## 4. Ugovor izvora, granica i embeddinga

**Autoritet:** `current` i svi kasniji profili smiju kandidovati samo dokumente sa `status == "current"`. Ne brisati `superseded` dokumente iz korpusa. Novi CLI prima `--policy-mode current|historical`, podrazumijevano `current`; `historical` u ovim profilima uvijek vraća eksplicitno odbijanje da istorijske politike nisu podržane. UI ili pozivalac mora deklarisati režim. Automatsko prepoznavanje istorijske namjere iz slobodnog pitanja nije dio prve implementacije i ne smije se predstavljati kao riješeno. U evaluaciji koristiti označeni `policy_mode`; obim current-only režima mora biti vidljiv korisniku.

**Tekst i offseti:** normalizovati tekst sa `" ".join(text.split())`. Pratiti `[start, end)` svakog M1 chunka u tom istom tekstu kumulativnim dužinama, bez `str.find` koji može odabrati pogrešno ponovljenu rečenicu. Između chunkova je jedan separator. Važi `cleaned[start:end] == chunk.text` i `" ".join(chunk.text ...) == cleaned`. Ne dodavati metapodatke ili izmišljene rečenice u tekst za citiranje.

Late chunking ovdje poboljšava reprezentaciju istih chunkova, ne jezičko prepoznavanje granica. M1 ograničenje skraćenica ostaje poznato; promjena sentence parsera ili granica zahtijeva dodatni, zasebni eksperiment poslije glavnih poređenja.

**Model:** prvi kandidat je lokalni [`jinaai/jina-embeddings-v2-small-en`](https://huggingface.co/jinaai/jina-embeddings-v2-small-en). Njegova kartica opisuje mean pooling i do 8192 tokena. Prije prvog mjerljivog rada u `model-lock.json` upisati stvarni commit SHA modela i tokenizera, paketne verzije, uređaj, preciznost, limit i način poolinga; bez tih podataka eksperiment nije ponovljiv. Za kod preuzet uz model koristiti pregledanu, zaključanu reviziju. Nije dozvoljeno ostaviti `main` kao završnu reviziju. Ako kandidat nije kompatibilan, promjenu modela prvo dokumentovati i ponoviti obje embedding varijante istim zamjenskim modelom.

**Poređenje reprezentacija:** u `hybrid-naive` svaki chunk se enkodira zasebno; u `hybrid-late` svaki dokument se enkodira zasebno, a mean pooling se primjenjuje na tokene pripadajućeg chunka. Nikada ne enkodirati zajedno različite verzije ili dokumente. Upit dobija jedan vektor istim encoderom. Poslije poolinga primijeniti L2 normalizaciju i koristiti cosine/dot product za pretragu. Ne praviti jedan vektor dokumenta pa ga kopirati svim chunkovima. [Metoda i autorski kod](https://github.com/jina-ai/late-chunking).

Lokalni ugovor tokenizacije mora biti determinističan: zahtijevati pouzdane offsete u normalizovanom tekstu; iz poolinga isključiti padding i specijalne tokene bez tekstualnog offseta, jednako u obje varijante. Ovo je eksplicitna lokalna varijanta, ne identična reprodukcija tretmana specijalnih tokena u radu. Ako token prelazi granicu, dodijeliti ga chunku koji sadrži početni znak tokena; separator dodijeliti prethodnom chunku. Testirati tu odluku i evidentirati broj takvih slučajeva. Chunk bez tekstualnih tokena ili nulti vektor izaziva jasnu grešku. Primijeniti `eval()` i režim bez gradijenata.

Bez tihog truncationa: broj tokena dokumenta, upita i reranker para provjeriti prije inferencije. Ako prelazi stvarni limit, vratiti jasnu grešku za taj ulaz i zabilježiti je; obrada dugih dokumenata u macro prozorima je izvan prvog izdanja. Cijela rečenica od 163 znaka iz M1 mora ostati sačuvana. Tokeni i znakovi nisu ista jedinica.

Keš embeddinga smije biti lokalni; ključ obuhvata SHA-256 korpusa, model/tokenizer reviziju, profil poolinga, offsete i postavke. Promjena tih vrijednosti invalidira keš. Za 26 chunkova koristiti vektore u memoriji i iscrpnu pretragu, bez vector baze.

## 5. Kandidati, reranking i odbijanje

U oba retrieval kraka uzeti najviše `CANDIDATE_K=10` podobnih chunkova, bez punjenja liste nulama. Leksička grana zadržava postojeći `lexical_score` i minimum 0.01; dense grana rangira konačne cosine skorove bez tvrdnje da su oni vjerovatnoće. Spojiti po `chunk_id`:

```text
rrf(c) = sum(1 / (60 + rank_branch(c)))
```

Rangovi su od 1, odsutan kandidat daje doprinos 0; jednak skor razriješiti po `chunk_id`. [RRF izvor](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf). Zadržati prvih 10 jedinstvenih kandidata. Nema spajanja različitih izvora u jedan citat niti ponavljanja istog ID-ja. `hybrid-*` prikazuje prva dva; veći skup kandidata nije veći konačni `TOP_K`.

Za `reranked` koristiti lokalni [`cross-encoder/ms-marco-MiniLM-L6-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2), sa zaključanom revizijom u istom manifestu. Ocijeniti svih najviše 10 parova `(question, chunk.text)`, pa sortirati po sirovom logitu opadajuće, a zatim po `chunk_id`. Podrazumijevani sigmoid biblioteke ne smije neprimjetno promijeniti skalu; zabilježiti tačan izlaz. Sačuvati leksički skor, cosine, RRF rang i reranker logit kao različita dijagnostička polja. Logit nije dokaz tačnosti niti entailment skor.

`evidence-gated` odbacuje svaki kandidat sa logitom manjim od `tau`, pa uzima najviše dva preostala. Nema automatskog dodavanja drugog citata ispod praga. Ako nema nijednog, vratiti postojeću poruku odbijanja i praznu listu citata; retrieval dijagnostika se zadržava. Zadržati extractive format odgovora. Relevantan pasaž može dati samo dio odgovora na višedijelno pitanje; to se mora otkriti novom evaluacijom, a ne proglasiti riješenim samim thresholdom.

`tau` se određuje isključivo na novom razvojnom skupu. Ispitati pragove između uzastopnih zabilježenih logita, kao i slučajeve prihvatanja svih/odbijanja svih. Među pragovima bez pogrešno prihvaćenih nepodržanih razvojnih pitanja izabrati onaj sa najviše strogo tačnih odgovora na podržana pitanja; pri izjednačenju birati viši prag. Prikazati i pokrivenost i sve false refusal slučajeve. Ako prihvatanje podržanih pitanja nije zadovoljavajuće, faza nije uspješna; ne podešavati je gledanjem holdout rezultata. Čuvati izabrani prag, razvojni otisak i tabelu svih ispitanih pragova. To je jednostavna projektna adaptacija ideje selektivnog QA, bez tvrdnje o potpunoj reprodukciji rada Kamath et al.

## 6. Nova evaluacija uz očuvanje starih metrika

Starih 12 pitanja ostaju **poznati regresioni skup**, a ne novi neviđeni test. Sve stare metrike računati identično nad istim bajtovima `eval/eval_set.json` (SHA-256 `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`). Na njih ne podešavati modele, broj kandidata ni pragove. Stari `before.json` i `after.json` se ne regenerišu.

Prije prvih modelskih rezultata napraviti najmanje **30 razvojnih i 30 novih holdout pitanja**, svaki sa podržanim direktnim pitanjima (12), parafrazama (8) i nepodržanim pitanjima (10, od toga najmanje 5 bliskih temi). Ovaj obim je praktični početni dizajn, ne dovoljan dokaz statističke značajnosti. Dodati primjere višedijelnih zahtjeva, verzija, skraćenica, ponovljenih rečenica i referenci na prethodnu rečenicu. Testovi granica mogu biti posebni sintetički unit primjeri, bez proširivanja produkcijskog korpusa.

Grupisati parafraze iste osnovne tvrdnje/pitanja u isti split; ukloniti duplikate i porodice starih 12 pitanja iz novog holdouta. Novi holdout je neviđen po pitanju/porodici, ne po dokumentu: korpus je i dalje isti i mali. Čovjek pregleda tekst pitanja, očekivano ponašanje, potrebne činjenice i izvorne spanove prije zamrzavanja; AI prijedlog nije nezavisna ljudska provjera. Ako nema dovoljno različitih činjenica za ovaj split, prijaviti ograničenje i smanjiti plan prije mjerenja, bez popunjavanja trivijalnim parafrazama.

Nova oznaka sadrži: `id`, `question_family`, `split`, `expected_behaviour`, `policy_mode`, `required_facts`, i za svaku činjenicu jedan ili više prihvatljivih izvornih spanova (`doc_id`, verzija, status, offseti u normalizovanom tekstu i doslovni tekst). Posebno označiti poznate konfliktne spanove. ID-jevi chunkova nisu trajni gold podaci. Za E09 u odvojenim novim anotacijama zahtijevati i rok i mjesto zahtjeva; ne mijenjati njegov stari eval red.

Novi runner za svaki profil proizvodi stare metrike i **odvojeni** blok `research_metrics`:

| Metrika | Operativna definicija i nazivnik |
| --- | --- |
| Evidence recall@2 i @10 | Udio potrebnih činjenica podržanih bar jednim prihvatljivim spanom u top-k; prosjek po podržanom pitanju. Span mora biti potpuno sadržan u jednom vraćenom chunku. Ne poistovjećivati sa starim document hit-om. |
| MRR@10 | Recipročni rang prvog chunka koji sadrži bar jedan gold span, 0 ako ga nema; prosjek po podržanom pitanju. Ne mjeri potpunost višedijelnog odgovora. |
| Required-fact coverage | Udio traženih činjenica pokrivenih stvarno citiranim spanovima; prosjek po podržanom pitanju, odbijanje je 0. |
| Supporting-citation precision | Broj citata koji sadrže prihvatljiv span i nemaju označen konflikt podijeljen brojem citata; prosjek samo među odgovorima. Za dat odgovor bez citata vrijednost je 0. Zasebno prijaviti broj odgovora. |
| Stale-citation rate | Broj `superseded` citata / broj svih citata kod pitanja o važećem pravilu. Bez citata: null, uz eksplicitni nazivnik. |
| Known-conflict answer rate | Broj datih odgovora sa ručno označenim konfliktnim spanom / broj datih odgovora. To je poznati konfliktni skor, ne univerzalni NLI detektor. |
| Unsupported false-acceptance rate | Nepodržana pitanja na koja je odgovoreno / sva nepodržana pitanja. |
| Supported false-refusal rate | Podržana pitanja koja su odbijena / sva podržana pitanja. |
| Answer coverage i selective accuracy | Pokrivenost = broj odgovorenih / sva pitanja. Selektivna tačnost = strogo tačni dati odgovori / svi dati odgovori; bez odgovora: null. Odbijanje svega ne smije izgledati kao kvalitetan sistem. |
| Strict pass | Podržano: odgovor, svi required facts pokriveni, svaki citat relevantan, nema označenog konflikta ni zastarjelog citata. Nepodržano: odbijanje i bez citata. Agregat i puni redovi po pitanju. |

Automatske span provjere su konzervativne i ne mjere sve semantički ekvivalentne odgovore. Ako relevantan span koegzistira sa drugim nepotpunim ili dvosmislenim tvrdnjama koje anotacije ne pokrivaju, potreban je ručni pregled. Posebno za E06 i sva promijenjena pitanja provjeriti stvarni tekst odgovora. RAGAs/ALCE mogu inspirisati dodatni audit, ali te lokalne metrike ne nazivati njihovim zvaničnim skorovima. Prosta vjernost citiranom izvoru ne dokazuje da je izvor važeći.

## 7. Testovi i kriterijumi prihvatanja

Obavezno zadržati svih 30 postojećih testova. Novi deterministički testovi koriste male lažne encodere za: offsete i ponovljene rečenice; `.?!` i preduge rečenice; token na granici; padding/specijalne tokene; mean/L2 pooling sa ručno izračunatim vektorima; razliku nezavisnog i kontekstualnog toka; odvojenu obradu dokumenata; odbijanje predugih ulaza; filter verzija; RRF sa nedostajućim krakom i izjednačenjem; stabilni reranking; prag sa jednim/nijednim validnim citatom; pravilne nazivnike i E06/E09 kontraprimjere za nove metrike; invalidaciju keša i zabranu kalibracije na holdoutu. Odvojeni integracioni smoke test sa pravim modelom ne smije zamijeniti ručno provjerljive unit testove.

Uspjeh implementacije znači da ugovori rade i da su dokazi ponovljivi. Uspjeh istraživačke hipoteze zahtijeva i kvalitet; sljedeći kriterijumi su unaprijed zadati ciljevi, bez obećanja da će biti ispunjeni:

- `m1` reprodukuje 9/12 i originalne pojedinačne metrike; istorijski JSON fajlovi ostaju istih bajtova.
- `current` i kasniji profili imaju 0 zastarjelih citata za current-policy pitanja; E06 ne prikazuje pravilo od 2 dana. Sam pass E06 nije dovoljan.
- Konačni kandidat zadržava E04/E09 i ostalih šest ranijih prolaza; E09 ručno pokriva obje tražene činjenice. Prijaviti svaki izgubljeni prolaz.
- Na novom holdoutu konačni kandidat ima veći strict pass od M1 i manji false-acceptance rate bez povećanja false-refusal rate. Citation precision i evidence recall@2 ne smiju pasti u odnosu na M1. Prikazati brojnike/nazivnike i promjene po pitanju; ako ciljevi nisu ispunjeni, prijaviti neuspjeh i ne uključivati profil podrazumijevano.
- Late chunking se zadržava samo ako naspram `hybrid-naive` popravi evidence recall@2 ili MRR@10 na holdoutu bez pada strict pass-a, uz prikaz memorije i vremena. Ako su rezultati isti ili gori, preporučiti jednostavniji encoder tok, čak i ako ukupni pipeline nadmašuje M1 zbog drugih faza.
- Nema unaprijed obećanih 12/12. Holdout se koristi jednom za odluku; naredno podešavanje poslije uvida zahtijeva novi neviđeni skup. Malom uzorku ne pripisivati statističku značajnost.

## 8. Izvršavanje, artefakti i predaja

Budući CLI ugovor, **komande ispod još ne postoje u repozitorijumu**:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-research.txt
.venv/Scripts/python.exe -m pytest --basetemp=.tools/pytest-research
.venv/Scripts/python.exe -m src.research_eval --profile m1 --eval-set eval/eval_set.json --out results/m7-m1-original.json
.venv/Scripts/python.exe -m src.research_eval --profile hybrid-naive --eval-set eval/research-dev.json --out results/m7-naive-dev.json
.venv/Scripts/python.exe -m src.research_eval --profile hybrid-late --eval-set eval/research-dev.json --out results/m7-late-dev.json
.venv/Scripts/python.exe scripts/calibrate_evidence.py --eval-set eval/research-dev.json --profile reranked --out experiments/evidence-threshold.json
.venv/Scripts/python.exe -m src.research_eval --profile evidence-gated --eval-set eval/research-holdout.json --out results/m7-gated-holdout.json
```

Izvršiti sve profile nad istim novim holdoutom u jednom unaprijed zamrznutom batch-u, bez adaptivnog podešavanja između njih. Dodati i regresione izlaze svih profila nad starim evalom. Izlazna putanja mora biti nova; ako postoji, stati i sačuvati postojeći rezultat.

Sačuvati: kod/testove po fazama; `model-lock.json`; zaključane profile i prag sa dev rezultatima; potpune rezultate i rank liste svake varijante; SHA-256 sirovih bajtova oba nova skupa i originalnog evala; SHA-256 kanonski serijalizovanog korpusa (svi dokumenti, metapodaci, redoslijed i tekst, UTF-8 LF); Git commit; model/tokenizer revizije; Python/paketne verzije; uređaj i preciznost; chunkove/offsete; cache status; broj kandidata; sva četiri različita skora; izabrane citate i razlog odbijanja; vrijeme indeksiranja i peak RSS; medijanu i p95 latenciju poslije jednog warmup prolaza uz broj upita. Odvojiti download, cold indexing i warm query trošak.

Za poređenje novih metrika koristiti poseban izvještaj koji provjerava iste skupove, oznake i verziju sheme metrika; različiti skupovi se prikazuju odvojeno. JSON fajlovi u `results` su ignorisani: u Git dodavati samo eksplicitno pregledane izlaze, nikad sve ignorisane fajlove ni model težine. Windows LF/CRLF razliku prijaviti i sačuvati izvorne rezultate; ne mijenjati hash u JSON-u da bi poređenje prošlo.

Predloženi commitovi: `Add version-aware research evaluation and gold evidence labels`; `Add hybrid retrieval with independent chunk embeddings`; `Add late chunk pooling with span alignment`; `Add reranking and calibrated evidence selection`; `Document M7 ablations, limitations, and reproducibility`. Svaki commit sadrži relevantnu provjeru i opis promjene. Konačni izvještaj mora razlikovati izmjereni učinak svake faze od projektnih očekivanja.
