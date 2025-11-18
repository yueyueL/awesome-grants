#!/usr/bin/env python3
"""
Enhanced Wiki Generator - Creates user-friendly documentation from live scraped data
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


class EnhancedWikiGenerator:
    """Generates beautiful, user-friendly wiki from grant data"""

    def __init__(self, data_dir: str = "../data", docs_dir: str = "../docs"):
        self.data_dir = data_dir
        self.docs_dir = docs_dir
        self.grants = []
        self.metadata = {}

    def load_grants(self, filename: str = "grants_live_master.json"):
        """Load grants from scraped data"""
        filepath = os.path.join(self.data_dir, filename)

        print(f"📖 Loading grants from {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.grants = data.get('grants', [])
            self.metadata = data.get('collection_info', {})

        print(f"✓ Loaded {len(self.grants)} grants")
        print(f"  Scraped at: {self.metadata.get('scraped_at', 'Unknown')}")
        print(f"  Sources: {', '.join(self.metadata.get('successful_sources', []))}")

    def generate_all(self):
        """Generate all wiki pages"""
        print("\n🎨 Generating user-friendly wiki pages...\n")

        # Main index/home
        self.generate_home()

        # Browse by organization
        self.generate_by_organization()

        # Browse by source
        self.generate_by_source()

        # Live grants dashboard
        self.generate_live_dashboard()

        # How to use guide
        self.generate_how_to_use()

        # Search/filter guide
        self.generate_search_guide()

        print("\n✨ Wiki generation complete!")

    def generate_home(self):
        """Generate main wiki home page"""
        content = f"""# Awesome Grants Wiki - Home

Welcome to the **Awesome Grants** wiki! This is your comprehensive guide to finding funding opportunities for research, open source projects, and innovative ideas.

## 📊 Quick Stats

- **Total Grants**: {len(self.grants)} live opportunities
- **Last Updated**: {self._format_date(self.metadata.get('scraped_at', ''))}
- **Data Sources**: {', '.join(self.metadata.get('successful_sources', []))}
- **Auto-Updated**: Yes! Run `python3 src/master_scraper.py` to refresh

## 🚀 Quick Start

### I want to...

**Find grants for my career stage:**
- [Students & PhD Candidates](./by-audience.md#students--phd) - Fellowships, travel grants, summer programs
- [Postdocs & Early Career](./by-audience.md#postdocs--ecrs) - Postdoc fellowships, transition awards
- [Faculty & PIs](./by-audience.md#faculty--pi) - Research grants, CAREER awards
- [Open Source Developers](./by-audience.md#oss-maintainers) - Infrastructure funding, development grants

**Browse by my location:**
- [US Federal Grants](./by-region.md#us) - NSF, NIH, DOE, NASA
- [European Grants](./by-region.md#eu--horizon) - ERC, Horizon Europe
- [UK Grants](./by-region.md#uk-ukri-wellcome-etc) - UKRI, Wellcome Trust
- [Global/International](./by-region.md#global) - Open to all countries

**Search by organization:**
- [Browse by Funding Organization](./by-organization.md) - NSF, NIH, foundations, etc.

**See what's new:**
- [Live Grants Dashboard](./live-dashboard.md) - Latest opportunities from live scraping

## 📚 Browse Options

### By Category
- [By Audience](./by-audience.md) - Career stage (students, postdocs, faculty, OSS, indie)
- [By Region](./by-region.md) - Geographic location
- [By Type](./by-type.md) - Grant mechanism (fellowships, research, microgrants)
- [By Domain](./by-domain.md) - Research area
- [By Organization](./by-organization.md) - Funding agency/foundation

### Special Collections
- [Live Scraped Grants](./live-dashboard.md) - {len(self.grants)} opportunities auto-collected
- [Federal Opportunities](./by-organization.md#federal-agencies) - US government grants
- [Private Foundations](./by-organization.md#foundations) - Non-profit funding

## 🔍 How to Use

1. **[Start Here](./how-to-use.md)** - Complete guide to using this wiki
2. **[Search Tips](./search-guide.md)** - How to find the perfect grant
3. **[Update Data](./how-to-use.md#updating-data)** - Get latest opportunities

## 💡 Features

- ✅ **Live Data** - Auto-scraped from Grants.gov, NSF, and other sources
- ✅ **Always Fresh** - Run scraper anytime to update
- ✅ **Easy to Browse** - Organized multiple ways
- ✅ **Direct Links** - Click through to apply
- ✅ **Rich Metadata** - Amounts, deadlines, descriptions

## 🆘 Need Help?

- [How to Use This Wiki](./how-to-use.md)
- [Search and Filter Guide](./search-guide.md)
- [Report Issues](https://github.com/YOUR_USERNAME/awesome-grants/issues)

---

**Last Updated**: {self._format_date(self.metadata.get('scraped_at', ''))}
**Data Freshness**: {self._get_freshness_indicator()}
"""

        self._write_file("Home.md", content)
        print("  ✓ Generated Home.md")

    def generate_by_organization(self):
        """Generate grants organized by funding organization"""
        content = """# Browse by Organization

Find grants from specific funding agencies and foundations.

## Table of Contents

- [Federal Agencies](#federal-agencies)
- [Foundations](#foundations)
- [All Organizations](#all-organizations)

---

"""

        # Group by organization
        by_org = defaultdict(list)
        for grant in self.grants:
            org = grant.get('organization', 'Unknown')
            by_org[org].append(grant)

        # Separate federal vs foundations vs others
        federal_keywords = ['National', 'Federal', 'NSF', 'NIH', 'NASA', 'DOE', 'DARPA', 'NEH']
        federal_orgs = {}
        foundation_orgs = {}
        other_orgs = {}

        for org, grants in sorted(by_org.items()):
            if any(keyword in org for keyword in federal_keywords):
                federal_orgs[org] = grants
            elif 'Foundation' in org or 'Trust' in org:
                foundation_orgs[org] = grants
            else:
                other_orgs[org] = grants

        # Federal Agencies section
        if federal_orgs:
            content += "## Federal Agencies\n\n"
            content += f"**{sum(len(g) for g in federal_orgs.values())} grants from {len(federal_orgs)} federal agencies**\n\n"

            for org in sorted(federal_orgs.keys()):
                grants = federal_orgs[org]
                content += f"### {org}\n\n"
                content += f"**{len(grants)} opportunities**\n\n"

                for grant in sorted(grants, key=lambda x: x.get('name', '')):
                    content += self._format_grant_entry(grant)

                content += "\n---\n\n"

        # Foundations section
        if foundation_orgs:
            content += "## Foundations\n\n"
            content += f"**{sum(len(g) for g in foundation_orgs.values())} grants from {len(foundation_orgs)} foundations**\n\n"

            for org in sorted(foundation_orgs.keys()):
                grants = foundation_orgs[org]
                content += f"### {org}\n\n"
                content += f"**{len(grants)} opportunities**\n\n"

                for grant in sorted(grants, key=lambda x: x.get('name', '')):
                    content += self._format_grant_entry(grant)

                content += "\n---\n\n"

        # All Organizations (complete list)
        content += "## All Organizations\n\n"
        content += "Complete alphabetical listing:\n\n"

        for org in sorted(by_org.keys()):
            grants = by_org[org]
            content += f"### {org}\n\n"
            content += f"**{len(grants)} opportunities**\n\n"

            for grant in sorted(grants, key=lambda x: x.get('name', '')):
                content += self._format_grant_entry(grant)

            content += "\n"

        self._write_file("by-organization.md", content)
        print("  ✓ Generated by-organization.md")

    def generate_by_source(self):
        """Generate grants organized by data source"""
        content = f"""# Browse by Data Source

Grants organized by where the data was collected from.

**Total Sources**: {len(self.metadata.get('successful_sources', []))}
**Last Scraped**: {self._format_date(self.metadata.get('scraped_at', ''))}

## Table of Contents

"""

        # Group by source
        by_source = defaultdict(list)
        for grant in self.grants:
            source = grant.get('source', 'Unknown')
            by_source[source].append(grant)

        # Add TOC
        for source in sorted(by_source.keys()):
            anchor = source.lower().replace(' ', '-').replace('(', '').replace(')', '')
            content += f"- [{source}](#{anchor}) ({len(by_source[source])} grants)\n"

        content += "\n---\n\n"

        # Content for each source
        for source in sorted(by_source.keys()):
            grants = by_source[source]
            content += f"## {source}\n\n"
            content += f"**{len(grants)} grants** collected from this source\n\n"

            # Show source metadata
            if source in self.metadata.get('grants_by_source', {}):
                count = self.metadata['grants_by_source'][source]
                content += f"*Successfully scraped {count} opportunities*\n\n"

            # List grants
            for grant in sorted(grants, key=lambda x: x.get('name', '')):
                content += self._format_grant_entry(grant)

            content += "\n---\n\n"

        self._write_file("by-source.md", content)
        print("  ✓ Generated by-source.md")

    def generate_live_dashboard(self):
        """Generate live grants dashboard"""
        content = f"""# Live Grants Dashboard

**Real-time grant opportunities** collected automatically from APIs and web scraping.

## Overview

- **Total Live Grants**: {len(self.grants)}
- **Last Updated**: {self._format_date(self.metadata.get('scraped_at', ''))}
- **Successful Sources**: {len(self.metadata.get('successful_sources', []))}
- **Freshness**: {self._get_freshness_indicator()}

## Data Sources

"""

        # Show sources with counts
        for source in self.metadata.get('successful_sources', []):
            count = self.metadata.get('grants_by_source', {}).get(source, 0)
            content += f"- ✅ **{source}**: {count} grants\n"

        if self.metadata.get('failed_sources'):
            content += "\n**Sources Not Available** (may need configuration):\n"
            for source in self.metadata.get('failed_sources', []):
                content += f"- ⚙️ {source}\n"

        content += "\n## Latest Opportunities\n\n"
        content += f"Showing all {len(self.grants)} grants scraped from live sources:\n\n"

        # Group by source for display
        by_source = defaultdict(list)
        for grant in self.grants:
            source = grant.get('source', 'Unknown')
            by_source[source].append(grant)

        for source in sorted(by_source.keys()):
            grants = by_source[source]
            content += f"### From {source}\n\n"
            content += f"**{len(grants)} opportunities**\n\n"

            for grant in grants:
                content += self._format_grant_entry(grant, show_source=False)

            content += "\n"

        content += """
---

## How to Update

To get the latest grants:

```bash
cd /path/to/awesome-grants
python3 src/master_scraper.py
python3 src/enhanced_wiki_generator.py
```

This will:
1. Scrape fresh data from all sources
2. Regenerate this dashboard
3. Update all wiki pages

---

**Pro Tip**: Set up a cron job to run the scraper weekly for always-fresh data!
"""

        self._write_file("live-dashboard.md", content)
        print("  ✓ Generated live-dashboard.md")

    def generate_how_to_use(self):
        """Generate how-to-use guide"""
        content = """# How to Use This Wiki

Welcome! This guide will help you make the most of the Awesome Grants wiki.

## Quick Start

### 1. Find Grants for Your Profile

**Choose your path:**

- **Student/PhD?** → [Students & PhD Guide](./by-audience.md#students--phd)
- **Postdoc?** → [Postdocs & ECRs Guide](./by-audience.md#postdocs--ecrs)
- **Faculty/PI?** → [Faculty & PI Guide](./by-audience.md#faculty--pi)
- **OSS Developer?** → [OSS Maintainers Guide](./by-audience.md#oss-maintainers)
- **Indie Builder?** → [Indie Builders Guide](./by-audience.md#indie-builders--microgrants)

### 2. Filter by Location

If you have geographic restrictions:

- [US Only](./by-region.md#us)
- [Europe](./by-region.md#eu--horizon)
- [UK](./by-region.md#uk-ukri-wellcome-etc)
- [Global/International](./by-region.md#global)

### 3. Browse by Organization

Know which agency you want to apply to?

- [National Science Foundation](./by-organization.md#national-science-foundation)
- [National Institutes of Health](./by-organization.md#national-institutes-of-health)
- [All Organizations](./by-organization.md)

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
"""

        self._write_file("how-to-use.md", content)
        print("  ✓ Generated how-to-use.md")

    def generate_search_guide(self):
        """Generate search and filter guide"""
        content = """# Search & Filter Guide

Learn how to find exactly the grants you need.

## Search Strategies

### 1. By Career Stage

**I'm a graduate student**
→ Go to [Students & PhD](./by-audience.md#students--phd)

**I'm a postdoc**
→ Go to [Postdocs & ECRs](./by-audience.md#postdocs--ecrs)

**I'm faculty**
→ Go to [Faculty & PI](./by-audience.md#faculty--pi)

### 2. By Organization

**I want NSF funding**
→ Go to [By Organization](./by-organization.md) → National Science Foundation

**I want NIH funding**
→ Go to [By Organization](./by-organization.md) → National Institutes of Health

**I want foundation grants**
→ Go to [By Organization](./by-organization.md#foundations)

### 3. By Amount

**Looking for small grants (<$10k)**
- Browse [Microgrants](./by-type.md#microgrants)
- Check foundation grants

**Looking for large grants (>$100k)**
- Browse [Research Project Grants](./by-type.md#research-project-grants)
- Check federal agencies (NSF, NIH)

### 4. By Keyword

Use your browser's search function (Ctrl+F / Cmd+F) and search for:
- Research topics: "AI", "climate", "biology"
- Grant types: "fellowship", "travel", "equipment"
- Keywords from your field

## Filter Combinations

### Example 1: Postdoc + US + Biology

1. Start at [Postdocs & ECRs](./by-audience.md#postdocs--ecrs)
2. Use Ctrl+F to search for "biology" or "life sciences"
3. Check grant location/eligibility

### Example 2: OSS + Small Grants + Open Internet

1. Go to [OSS Maintainers](./by-audience.md#oss-maintainers)
2. Look in [Microgrants](./by-type.md#microgrants) section
3. Search for "internet", "open source", "web"

### Example 3: Faculty + Europe + Engineering

1. Start at [Faculty & PI](./by-audience.md#faculty--pi)
2. Filter by [EU / Horizon](./by-region.md#eu--horizon)
3. Search for "engineering" or specific field

## Advanced Tips

### Multi-Tab Strategy

Open multiple views:
1. Tab 1: [By Organization](./by-organization.md) - Browse all NSF
2. Tab 2: [By Audience](./by-audience.md) - Your career stage
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
- `\\$[0-9]+,000` - Find grants with specific amounts
- `deadline.*2025` - Find 2025 deadlines
- `(NSF|NIH|NASA)` - Find federal agency grants

## Quick Reference

### By Category
| Category | Best For | Link |
|----------|----------|------|
| **Audience** | Career stage | [View](./by-audience.md) |
| **Region** | Geographic location | [View](./by-region.md) |
| **Organization** | Specific funder | [View](./by-organization.md) |
| **Type** | Grant mechanism | [View](./by-type.md) |
| **Source** | Data origin | [View](./by-source.md) |
| **Live Dashboard** | Latest grants | [View](./live-dashboard.md) |

### By Grant Type
- **Fellowships**: Personal salary support
- **Research Grants**: Project funding
- **Travel Grants**: Conference attendance
- **Microgrants**: Small amounts (<$50k)
- **OSS Grants**: Open source development

## Common Searches

**"I need money for my PhD"**
→ [Students & PhD](./by-audience.md#students--phd) → Fellowships

**"I need postdoc funding"**
→ [Postdocs & ECRs](./by-audience.md#postdocs--ecrs) → Look for "fellowship"

**"I need project funding for my lab"**
→ [Faculty & PI](./by-audience.md#faculty--pi) → Research grants

**"I need money for my open source project"**
→ [OSS Maintainers](./by-audience.md#oss-maintainers)

**"I need travel money for a conference"**
→ [By Type](./by-type.md#travel-grants--conference-grants)

## Still Can't Find It?

1. Check the [Live Dashboard](./live-dashboard.md) for newest grants
2. Run the scraper for fresh data: `python3 src/master_scraper.py`
3. Browse [All Organizations](./by-organization.md) alphabetically
4. Search the JSON files directly

---

Need more help? Check the [How to Use Guide](./how-to-use.md)
"""

        self._write_file("search-guide.md", content)
        print("  ✓ Generated search-guide.md")

    def _format_grant_entry(self, grant: Dict[str, Any], show_source: bool = True) -> str:
        """Format a grant entry for display"""
        entry = f"#### [{grant.get('name', 'Unknown')}]({grant.get('url', '#')})\n\n"

        if grant.get('organization'):
            entry += f"- **Organization**: {grant['organization']}\n"

        if grant.get('amount'):
            entry += f"- **Amount**: {grant['amount']}\n"

        if grant.get('deadline'):
            entry += f"- **Deadline**: {grant['deadline']}\n"

        if grant.get('description'):
            desc = grant['description'][:200] + ('...' if len(grant['description']) > 200 else '')
            entry += f"- **Description**: {desc}\n"

        if show_source and grant.get('source'):
            entry += f"- **Source**: {grant['source']}\n"

        if grant.get('scraped_at'):
            entry += f"- **Collected**: {self._format_date(grant['scraped_at'])}\n"

        entry += "\n"
        return entry

    def _format_date(self, date_str: str) -> str:
        """Format ISO date to readable format"""
        if not date_str:
            return "Unknown"

        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %H:%M UTC")
        except:
            return date_str

    def _get_freshness_indicator(self) -> str:
        """Get freshness indicator"""
        scraped_at = self.metadata.get('scraped_at', '')
        if not scraped_at:
            return "Unknown"

        try:
            dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            delta = now - dt

            if delta.days == 0:
                return "🟢 Fresh (today)"
            elif delta.days <= 7:
                return f"🟡 Recent ({delta.days} days ago)"
            else:
                return f"🔴 Needs update ({delta.days} days ago)"
        except:
            return "Unknown"

    def _write_file(self, filename: str, content: str):
        """Write content to file"""
        filepath = os.path.join(self.docs_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print(" " * 15 + "ENHANCED WIKI GENERATOR")
    print(" " * 10 + "User-Friendly Documentation Builder")
    print("=" * 60 + "\n")

    generator = EnhancedWikiGenerator()

    # Load live scraped data
    generator.load_grants("grants_live_master.json")

    # Generate all wiki pages
    generator.generate_all()

    print(f"\n✅ Wiki generated successfully!")
    print(f"📂 Location: docs/")
    print(f"🏠 Start at: docs/Home.md")


if __name__ == "__main__":
    main()
