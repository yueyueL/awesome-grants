# Data directory

This directory is excluded from the Jekyll build (`_config.yml`). It holds the
machine-readable datasets behind the awesome-grants list.

## Active files

| File | Description |
| --- | --- |
| `grants.json` | Canonical curated dataset (66 grants), hand-maintained. |
| `grants_live_master.json` | Live scrape output. Regenerate with `python3 src/master_scraper.py`. |
| `grants_foundations.json` | Foundation scraper output — currently empty pending scraper fixes. |

Note: `grants_scraped_live.json` may reappear here; it is recreated by
`src/live_scrapers.py` when run standalone and is superseded by
`grants_live_master.json`.

## legacy/

Frozen snapshots generated on 2025-11-16 by a script that is no longer in the
repository, so they cannot be regenerated. They are kept for reference only:

- the `grants_by_*` groupings are trivially derivable from `grants.json`'s
  `audience`, `region`, `type`, and `domain` fields;
- counts and contents may disagree with the current curated data.

## Known data caveats

- Deadlines use mixed formats: `MM/DD/YYYY` in scraped data, free text in the
  curated data.
- Always verify deadlines and eligibility on the official grant pages before
  relying on them.
