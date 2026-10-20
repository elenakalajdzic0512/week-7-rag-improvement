# M1 — specifikacija promjene prije implementacije

**Status:** specifikacija prije implementacije. M1 još nije implementiran niti je pokrenut završni eval.

## Problem i dokaz

Početni eval (`results/before.json`) prolazi 6/12 pitanja. Za E04, „How many business days does a laptop replacement take?”, i E09, „Where do I request a replacement laptop and how long does it take?”, očekivana činjenica je **5 business days** iz važećeg dokumenta `hb-01` (*Equipment replacement*, 2026). Oba pitanja citiraju `hb-01-chunk-0` i `hb-01-chunk-2`, ali nijedan izabrani chunk ne sadrži tu frazu. Ona je cjelovita u `hb-01-chunk-1`, koji nije među prva dva rezultata. Zato oba imaju `retrieval_hit=true`, `citation_precision=1.0`, `fact_in_citations=false` i `pass=false`. Tačni tekstovi i CLI izlazi su u [početnim nalazima](baseline-findings.md) i [CLI provjerama](baseline-cli-checks.txt).

**Hipoteza:** čuvanje cijelih rečenica u chunkovima može omogućiti da chunk s potrebnom činjenicom bude pronađen i citiran. To ne garantuje ulazak u `TOP_K=2`, jer retrieval i dalje rangira po leksičkom skoru.

## Jedina intervencija

Implementirati postojeću `split_text_by_sentences` u `src/chunking.py` i aktivirati `CHUNK_STRATEGY="sentences"` u `src/config.py`. To je jedna namjera: zamjena strategije chunkovanja. `CHUNK_SIZE` ostaje **140**. `CHUNK_OVERLAP` ostaje **30** u konfiguraciji, ali se ne koristi u `sentences` grani; funkciji se prosljeđuje samo `CHUNK_SIZE`. Sva ostala podešavanja, korpus, retrieval, formiranje odgovora, eval skup i metrike ostaju neizmijenjeni. Ne dodavati NLP zavisnosti.

## Ugovor `split_text_by_sentences(text, chunk_size=140)`

1. Za `chunk_size <= 0` podići `ValueError`.
2. Normalizovati razmake kao postojeća strategija: `cleaned = " ".join(text.split())`. Prazan rezultat vraća `[]`.
3. Granica rečenice je **razmak nakon** `.`, `?` ili `!`. Znak interpunkcije ostaje u prethodnoj rečenici. Završni tekst bez završne interpunkcije takođe se zadržava.
4. Puna rečenica je nedjeljiva jedinica. Pakovati uzastopne rečenice pohlepno, u izvornom redoslijedu, s tačno jednim razmakom između njih. Dodati narednu rečenicu u tekući chunk samo ako ukupna dužina, uključujući taj razmak, ne prelazi `chunk_size`.
5. Spojeni chunk ima najviše `chunk_size` znakova. Ako je pojedinačna rečenica duža od limita, ostaje cijela kao zaseban chunk, iako prelazi limit; ne spajati je sa susjednom rečenicom.
6. Nema preklapanja, preskakanja ni dupliranja sadržaja. Spajanje izlaznih chunkova jednim razmakom mora dati normalizovani ulazni tekst.
7. `build_chunks` nastavlja da čuva redoslijed, metapodatke i format ID-jeva `{doc_id}-chunk-{i}`.

Ovo jednostavno pravilo nije jezički parser: skraćenice praćene razmakom mogu biti pogrešno razdvojene. To je poznato ograničenje, bez proširivanja obima promjene.

## Provjera i kriterijumi

- Koleginica dodaje ciljane testove za pohlepno pakovanje, rečenicu dužu od limita, očuvanje cijelog normalizovanog sadržaja, prazan tekst, nepozitivan limit i završni tekst bez interpunkcije. Postojeće testove ne brisati niti oslabljivati.
- Pokrenuti sve testove: `.venv/bin/python -m pytest`.
- Pokrenuti cio fiksni eval od 12 pitanja: `.venv/bin/python -m src.eval_runner --out results/after.json`. Primarno posmatrati `fact_in_citations` i `pass` za E04/E09, zatim sve promjene i regresije.
- Uporediti: `.venv/bin/python -m src.eval_compare results/before.json results/after.json`. Sačuvati izlaz poređenja.
- Ručno provjeriti promijenjeno pitanje, npr. `.venv/bin/python -m src.cli --question "How many business days does a laptop replacement take?" --show-retrieved`; uporediti stvarni odgovor, tekst citata, verziju i status izvora s očekivanom činjenicom. Ako to pitanje ostane nepromijenjeno, provjeriti pitanje koje se zaista promijenilo; ako takvog nema, tako zabilježiti.
- Prije poređenja potvrditi isti `eval_set_sha256`: `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`. Sačuvati `results/before.json` neizmijenjen.

Ne mijenjati druge postavke ako M1 ne pomogne. Neuspjela hipoteza je prihvatljiv rezultat. Promjena dužina chunkova mijenja leksičke skorove, rangiranje, citate i potencijalno odluke o odbijanju; zato je puni eval obavezan. M1 ne obećava rješavanje zastarjelih verzija (E06), parafraza (E05) ili nepodržanih pitanja (E10/E11).
