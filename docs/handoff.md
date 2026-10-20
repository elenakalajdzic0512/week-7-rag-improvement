# Predaja koleginici — M1

**Trenutno stanje:** početni kod i dokazi su pripremljeni; M1 nije implementiran i `results/after.json` ne postoji. Prije rada pročitati [specifikaciju](change-spec.md), [početne nalaze](baseline-findings.md), [CLI provjere](baseline-cli-checks.txt) i neizmijenjeni [before rezultat](../results/before.json).

## Okruženje

Raditi iz korijena projekta s Pythonom 3.12. Ako lokalni `.venv` nije dostupan, pripremiti ga ovako (bez promjene `requirements.txt` ili globalnih paketa):

```bash
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python --version
.venv/bin/python -m pytest --version
```

Za početni rad ovdje su korišćeni Python 3.12.14 i pytest 8.3.3. Početni testovi su bili 18/18, a eval 6/12; `eval_set_sha256` je `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

## Dozvoljeni obim implementacije

Implementirati samo `split_text_by_sentences` u `src/chunking.py` prema [ugovoru](change-spec.md) i postaviti `CHUNK_STRATEGY="sentences"` u `src/config.py`. Dodati ciljane testove u `tests/` bez brisanja ili slabljenja postojećih. `CHUNK_SIZE=140` i `CHUNK_OVERLAP=30` ostaju zapisani; overlap se ne koristi u sentences grani. Ne mijenjati korpus, `eval/eval_set.json`, retrieval, odgovaranje, metrike, druge postavke ili zavisnosti. Ne prepisivati niti ručno uređivati `results/before.json`.

## Provjera i zapis rezultata

Iz korijena projekta:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m src.eval_runner --out results/after.json
.venv/bin/python -m src.eval_compare results/before.json results/after.json
```

Prije evala provjeriti da `results/after.json` ne postoji ili prethodni rezultat sačuvati bez prepisivanja. Potvrditi jednak otisak eval skupa u oba rezultata. Sačuvati puni izlaz poređenja, npr. uz `set -o pipefail` i `.venv/bin/python -m src.eval_compare results/before.json results/after.json | tee results/comparison.txt`; ne oslanjati se samo na prepisane brojke. Zabilježiti sve regresije i najmanje jedno preostalo ograničenje, na osnovu stvarnog after rezultata.

Za pitanje koje se promijenilo pokrenuti CLI s `--show-retrieved` i zabilježiti tačnu komandu, izlaz, tekst odgovora, citirani chunk, verziju i status izvora. Za ciljano E04 primjer komande je:

```bash
.venv/bin/python -m src.cli --question "How many business days does a laptop replacement take?" --show-retrieved
```

Provjeriti podržava li citat zaista „5 business days”. Ako se E04 ne promijeni, izabrati drugo stvarno promijenjeno pitanje. Ako se nijedno pitanje ne promijeni, to izričito zapisati bez izmišljanja poboljšanja. Čak i ako M1 ne popravi ciljano pitanje, ne podešavati dodatne postavke u ovom eksperimentu. Dopuniti [radni izvještaj](before-after-report.md) samo potvrđenim završnim nalazima.

## Otvorene obaveze

- Originalni tutorov šablon izvještaja još nije dostupan; radni nacrt treba kasnije uskladiti s njim.
- Pregled drugog para: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
- Demonstrator: **NIJE JOŠ URAĐENO / NIJE POTVRĐENO**.
