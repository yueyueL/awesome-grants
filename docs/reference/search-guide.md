---
layout: default
title: Search Guide
nav_order: 4
parent: Resources
---

# 🔎 Search & Filter Guide

Learn how to find exactly the grants you need.

## Search Strategies

### 1. By Career Stage

**I'm a graduate student**
→ Go to [Students & PhD](../audience/students/README.md)

**I'm a postdoc**
→ Go to [Postdocs & ECRs](../audience/postdocs/README.md)

**I'm faculty**
→ Go to [Faculty & PI](../audience/faculty/README.md)

### 2. By Organization

**I want NSF funding**
→ Go to [By Organization](../organizations/README.md) → National Science Foundation

**I want NIH funding**
→ Go to [By Organization](../organizations/README.md) → National Institutes of Health

**I want foundation grants**
→ Go to [By Organization](../organizations/README.md#foundations)

### 3. By Amount

**Looking for small grants (<$10k)**
- Browse [Microgrants](../types/README.md#microgrants)
- Check foundation grants

**Looking for large grants (>$100k)**
- Browse [Research Project Grants](../types/README.md#research-project-grants)
- Check federal agencies (NSF, NIH)

### 4. By Keyword

Use your browser's search function (Ctrl+F / Cmd+F) and search for:
- Research topics: "AI", "climate", "biology"
- Grant types: "fellowship", "travel", "equipment"
- Keywords from your field

## Filter Combinations

### Example 1: Postdoc + US + Biology

1. Start at [Postdocs & ECRs](../audience/postdocs/README.md)
2. Use Ctrl+F to search for "biology" or "life sciences"
3. Check grant location/eligibility

### Example 2: OSS + Small Grants + Open Internet

1. Go to [OSS Maintainers](../audience/oss/README.md)
2. Look in [Microgrants](../types/README.md#microgrants) section
3. Search for "internet", "open source", "web"

### Example 3: Faculty + Europe + Engineering

1. Start at [Faculty & PI](../audience/faculty/README.md)
2. Filter by [EU / Horizon](../regions/eu/README.md)
3. Search for "engineering" or specific field

## Advanced Tips

### Multi-Tab Strategy

Open multiple views:
1. Tab 1: [By Organization](../organizations/README.md) - Browse all NSF
2. Tab 2: [By Audience](../audience/README.md) - Your career stage
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
| **Audience** | Career stage | [View](../audience/README.md) |
| **Region** | Geographic location | [View](../regions/README.md) |
| **Organization** | Specific funder | [View](../organizations/README.md) |
| **Type** | Grant mechanism | [View](../types/README.md) |
| **Domain** | Research area | [View](../domains/README.md) |
| **Live Dashboard** | Latest grants | [View](./live-dashboard.md) |

### By Grant Type
- **Fellowships**: Personal salary support
- **Research Grants**: Project funding
- **Travel Grants**: Conference attendance
- **Microgrants**: Small amounts (<$50k)
- **OSS Grants**: Open source development

## Common Searches

**"I need money for my PhD"**
→ [Students & PhD](../audience/students/README.md) → Fellowships

**"I need postdoc funding"**
→ [Postdocs & ECRs](../audience/postdocs/README.md) → Look for "fellowship"

**"I need project funding for my lab"**
→ [Faculty & PI](../audience/faculty/README.md) → Research grants

**"I need money for my open source project"**
→ [OSS Maintainers](../audience/oss/README.md)

**"I need travel money for a conference"**
→ [By Type](../types/README.md#travel-grants--conference-grants)

## Still Can't Find It?

1. Check the [Live Dashboard](./live-dashboard.md) for newest grants
2. Run the scraper for fresh data: `python3 src/master_scraper.py`
3. Browse [All Organizations](../organizations/README.md) alphabetically
4. Search the JSON files directly

---

Need more help? Check the [How to Use Guide](./how-to-use.md)
