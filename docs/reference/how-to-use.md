---
layout: default
title: How to Use
nav_order: 5
parent: Resources
permalink: /docs/how-to-use
---

# How to Use This Wiki

Welcome! This guide will help you make the most of the Awesome Grants wiki.

## Quick Start

### 1. Find Grants for Your Profile

The listings cover every career stage — students and PhD candidates, postdocs
and early-career researchers, faculty and PIs, open source maintainers, and
indie builders. Use your browser's search (Ctrl+F / Cmd+F) on the listing
pages to find grants matching your stage.

### 2. Filter by Location

If you have geographic restrictions, check each grant's eligibility details —
the collection includes US federal, European, UK, and global/international
opportunities.

### 3. Browse by Organization

Know which agency you want to apply to?

- [National Science Foundation](../organizations/README.md#national-science-foundation)
- [National Institutes of Health](../organizations/README.md)
- [All Organizations](../organizations/README.md)

## Understanding Grant Entries

Each grant entry shows:

```
### Grant Name
- **Organization**: Who funds it
- **URL**: Direct link to application
- **Amount**: Funding amount (if available)
- **Deadline**: When to apply
- **Description**: What it's for
- **Source**: Where we got this data
```

## Data Freshness

### Live Scraped Data

This wiki is built from **live scraped data**:
- Auto-collected from Grants.gov, NSF, and other sources
- Updated whenever you run the scraper
- See [Live Dashboard](./live-dashboard.md) for latest

### Updating Data

To get fresh grants:

```bash
# 1. Run the scraper
python3 src/master_scraper.py

# 2. Regenerate wiki
python3 src/enhanced_wiki_generator.py
```

**Recommended**: Update weekly for fresh opportunities

## Tips for Success

### 1. Check Multiple Categories

Don't limit yourself to one category! A grant might appear in:
- By organization (e.g., "NSF")
- By data source (e.g., "Grants.gov")
- The live dashboard

### 2. Look at Similar Grants

If you find one good grant, check:
- Other grants from the same organization
- Grants in the same research domain
- Grants with similar amounts

### 3. Save What You Find

- Bookmark grants you're interested in
- Note application deadlines
- Check eligibility carefully on the official website

### 4. Verify on Official Sites

⚠️ **Important**: Always verify details on the official grant website:
- Deadlines may change
- Eligibility requirements are detailed
- Application procedures vary

## Navigation Tips

### Using the Table of Contents

Each page has a clickable table of contents at the top. Use it to jump to sections.

### Browser Search

Use Ctrl+F (Cmd+F on Mac) to search within a page for keywords.

### Multiple Tabs

Open categories in different tabs to compare options.

## Common Questions

**Q: How often is this updated?**
A: Whenever the scraper runs. Check [Live Dashboard](./live-dashboard.md) for last update time.

**Q: Are all grants listed current?**
A: We show what's scraped from live sources. Always verify deadlines on official sites.

**Q: Can I add a grant?**
A: Yes! See the [Contributing Guide](../../README.md#contributing) in the main README.

**Q: What if a link is broken?**
A: Report it as an issue on GitHub or run the scraper to get fresh data.

## Need Help?

- 📖 [Search Guide](./search-guide.md) - How to find specific grants
- 📊 [Live Dashboard](./live-dashboard.md) - See latest opportunities
- 🏠 [Wiki Home](../Home.md) - Back to main page
- 🐛 [Report Issues](https://github.com/yueyueL/awesome-grants/issues)

---

Happy grant hunting! 🎯
