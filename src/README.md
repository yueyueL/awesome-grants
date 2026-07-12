# Awesome Grants - Source Code

This directory contains the automation that keeps the docs and datasets fresh.

## Overview

```
┌──────────────────────┐      ┌────────────────────────┐
│   master_scraper.py  │─────▶│  data/grants_live_*.json│
└──────────┬───────────┘      └──────────┬─────────────┘
           │                             │
           │ scraped via                 │ feeds into
┌──────────▼──────────┐        ┌─────────▼────────────────┐
│ live_scrapers.py    │        │ enhanced_wiki_generator.py│
│ foundation_scrapers │        │ (generates docs/*)        │
└─────────────────────┘        └───────────────────────────┘
```

1. **Scrape everything** with `master_scraper.py`
2. **Review/commit** the updated JSON in `../data/`
3. **Regenerate docs** with `enhanced_wiki_generator.py`

## Files

- **`master_scraper.py`** – Orchestrates every scraper/source
- **`live_scrapers.py`** – Government/API scrapers (Grants.gov, NSF, NIH, EU, UKRI)
- **`foundation_scrapers.py`** – Foundation scrapers (Sloan, Mozilla, NLnet, Prototype Fund, Wellcome)
- **`enhanced_wiki_generator.py`** – Turns `data/grants_live_master.json` into the Markdown wiki

Legacy curated JSON files are still present in `../data/` for reference, but the automation now focuses on the live pipeline above.

## Usage

> **Note:** Run the scripts from the repository root (paths are anchored via `Path(__file__)`, so this works from anywhere, but the repo root is the recommended working directory).

### 1) Collect live data

```bash
python3 src/master_scraper.py
```

Outputs:
- `data/grants_live_master.json` – merged dataset + metadata
- Stats in the terminal for each source

(`data/grants_scraped_live.json` is written only by running `live_scrapers.py` directly, not by `master_scraper.py`.)

### 2) Regenerate the wiki

```bash
python3 src/enhanced_wiki_generator.py
```

Outputs:
- Updates `docs/` (Home, by-audience, by-type, live-dashboard, etc.)
- Pulls metadata (scraped_at, source counts) from `grants_live_master.json`

### 3) Commit

```bash
cd ..
git add data/ docs/
git commit -m "Refresh live grants"
```

## Adding/Updating Scrapers

### Government & API sources (`live_scrapers.py`)

1. Create a new subclass of `GrantScraper`
2. Implement `scrape(max_grants=...)`
3. Append it to the list inside `MasterGrantScraper.scrape_all`
4. Test with `python3 master_scraper.py`

### Foundations (`foundation_scrapers.py`)

Follow the same pattern using `FoundationScraper` as the base class.

### Tips

- Keep requests gentle (`time.sleep(2)` between sources)
- Always normalize output fields:
  - `name`, `organization`, `url`
  - `amount`, `deadline`, `description`
  - `source`, `scraped_at`
- Truncate long descriptions (e.g., `[:300]`) to keep JSON manageable

## Data Format

Every scraper returns dictionaries that at minimum contain:

```json
{
  "name": "Grant Name",
  "organization": "Funding Organization",
  "url": "https://example.com",
  "amount": "Variable",
  "deadline": "2025-09-01",
  "description": "Short summary...",
  "source": "NSF RSS Feed",
  "scraped_at": "2025-11-16T12:00:00Z"
}
```

## Dependencies

- Python 3.8+
- Dependencies are listed in `requirements.txt` at the repo root

Install once (from the repo root):

```bash
pip3 install -r requirements.txt
```

## Troubleshooting

| Issue | Fix |
| --- | --- |
| HTTP 403 / blocked | Update User-Agent header or slow down requests |
| HTML structure changed | Update the parser in the relevant scraper class |
| Large responses | Reduce `max_per_source` in `master_scraper.py` |
| Docs not updating | Ensure `grants_live_master.json` exists before running `enhanced_wiki_generator.py` |

## Contributing

- Keep scrapers polite (respect robots.txt and rate limits)
- Add logging/print statements for new sources so failures are easy to spot
- Include updated `data/` + `docs/` files in PRs so reviewers can see the effect

Questions? Open an issue in the main repo.
