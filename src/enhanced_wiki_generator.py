#!/usr/bin/env python3
"""
Enhanced Wiki Generator - Creates user-friendly documentation from live scraped data
"""

import json
import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

REPO_URL = 'https://github.com/yueyueL/awesome-grants'
ROOT = Path(__file__).resolve().parent.parent


class EnhancedWikiGenerator:
    """Generates beautiful, user-friendly wiki from grant data"""

    def __init__(self, data_dir: Path = ROOT / "data", docs_dir: Path = ROOT / "docs"):
        self.data_dir = data_dir
        self.docs_dir = docs_dir
        self.grants = []
        self.metadata = {}

    def load_grants(self, filename: str = "grants_live_master.json"):
        """Load grants from scraped data"""
        filepath = os.path.join(self.data_dir, filename)

        print(f"📖 Loading grants from {filename}...")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise SystemExit(
                f"❌ Data file not found: {filepath}\n"
                "Run: python3 src/master_scraper.py first"
            )
        except json.JSONDecodeError as e:
            raise SystemExit(
                f"❌ Data file is not valid JSON ({filepath}): {e}\n"
                "Run: python3 src/master_scraper.py first"
            )

        self.grants = data.get('grants', [])
        self.metadata = data.get('collection_info', {})

        print(f"✓ Loaded {len(self.grants)} grants")
        print(f"  Scraped at: {self.metadata.get('scraped_at', 'Unknown')}")
        print(f"  Sources: {', '.join(self.metadata.get('successful_sources', []))}")

    def generate_all(self):
        """Generate all wiki pages"""
        print("\n🎨 Generating user-friendly wiki pages...\n")

        # docs/Home.md is hand-authored; the generator intentionally skips it.
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
        """No-op: docs/Home.md is hand-authored and must not be overwritten."""
        print("  ⏭ Skipped Home.md (hand-authored page, not generated)")

    def generate_by_organization(self):
        """Generate grants organized by funding organization"""
        content = self._front_matter(
            layout="default",
            title="Grants by Organization",
            nav_order=9,
            permalink="/docs/by-organization",
        )
        content += """# Browse by Organization

Find grants from specific funding agencies and foundations.

## Table of Contents

- [Federal Agencies](#federal-agencies)
- [Foundations](#foundations)
- [All Organizations](#all-organizations)

---

"""

        active_grants, expired_grants = self._split_expired(self.grants)

        # Group by organization
        by_org = defaultdict(list)
        for grant in active_grants:
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

        content += self._closed_note(expired_grants)

        self._write_file(os.path.join("organizations", "README.md"), content)
        print("  ✓ Generated organizations/README.md")

    def generate_by_source(self):
        """Generate grants organized by data source"""
        content = self._front_matter(
            layout="default",
            title="Data Sources",
            parent="Resources",
            nav_order=8,
            permalink="/docs/data-sources",
        )
        content += f"""# Browse by Data Source

Grants organized by where the data was collected from.

**Total Sources**: {len(self.metadata.get('successful_sources', []))}
**Last Scraped**: {self._format_date(self.metadata.get('scraped_at', ''))}

## Table of Contents

"""

        active_grants, expired_grants = self._split_expired(self.grants)

        # Group by source
        by_source = defaultdict(list)
        for grant in active_grants:
            source = grant.get('source', 'Unknown')
            by_source[source].append(grant)

        # Add TOC
        for source in sorted(by_source.keys()):
            anchor = self._anchor(source)
            content += f"- [{source}](#{anchor}) ({len(by_source[source])} grants)\n"

        content += "\n---\n\n"

        # Content for each source
        for source in sorted(by_source.keys()):
            grants = by_source[source]
            content += f"## {source}\n\n"
            content += f"**{len(grants)} open grants** collected from this source\n\n"

            # Show source metadata
            if source in self.metadata.get('grants_by_source', {}):
                count = self.metadata['grants_by_source'][source]
                content += f"*Successfully scraped {count} opportunities*\n\n"

            # List grants
            for grant in sorted(grants, key=lambda x: x.get('name', '')):
                content += self._format_grant_entry(grant)

            content += "\n---\n\n"

        content += self._closed_note(expired_grants)

        self._write_file(os.path.join("reference", "data-sources.md"), content)
        print("  ✓ Generated reference/data-sources.md")

    def generate_live_dashboard(self):
        """Generate live grants dashboard"""
        active_grants, expired_grants = self._split_expired(self.grants)

        content = self._front_matter(
            layout="default",
            title="Live Dashboard",
            nav_order=6,
            parent="Resources",
            permalink="/docs/live-dashboard",
        )
        content += f"""# Live Grants Dashboard

**Real-time grant opportunities** collected automatically from APIs and web scraping.

## Overview

- **Open Grants Listed**: {len(active_grants)}
- **Data Collected**: {self._get_freshness_indicator()}
- **Successful Sources**: {len(self.metadata.get('successful_sources', []))}

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
        content += f"Showing {len(active_grants)} open grants scraped from live sources:\n\n"

        # Group by source for display
        by_source = defaultdict(list)
        for grant in active_grants:
            source = grant.get('source', 'Unknown')
            by_source[source].append(grant)

        for source in sorted(by_source.keys()):
            grants = by_source[source]
            content += f"### From {source}\n\n"
            content += f"**{len(grants)} opportunities**\n\n"

            for grant in grants:
                content += self._format_grant_entry(grant, show_source=False)

            content += "\n"

        content += self._closed_note(expired_grants)

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

        self._write_file(os.path.join("reference", "live-dashboard.md"), content)
        print("  ✓ Generated reference/live-dashboard.md")

    def generate_how_to_use(self):
        """Generate how-to-use guide"""
        content = self._front_matter(
            layout="default",
            title="How to Use",
            nav_order=5,
            parent="Resources",
            permalink="/docs/how-to-use",
        )
        content += f"""# How to Use This Wiki

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
- 🐛 [Report Issues]({REPO_URL}/issues)

---

Happy grant hunting! 🎯
"""

        self._write_file(os.path.join("reference", "how-to-use.md"), content)
        print("  ✓ Generated reference/how-to-use.md")

    def generate_search_guide(self):
        """Generate search and filter guide"""
        content = self._front_matter(
            layout="default",
            title="Search Guide",
            nav_order=4,
            parent="Resources",
            permalink="/docs/search-guide",
        )
        content += """# Search & Filter Guide

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
- `\\$[0-9]+,000` - Find grants with specific amounts
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
"""

        self._write_file(os.path.join("reference", "search-guide.md"), content)
        print("  ✓ Generated reference/search-guide.md")

    def _front_matter(self, **fields) -> str:
        """Build a Jekyll front matter block from ordered keyword fields."""
        lines = ["---"]
        for key, value in fields.items():
            lines.append(f"{key}: {value}")
        lines.append("---")
        return "\n".join(lines) + "\n\n"

    def _anchor(self, heading: str) -> str:
        """Slugify a heading the way kramdown does (GFM-style anchors)."""
        return re.sub(r'[^a-z0-9 -]', '', heading.lower()).replace(' ', '-')

    def _parse_deadline(self, deadline: Any) -> Optional[date]:
        """Parse a deadline string; return None when unparseable."""
        if not deadline or not isinstance(deadline, str):
            return None
        for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(deadline.strip(), fmt).date()
            except ValueError:
                continue
        return None

    def _split_expired(self, grants: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Split grants into (active, expired) using parseable deadlines.

        Grants with unparseable or missing deadlines pass through as active.
        """
        today = date.today()
        active, expired = [], []
        for grant in grants:
            parsed = self._parse_deadline(grant.get('deadline'))
            if parsed is not None and parsed < today:
                expired.append(grant)
            else:
                active.append(grant)
        return active, expired

    def _closed_note(self, expired: List[Dict[str, Any]]) -> str:
        """Render a collapsed note listing recently closed (expired) grants."""
        if not expired:
            return ""
        note = "<details markdown=\"1\">\n"
        note += f"<summary>Recently closed ({len(expired)})</summary>\n\n"
        note += "These opportunities have deadlines in the past and are excluded from the main listing:\n\n"
        for grant in sorted(expired, key=lambda x: x.get('name', '')):
            note += self._format_grant_entry(grant)
        note += "</details>\n\n"
        return note

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
        except Exception as e:
            print(f"  ⚠️ Could not parse date '{date_str}': {e}")
            return date_str

    def _get_freshness_indicator(self) -> str:
        """Report the actual collection date, warning when data is stale."""
        scraped_at = self.metadata.get('scraped_at', '')
        if not scraped_at:
            return "Unknown"

        formatted = self._format_date(scraped_at)
        try:
            dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            delta = now - dt
            if delta.days > 30:
                return (
                    f"{formatted} — ⚠️ this data is {delta.days} days old; "
                    "run `python3 src/master_scraper.py` to refresh"
                )
        except Exception as e:
            print(f"  ⚠️ Could not compute data age from '{scraped_at}': {e}")
        return formatted

    def _write_file(self, relpath: str, content: str):
        """Write content to a path relative to the docs directory."""
        filepath = os.path.join(self.docs_dir, relpath)
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
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
    print(f"🏠 Hand-authored home page: docs/Home.md (not regenerated)")


if __name__ == "__main__":
    main()
