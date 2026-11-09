---
layout: default
title: Search Guide
nav_order: 4
parent: Resources
permalink: /docs/search-guide
---

# Search & Filter Guide

Learn how to find exactly the grants you need.

## Search Strategies

### 1. By Career Stage

Grants for every career stage — graduate students, postdocs, faculty, OSS
maintainers — appear throughout the listings. Use your browser's search
(Ctrl+F / Cmd+F) with terms like "fellowship", "postdoc", or "CAREER" to
narrow down.

### 2. By Organization

**I want NSF funding**
→ Go to [By Organization](../organizations/README.md) → National Science Foundation

**I want NIH funding**
→ Go to [By Organization](../organizations/README.md) → National Institutes of Health

**I want foundation grants**
→ Go to [By Organization](../organizations/README.md#foundations)

### 3. By Amount

**Looking for small grants (<$10k)**
- Search the listings for "microgrant"
- Check foundation grants

**Looking for large grants (>$100k)**
- Check federal agencies (NSF, NIH)
- Search for "research project"

### 4. By Keyword

Use your browser's search function (Ctrl+F / Cmd+F) and search for:
- Research topics: "AI", "climate", "biology"
- Grant types: "fellowship", "travel", "equipment"
- Keywords from your field

## Filter Combinations

### Example 1: Postdoc + US + Biology

1. Open [By Organization](../organizations/README.md)
2. Use Ctrl+F to search for "biology" or "life sciences"
3. Check grant location/eligibility

### Example 2: OSS + Small Grants + Open Internet

1. Open the [Live Dashboard](./live-dashboard.md)
2. Search for "internet", "open source", "web"
3. Check foundation sources for microgrants

### Example 3: Faculty + Europe + Engineering

1. Open [By Organization](../organizations/README.md)
2. Search for "engineering" or your specific field
3. Check each grant's regional eligibility

## Advanced Tips

### Multi-Tab Strategy

Open multiple views:
1. Tab 1: [By Organization](../organizations/README.md) - Browse all NSF
2. Tab 2: [Data Sources](./data-sources.md) - Browse by origin
3. Tab 3: [Live Dashboard](./live-dashboard.md) - Latest opportunities

Compare across tabs to find matches.

### Use the JSON Data

For power users, query the JSON directly:

```bash
# Find all grants with "AI" in the name
cat data/grants_live_master.json | jq '.grants[] | select(.name | contains("AI"))'

# Find grants over a certain amount
cat data/grants_live_master.json | jq '.grants[] | select(.amount | contains("$100"))'
```

### Regular Expressions

If viewing on GitHub or using a capable editor, use regex search:
- `\$[0-9]+,000` - Find grants with specific amounts
- `deadline.*2025` - Find 2025 deadlines
- `(NSF|NIH|NASA)` - Find federal agency grants

## Quick Reference

### By Category
| Category | Best For | Link |
|----------|----------|------|
| **Organization** | Specific funder | [View](../organizations/README.md) |
| **Source** | Data origin | [View](./data-sources.md) |
| **Live Dashboard** | Latest grants | [View](./live-dashboard.md) |

### By Grant Type
- **Fellowships**: Personal salary support
- **Research Grants**: Project funding
- **Travel Grants**: Conference attendance
- **Microgrants**: Small amounts (<$50k)
- **OSS Grants**: Open source development

## Common Searches

**"I need money for my PhD"**
→ Search the listings for "fellowship" and "graduate"

**"I need postdoc funding"**
→ Search the listings for "postdoc" and "fellowship"

**"I need project funding for my lab"**
→ Browse [By Organization](../organizations/README.md) → federal agencies

**"I need money for my open source project"**
→ Search the listings for "open source"

**"I need travel money for a conference"**
→ Search the listings for "travel"

## Still Can't Find It?

1. Check the [Live Dashboard](./live-dashboard.md) for newest grants
2. Run the scraper for fresh data: `python3 src/master_scraper.py`
3. Browse [All Organizations](../organizations/README.md) alphabetically
4. Search the JSON files directly

---

Need more help? Check the [How to Use Guide](./how-to-use.md)
