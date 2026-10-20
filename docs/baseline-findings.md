# Week 7 — početno stanje RAG sistema

Ovo je dokumentacija početnog stanja. Kod, korpus, konfiguracija, eval skup i metrike nisu mijenjani. CLI transkripti su u `docs/baseline-cli-checks.txt`, a izvorni rezultat mjerenja u `results/before.json`. [Zajednički izvještaj](before-after-report.md) prati zadatak prije i poslije promjene.

## Okruženje i ponovljive komande

- Projekat: `/Users/ladylazarus/Desktop/rag-week-7-weak-checkpoint`; nije bio unutar nadređenog Git repozitorijuma.
- `uv --version`: `uv 0.12.15 (Homebrew 2026-09-15 aarch64-apple-darwin)`.
- Nije postojao lokalni `.venv` ni instaliran Python 3.12. `uv` je instalirao CPython 3.12.14; lokalni `.venv/bin/python` je Python 3.12.14 i `pytest` je 8.3.3. Zavisnosti su instalirane samo u `.venv`.
- Komande pripreme (privremeni uv keš je van projekta):

  ```bash
  UV_CACHE_DIR=/private/tmp/uv-week7-cache uv python install 3.12
  UV_CACHE_DIR=/private/tmp/uv-week7-cache uv venv --python 3.12 .venv
  UV_CACHE_DIR=/private/tmp/uv-week7-cache uv pip install --python .venv/bin/python -r requirements.txt
  .venv/bin/python --version
  .venv/bin/python -m pytest --version
  ```

- Početni commit neizmijenjenog kostura na `main`: `c233b11f7a7faa8986236732de54be9453909d44` (`Record unmodified Week 7 RAG starter`). U taj commit ušli su samo eksplicitno odabrani projektni fajlovi; početni dokazi su dodati zasebnim dokumentacijskim commitom `8483353a21d90ff352f10720f3fcb4d16efbf7e9`.
- Test: `.venv/bin/python -m pytest` — 18/18 prošlo, izlazni status 0.
- Prije mjerenja `results/before.json` nije postojao. Komanda: `.venv/bin/python -m src.eval_runner --out results/before.json` — izlazni status 0. Za kasniji završni eval isti interpreter i poziv s `--out results/after.json`.
- SHA-256 sirovih bajtova `eval/eval_set.json`: `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`; poklapa se s ranije utvrđenim otiskom.
- Snimljene postavke: `CHUNK_STRATEGY=chars`, `CHUNK_SIZE=140`, `CHUNK_OVERLAP=30`, `TOP_K=2`, `RETRIEVAL_MIN_SCORE=0.01`, `STOPWORDS_ENABLED=False`, `CURRENT_ONLY=False`, `REFUSAL_THRESHOLD=0.02`, `CITATION_MIN_SCORE=None`.

## Metrike i sva pitanja

`results/before.json` je sačuvan bez ručnih izmjena. Prošlo je **6/12** pitanja; tačna odluka odgovor/odbijanje **0.8333** (10/12); pogodak očekivanog dokumenta kod pitanja s odgovorom **0.7778** (7/9); srednja preciznost citata među odgovorima **0.4545**. `—` znači da metrika nije primjenjiva. `Hit` provjerava dokument u retrieval rezultatima, `Fact` doslovno normalizovanu očekivanu frazu u citiranom chunku, a `CitPrec` udio citata iz očekivanog dokumenta.

| ID | Pitanje | Očekivano | Stvarno | Hit | Fact | CitPrec | Prolaz |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | How many days of annual leave do employees get? | odgovor | odgovor | da | da | 0.50 | da |
| E02 | How often do passwords need to be changed? | odgovor | odgovor | da | da | 0.50 | da |
| E03 | What is the yearly training budget per employee? | odgovor | odgovor | da | da | 0.50 | da |
| E04 | How many business days does a laptop replacement take? | odgovor | odgovor | da | ne | 1.00 | ne |
| E05 | How long until I get a new notebook computer? | odgovor | odgovor | ne | ne | 0.00 | ne |
| E06 | How many days per week can I work remotely? | odgovor | odgovor | ne | ne | 0.00 | ne |
| E07 | What are the IT support hours? | odgovor | odgovor | da | da | 1.00 | da |
| E08 | By when must travel receipts be submitted? | odgovor | odgovor | da | da | 0.50 | da |
| E09 | Where do I request a replacement laptop and how long does it take? | odgovor | odgovor | da | ne | 1.00 | ne |
| E10 | What is the current company stock price? | odbijanje | odgovor | — | — | 0.00 | ne |
| E11 | What is the parental leave policy? | odbijanje | odgovor | — | — | 0.00 | ne |
| E12 | Who won the 1958 football world cup? | odbijanje | odbijanje | — | — | — | da |

## Dokazani propusti

Svih šest neuspjelih pitanja je ručno provjereno CLI komandom s `--show-retrieved`. Sistem ne generiše sažetu rečenicu: njegov „odgovor” je prefiks i doslovni tekst citiranih chunkova. Zato se ispod navodi sadržaj koji je stvarno prikazao, bez pripisivanja tvrdnji koje nije izrekao.

### E04 — presječena činjenica

- **Pitanje:** “How many business days does a laptop replacement take?” Očekivan je odgovor **5 business days** iz važećeg `hb-01`, *Equipment replacement* (2026).
- **Stvarno:** odgovor citira `hb-01-chunk-0` i `hb-01-chunk-2`, oba current. Prvi završava s “set up by IT staff with”; drugi počinje s “iness days” i zatim govori o prijavi izgubljenog uređaja i IT portalu. Nijedan ne sadrži broj 5. `Hit=da`, `Fact=ne`, `CitPrec=1.00`, neuspjeh po metrici i sadržaju.
- **Neposredni problem:** relevantna fraza je cjelovita u `hb-01-chunk-1` (“handover can take up to 5 business days”), ali taj chunk nije u top 2; njegov skor je 0.107143, iza izabranih 0.217391 i 0.173913. **Mogući uzrok:** granice chunkova presijecaju riječi i rečenice, a leksičko rangiranje favorizuje druge dijelove istog dokumenta.

### E05 — parafraza mimo izvora

- **Pitanje:** “How long until I get a new notebook computer?” Očekivan je odgovor **5 business days** iz važećeg `hb-01`, *Equipment replacement* (2026).
- **Stvarno:** odgovor citira `hb-06-chunk-0` (*Onboarding*, 2026 current) o dvosedmičnom uvođenju i `hb-07-chunk-1` (*Annual leave*, 2026 current) o zahtjevu za godišnji odmor. Ne daje rok za računar. `Hit=ne`, `Fact=ne`, `CitPrec=0.00`; neuspjeh po metrici i sadržaju.
- **Neposredni problem:** nijedan citat ne podržava traženi rok. **Mogući uzrok:** leksički retrieval ne povezuje “notebook computer” s “laptop”, a česte riječi iz upita povlače nepovezane dokumente. Samo uklanjanje stop riječi ne bi riješilo sinonim.

### E06 — zastarjela tvrdnja

- **Pitanje:** “How many days per week can I work remotely?” Očekivan je odgovor **3 days per week** iz važećeg `hb-03`, *Remote work policy* (2026 current).
- **Stvarno:** citira samo `hb-02-chunk-0` i `hb-02-chunk-1` (*Remote work policy*, 2024 superseded); prvi eksplicitno kaže **2 days per week**. `Hit=ne`, `Fact=ne`, `CitPrec=0.00`; neuspjeh po metrici **i stvarna kontradikcija s važećim pravilom**.
- **Neposredni problem:** zastarjeli dokument ostaje pretraživ i zauzima oba mjesta u top 2. Njegovi skorovi 0.481481 i 0.400000 nadmašuju `hb-03-chunk-0` (0.370370), koji sadrži važeću vrijednost. **Mogući uzrok:** `CURRENT_ONLY=False` uz rangiranje po poklapanju riječi, bez prednosti važeće verzije.

### E09 — djelimičan odgovor bez roka

- **Pitanje:** “Where do I request a replacement laptop and how long does it take?” Očekivani rok je **5 business days** iz važećeg `hb-01`, *Equipment replacement* (2026); isti dokument kaže da se zahtjev podnosi u IT portalu pod Hardware.
- **Stvarno:** `hb-01-chunk-0` i `hb-01-chunk-2` daju tekst o zamjeni i adresu portala, ali ne cjelovit rok. `Hit=da`, `Fact=ne`, `CitPrec=1.00`; neuspjeh po metrici i nepotpun sadržaj.
- **Neposredni problem:** `hb-01-chunk-1` s cjelovitom frazom nije citiran; skor 0.142857 stavlja ga tek na peto mjesto, iza izabranih 0.260870 i 0.217391. **Mogući uzrok:** isto presijecanje činjenice i leksičko rangiranje kao u E04; veći `TOP_K` od 3 ne bi bio dovoljan za ovaj upit.

### E10 — lažno prihvaćen upit izvan korpusa

- **Pitanje:** “What is the current company stock price?” Očekivano je odbijanje: nijedan od deset dokumenata korpusa ne navodi cijenu akcije.
- **Stvarno:** sistem ne odbija i citira `hb-09-chunk-1` (*Office access and parking*, 2026 current) i `hb-05-chunk-1` (*Passwords and access*, 2026 current). Tekst je o parkingu i pristupu, bez cijene akcije. `CitPrec=0.00`, neuspjeh ponašanja. Sistem **ne izmišlja brojčanu cijenu**, već vraća nepovezan sadržaj kao odgovor.
- **Neposredni problem:** najbolji skor 0.058824 prelazi prag odbijanja 0.02. **Mogući uzrok:** slabo poklapanje opštih riječi dovoljno je za prihvatanje upita.

### E11 — pogrešna politika kao odgovor

- **Pitanje:** “What is the parental leave policy?” Očekivano je odbijanje: korpus ima pravilo o godišnjem, ali ne o roditeljskom odsustvu.
- **Stvarno:** sistem ne odbija i citira `hb-07-chunk-1` i `hb-07-chunk-0` (*Annual leave*, 2026 current). U odgovor ulaze pravila o godišnjem odmoru, bez pravila o roditeljskom. `CitPrec=0.00`, neuspjeh ponašanja i sadržaja.
- **Neposredni problem:** najbolji skor 0.166667 prelazi prag 0.02. **Mogući uzrok:** riječ “leave” i “policy” podudaraju se s pogrešnom vrstom odsustva.

Nema utvrđenog slučaja u kojem metrika označava **prolaz**, a tekst tvrdi zastarjelo suprotno pravilo. Ipak, E01–E03 i E08 prolaze s `CitPrec=0.50`: svaki odgovor sadrži i jedan citat iz drugog dokumenta. To je šum u citatima, ne dokaz kontradikcije. E06 je dokazano zastario odgovor i metrika ga ispravno označava kao neuspjeh.

## Izabrana intervencija i ostale opcije

**Izabrana intervencija: M1, chunkovanje po rečenicama.** E04 i E09 dijele neposredni, ponovljeni uzrok: očekivana činjenica ostaje u `hb-01-chunk-1`, ali top 2 vraća dijelove bez cjelovitog roka. M1 bi držao rečenicu o roku u cjelini i izbjegao komade koji počinju usred riječi. To je hipoteza o učinku, ne garantovan prolaz; promjena dužina chunkova mijenja sve skorove i zahtijeva puni završni eval.

Opcije iz `docs/improvement-menu.md`: **M2** filtriranje oko 40 čestih engleskih riječi može smanjiti šum, ali ne rješava sinonim “notebook”/“laptop”; **M3** prag odbijanja može pomoći E10, ali za E11 bi prag morao preći 0.166667 i mogao bi odbiti podržano E02 (najbolji skor 0.130435); **M4** minimalni skor citata može ukloniti sporedne citate, ali ne dodaje nedostajući dokaz; **M5** filtriranje samo važećih dokumenata direktno cilja E06, uz mogući gubitak istorijskih odgovora; **M6** veći `TOP_K` mogao bi povećati recall, ali dodaje šum i za E09 bi trebalo doći bar do petog rezultata. M1, M2, M4 i M5 zahtijevaju implementaciju; M3 i M6 su promjene postavki.

## Otvorena pitanja i ograničenja

- Nakon početne analize izabrana je M1 kao jedina intervencija; njen ugovor je u [specifikaciji](change-spec.md). Ova bilješka ostaje zapis početnih dokaza.
- Fiksni eval skup ima 12 pitanja; njegovi rezultati ne dokazuju ponašanje izvan tih pitanja. Fakt metrika traži doslovnu frazu u jednom citiranom chunku, pa ne ocjenjuje svaki oblik semantički tačnog odgovora. Istovremeno, `Pass` može tolerisati jedan nevažan od dva citata (`CitPrec=0.50`).
- Otisak potvrđuje neizmijenjene bajtove eval skupa, ali ne obuhvata korpus i kod. Za vjerodostojno poređenje treba sačuvati početni commit i dokumentovati kasniju jedinu promjenu.
- Nema trajnog indeksa, aplikacijskog keša ni slučajnog izbora. Chunkovi se grade u memoriji, a jednak skor se razrješava po `chunk_id`.
- `results/*.json` je ignorisano u Gitu; `before.json` je lokalni original i ne treba ga prepisati ili ručno uređivati. Prije dijeljenja projekta treba razjasniti dozvolu za objavljivanje početnog paketa/priručnika; u pregledanim fajlovima nema takve napomene.
