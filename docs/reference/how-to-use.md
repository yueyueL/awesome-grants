---
layout: default
title: How to Use
nav_order: 5
parent: Resources
---

# 📖 How to Use This Wiki

Welcome! This guide will help you make the most of the Awesome Grants wiki.

## Quick Start

### 1. Find Grants for Your Profile

**Choose your path:**

- **Student/PhD?** → [Students & PhD Guide](../audience/students/README.md)
- **Postdoc?** → [Postdocs & ECRs Guide](../audience/postdocs/README.md)
- **Faculty/PI?** → [Faculty & PI Guide](../audience/faculty/README.md)
- **OSS Developer?** → [OSS Maintainers Guide](../audience/oss/README.md)
- **Indie Builder?** → [Indie Builders Guide](../audience/indie/README.md)

### 2. Filter by Location

If you have geographic restrictions:

- [US Only](../regions/us/README.md)
- [Europe](../regions/eu/README.md)
- [UK](../regions/uk/README.md)
- [Global/International](../regions/global/README.md)

### 3. Browse by Organization

Know which agency you want to apply to?

- [National Science Foundation](../organizations/README.md#national-science-foundation)
- [National Institutes of Health](../organizations/README.md#national-institutes-of-health)
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
- By audience (e.g., "Faculty")
- By organization (e.g., "NSF")
- By region (e.g., "US")

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
A: Yes! See the [Contributing Guide](../README.md#contributing) in the main README.

**Q: What if a link is broken?**
A: Report it as an issue on GitHub or run the scraper to get fresh data.

## Need Help?

- 📖 [Search Guide](./search-guide.md) - How to find specific grants
- 📊 [Live Dashboard](./live-dashboard.md) - See latest opportunities
- 🏠 [Wiki Home](./Home.md) - Back to main page
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/awesome-grants/issues)

---

Happy grant hunting! 🎯
