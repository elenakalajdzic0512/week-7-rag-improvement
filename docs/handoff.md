# Predaja koleginici — M1

## Početno stanje

Početni kod je u commitu `c233b11f7a7faa8986236732de54be9453909d44`. M1 još nije implementiran i `results/after.json` ne postoji. Početni testovi su prošli **18/18**, eval **6/12**, a otisak skupa je `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`. Prije rada pročitati [specifikaciju](change-spec.md), [početne nalaze](baseline-findings.md), [CLI provjere](baseline-cli-checks.txt), [before rezultat](../results/before.json) i [zajednički izvještaj](before-after-report.md).

## Okruženje

Raditi iz korijena projekta s Pythonom 3.12. Ako lokalni `.venv` nije dostupan, pripremiti ga bez promjene `requirements.txt` ili globalnih paketa:

```bash
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python --version
.venv/bin/python -m pytest --version
```

U početnoj fazi korišćeni su Python 3.12.14 i pytest 8.3.3.

## Dozvoljeni obim izmjene

Implementirati samo `split_text_by_sentences` u `src/chunking.py` prema [ugovoru M1](change-spec.md) i postaviti `CHUNK_STRATEGY="sentences"` u `src/config.py`. Dodati ciljane testove bez brisanja ili slabljenja postojećih. `CHUNK_SIZE=140` i `CHUNK_OVERLAP=30` ostaju zapisani; overlap se ne koristi u sentences grani. Ne mijenjati korpus, `eval/eval_set.json`, retrieval, odgovaranje, metrike, druge postavke ili zavisnosti. **Ne prepisivati niti ručno uređivati `results/before.json`.**

## Koraci provjere

Prije evala provjeriti da `results/after.json` ne postoji; ako već postoji, sačuvati ga bez prepisivanja i razjasniti porijeklo. Zatim iz korijena projekta:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m src.eval_runner --out results/after.json
set -o pipefail
.venv/bin/python -m src.eval_compare results/before.json results/after.json | tee results/comparison.txt
```

Potvrditi jednak `eval_set_sha256` u oba rezultata. Ručno provjeriti pitanje koje se promijenilo uz `--show-retrieved`; primjer za ciljano E04:

```bash
.venv/bin/python -m src.cli --question "How many business days does a laptop replacement take?" --show-retrieved
```

Zabilježiti da li stvarni odgovor i citat sadrže „5 business days”, te verziju i status izvora. Ako se E04 ne promijeni, izabrati drugo stvarno promijenjeno pitanje. Ako se nijedno pitanje ne promijeni, to jasno zapisati. Ne podešavati druge postavke ako M1 ne pomogne.

## Dokazi koje treba sačuvati

- Izvorni `results/after.json`, s postavkama, otiskom i tabelom svih pitanja.
- Puni izlaz poređenja u `results/comparison.txt`, uključujući popravljena pitanja, regresije i promjene metrika.
- Zapis CLI provjere s tačnom komandom, odgovorom, citatima, verzijom i statusom izvora; ako nema promijenjenih pitanja, zapisati tu činjenicu.
- Commit ili pregledan diff implementacije i ciljanih testova, uz rezultat svih testova.

`results/*.json` je ignorisano u Gitu. Za dijeljenje završnog rezultata izričito dodati **samo** `results/after.json` komandom `git add -f -- results/after.json`; ne dodavati sve ignorisane fajlove. Sačuvati `before.json` neizmijenjen.

## Završne obaveze

Dopuniti [zajednički izvještaj](before-after-report.md) samo potvrđenim završnim nalazima. Navesti **sve regresije** i **najmanje jedno preostalo ograničenje**. Pribaviti i zabilježiti komentar drugog para. Izabrati demonstratora; trenutno se dogovara.
