# Greenvolt Next Romania Python scraper

Scraper pentru **GREENVOLT NEXT ROMANIA S.A.**, CIF **48838800**, destinat
[peviitor.ro](https://peviitor.ro). Datele firmei au fost confirmate prin
serviciul de verificare ANAF/CUIScan.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
python -m scraper.main --dry-run
```

După verificarea rezultatului, `python -m scraper.main` încarcă joburile.
Folosește `.venv`, deoarece auditul existent de placeholders exclude acest
folder. Un director `venv/` vechi trebuie mutat în afara proiectului.

## Sursa și filtrarea

[Widget Workable](https://apply.workable.com/api/v1/widget/accounts/greenvolt?details=true)
cu `details=true`. Sunt păstrate exclusiv înregistrările cu țara `Romania`,
apoi sunt eliminate URL-urile duplicate. URL-ul real, orașul și modul de lucru
sunt preluate din sursă. Nu este necesar Chromium pentru acest API JSON.

La verificarea din 1 noiembrie 2026 exista un job pentru România:
[Commercial B2B — Timișoara](https://apply.workable.com/j/B5C9B0385F), on-site,
departamentul Greenvolt Next Romania. Numărul poate varia în timp.

Scraperul validează firma, câmpurile joburilor și linkurile înainte de upload.
Canary-ul oprește rulările fără rezultate. Ștergerea automată a joburilor
absente dintr-o rulare este dezactivată.

## Automatizare

Workflow-ul **Scrape** rulează zilnic la 06:00 UTC. Poate fi pornit manual,
cu `dry_run` activat pentru verificare sau dezactivat pentru încărcare.
Workflow-ul **Tests** rulează la push și pull request. Ambele folosesc
workflow-urile reutilizabile din template-ul oficial Brewtality-3-16.

## Layout

- `config/company.json`: identitatea firmei și linkurile oficiale.
- `config/scraper.json`: sursa Workable și configurația rulării.
- `scraper/parse.py`: filtrarea și extragerea datelor.
- `scraper/main.py`: validare, încărcare și generarea documentației.
- `tests/`: teste unitare, de consistență și verificări externe.
- `docs/`: pagina publică și rezultatele generate de scraper.

## License

MIT.
