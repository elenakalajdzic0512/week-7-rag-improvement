# M5 — specifikacija filtriranja važećih izvora

**Status:** Specifikacija prije implementacije. Eksperiment se nadovezuje na završeni M1; M5 još nije implementiran.

**Početno stanje:** grana `feat/current-only-filter` polazi od commita `f48eeefd4d7df158b925a142a7d13d28b0b75cf9` na `main`. Obavezni M1 minimum je završen i dokumentovan, ali potvrda predaje tutoru nije dostavljena. Prema zadatku, implementacija naprednog dijela slijedi tek poslije predaje minimuma. Ovaj dokument je samo specifikacija.

## Problem i postojeći dokaz

Poslije M1 E06, „How many days per week can I work remotely?”, prolazi postojeću evaluaciju, ali odgovor istovremeno citira `hb-03-chunk-0` (2026, `current`, do **3 days per week**) i `hb-02-chunk-0` (2024, `superseded`, do **2 days per week**). Stara metrika prihvata važeću činjenicu u jednom citatu i `citation_precision=0.50`; ne otkriva kontradikciju u drugom citatu. Dokazi su u [rezultatu poslije M1](../results/after.json), [poređenju](../results/comparison.txt), [CLI transkriptu](after-cli-checks.txt) i [zajedničkom izvještaju](before-after-report.md). Važeće i zastarjelo pravilo potiču iz [korpusa](../src/corpus.py).

## Hipoteza i jedina intervencija

**Hipoteza:** filtriranje kandidata po statusu prije rangiranja može ukloniti zastarjeli dokaz iz E06 i sačuvati ispravan odgovor, bez gubitka prethodnih prolaza. To je očekivanje koje tek treba provjeriti.

U postojećoj `searchable_chunks` u `src/retrieval.py` implementirati već predviđenu opciju `CURRENT_ONLY`:

1. Kada je `CURRENT_ONLY=True`, vratiti samo chunkove za koje je `chunk.status == "current"`.
2. Kada je `CURRENT_ONLY=False`, očuvati postojeće ponašanje: svi ulazni chunkovi ostaju pretraživi.
3. Filtrirati **prije** računanja leksičkog skora i izbora `TOP_K`; ne mijenjati ulaznu listu, objekte chunkova, njihov međusobni redoslijed ili metapodatke.
4. Aktivirati `CURRENT_ONLY=True` u `src/config.py`. To je jedina promijenjena konfiguraciona vrijednost u odnosu na M1.

Postojeći `searchable_chunks` trenutno podiže `NotImplementedError` za `CURRENT_ONLY=True`, pa samo uključivanje postavke nije dovoljno. Implementacija filtera i aktiviranje postavke čine **jednu namjeru**: globalno isključivanje zastarjelih izvora iz pretrage. Ne dodavati profile, istorijski režim, automatsko prepoznavanje namjere pitanja, novi CLI ugovor ni nove zavisnosti.

**Dozvoljeni implementacijski fajlovi:** `src/retrieval.py`, `src/config.py` i ciljani testovi u `tests/`.

**Ne mijenjati:** M1 chunkovanje (`CHUNK_STRATEGY="sentences"`, `CHUNK_SIZE=140`, `CHUNK_OVERLAP=30`), korpus i statuse dokumenata, tokenizaciju, `lexical_score`, `TOP_K=2`, `RETRIEVAL_MIN_SCORE=0.01`, `REFUSAL_THRESHOLD=0.02`, `CITATION_MIN_SCORE=None`, formiranje odgovora, `eval/eval_set.json`, kod metrika i `requirements.txt`. Sačuvati `results/before.json`, `results/after.json`, `results/comparison.txt`, `docs/change-spec.md`, zajednički M1 izvještaj i Isidorin `docs/spec.md` neizmijenjene.

## Ciljani testovi

- Sa `CURRENT_ONLY=False` svi kandidati ostaju dostupni, u istom redoslijedu.
- Sa `CURRENT_ONLY=True` ostaju isključivo chunkovi čiji je status tačno `current`; testirati `superseded` i drugi status, bez pretpostavke da je svaki status osim `superseded` važeći.
- Prazan ulaz daje prazan izlaz.
- Kada postoje samo zastarjeli izvori, retrieval nema rezultat, a RAG koristi postojeću poruku odbijanja bez citata.
- Zastarjeli kandidat sa višim leksičkim skorom ne zauzima mjesto važećem kandidatu: filtriranje prethodi rangiranju i izboru top 2.
- Ulazna lista i chunkovi ostaju neizmijenjeni.
- Sačuvati svih 30 postojećih testova i pokrenuti ih zajedno sa novim ciljanim testovima kada implementacija bude dozvoljena.

## Mjerenje i dokazi poslije implementacije

**Kontrola je stanje poslije M1**, sačuvano u `results/after.json` (9/12 prolaza); ovo nije novo početno mjerenje i fajl se ne regeneriše. Novi rezultat ide u `results/current-only.json`, poređenje u `results/current-only-vs-m1.txt`, puni zapis CLI provjera u `docs/current-only-cli-checks.txt`, a puni zapis završnog pokretanja testova u `docs/current-only-test-results.txt`. Rezultati i zaključak se tek naknadno dokumentuju u `docs/current-only-report.md`. Nijedan od tih novih izlaznih fajlova ne smije postojati prije odgovarajućeg upisa; ako postoji, zaustaviti postupak i sačuvati ga bez prepisivanja.

Komande iz korijena projekta, **tek poslije predaje minimuma i implementacije**, uz aktivirano projektno Python 3.12 okruženje:

```bash
python -m pytest
python -m src.eval_runner --out results/current-only.json
python -m src.eval_compare results/after.json results/current-only.json
python -m src.cli --question "How many days per week can I work remotely?" --show-retrieved
```

Prije svakog upisa provjeriti da predviđena izlazna putanja ne postoji; izlaz poređenja, CLI transkript i izlaz testova sačuvati u gore navedenim novim putanjama. `eval_runner` ne štiti postojeći `--out` od prepisivanja. Uporediti `eval_set_sha256` sa M1 vrijednošću `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`. U konfiguracionom poređenju jedina razlika smije biti `CURRENT_ONLY: False -> True`; isti korpus i M1 chunkovi moraju ostati osnova oba rezultata. `results/*.json` je ignorisano u Gitu, pa eventualno dodavanje pregledanog novog rezultata mora biti izričito, bez dodavanja ostalih ignorisanih fajlova.

Ručno provjeriti stvarni tekst E06 odgovora, sve citate, njihove verzije i statuse, te odsustvo pravila od 2 dana. Pregledati i svako pitanje kojem se promijeni prolaz **ili izbor citata**, čak i ako zbirni skor ostane isti. Sačuvati tačne komande i izlaze. Ne mijenjati eval pitanja ni način računanja starih metrika; ručna provjera autoriteta izvora je zaseban dokaz.

## Kriterijumi zaključka

1. E06 daje važeće pravilo od **3 dana**, bez citata sa statusom `superseded` i bez zastarjele tvrdnje o **2 dana**. Sam postojeći `pass=true` nije dokaz da je kontradikcija uklonjena.
2. Nema regresija prolaz → pad u odnosu na M1 na istom skupu od 12 pitanja.
3. E04 i E09 zadržavaju traženu činjenicu **5 business days** u citatima; E09 ručno zadržava i mjesto zahtjeva **IT portal / Hardware**.
4. Prijaviti svaku promjenu citata i svako uočeno sadržinsko pogoršanje, čak i kada prolaz po metrici ostane isti.
5. Odvojeno ocijeniti uklanjanje kontradikcije E06 i očuvanje ostalih odgovora. Ako neki kriterijum nije ispunjen, rezultat označiti kao djelimičan ili negativan, bez dodavanja druge intervencije radi popravljanja skora.

## Ograničenja i odnos prema širem planu

Filter je **globalan** i ne zavisi od razumijevanja pitanja. Istorijska pitanja mogu dobiti pogrešan odgovor iz važećih izvora; istorijski QA nije podržan ovim eksperimentom. Ograničenje opsega mora biti jasno u dokumentaciji, bez nove CLI logike u ovoj intervenciji. Status `current` sam po sebi ne dokazuje relevantnost ili potpunost odgovora. M5 ne obećava rješavanje E05, E10 ili E11. Starih 12 pitanja su poznati regresioni skup, pa rezultat na njima ne dokazuje generalizaciju.

M5 izdvajamo kao usku prvu fazu iz [Isidorinog šireg budućeg plana](spec.md). Dense retrieval, late chunking, reranking, kalibrisana selekcija dokaza, novi profili i nove istraživačke metrike **nisu dio ove intervencije i nisu implementirani**. Učinak budućeg M5 treba pripisati zasebnom eksperimentu M1 → M5, a ne već završenom M1.
