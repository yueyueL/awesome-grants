#!/usr/bin/env python3
"""
Master Grant Scraper - Production-ready scraper combining all sources
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Import individual scrapers
from live_scrapers import NSFScraper, GrantsGovScraper, NIHScraper
from foundation_scrapers import (
    SloanFoundationScraper, MozillaGrantsScraper, NLnetScraper,
    PrototypeFundScraper, WellcomeTrustScraper
)

# Anchor all default paths to the repository root so the scraper works
# regardless of the current working directory.
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / 'data' / 'grants_live_master.json'
RUN_REPORT_PATH = ROOT / 'data' / 'last_run_report.json'


class MasterGrantScraper:
    """Master scraper that coordinates all grant collection"""

    def __init__(self):
        self.all_grants = []
        self.stats = {
            'total': 0,
            'by_source': {},
            'successful_scrapers': [],
            'failed_scrapers': [],
            'errors': {}
        }

    def scrape_all(self, max_per_source: int = 50):
        """Scrape from all available sources"""

        print("\n" + "=" * 70)
        print(" " * 15 + "MASTER GRANT SCRAPER")
        print(" " * 10 + "Live Data Collection from Web & APIs")
        print("=" * 70 + "\n")

        # Define scrapers to try (ordered by reliability)
        scrapers = [
            ('NSF RSS Feed', NSFScraper(), True),  # Most reliable
            ('Grants.gov API', GrantsGovScraper(), False),  # May have SSL issues
            ('NIH', NIHScraper(), False),
            ('Sloan Foundation', SloanFoundationScraper(), False),
            ('Mozilla Foundation', MozillaGrantsScraper(), False),
            ('NLnet', NLnetScraper(), False),
            ('Prototype Fund', PrototypeFundScraper(), False),
            ('Wellcome Trust', WellcomeTrustScraper(), False),
        ]

        for name, scraper, is_reliable in scrapers:
            try:
                print(f"{'►' * 3} Scraping {name}...")

                grants = scraper.scrape(max_grants=max_per_source)

                if grants and len(grants) > 0:
                    self.all_grants.extend(grants)
                    self.stats['by_source'][name] = len(grants)
                    self.stats['successful_scrapers'].append(name)
                    print(f"    ✓ SUCCESS: {len(grants)} grants collected\n")
                else:
                    self.stats['by_source'][name] = 0
                    if is_reliable:
                        print(f"    ⚠  WARNING: Expected data but got 0 grants\n")
                    else:
                        print(f"    ℹ  No grants found (may need HTML structure update)\n")

                # Be polite - don't hammer servers
                time.sleep(2)

            except Exception as e:
                self.stats['failed_scrapers'].append(name)
                self.stats['by_source'][name] = 0
                self.stats['errors'][name] = f"{type(e).__name__}: {e}"
                print(f"    ✗ ERROR ({type(e).__name__}): {e}\n")

        self.stats['total'] = len(self.all_grants)

        self._print_summary()

        return self.all_grants

    def _print_summary(self):
        """Print collection summary"""
        print("\n" + "=" * 70)
        print(" " * 20 + "COLLECTION SUMMARY")
        print("=" * 70)

        print(f"\n📊 Total Grants Collected: {self.stats['total']}")

        print(f"\n✅ Successful Sources ({len(self.stats['successful_scrapers'])}):")
        for source in self.stats['successful_scrapers']:
            count = self.stats['by_source'][source]
            print(f"   • {source}: {count} grants")

        if self.stats['failed_scrapers']:
            print(f"\n❌ Failed Sources ({len(self.stats['failed_scrapers'])}):")
            for source in self.stats['failed_scrapers']:
                print(f"   • {source}")

        print("\n" + "=" * 70 + "\n")

    def save_to_json(self, filename):
        """Save all grants to JSON"""
        data = {
            "collection_info": {
                "scraped_at": datetime.now().isoformat(),
                "total_grants": self.stats['total'],
                "successful_sources": self.stats['successful_scrapers'],
                "failed_sources": self.stats['failed_scrapers'],
                "grants_by_source": self.stats['by_source']
            },
            "grants": self.all_grants
        }

        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved to: {filename}")
        print(f"   {self.stats['total']} grants in JSON format\n")

    def save_run_report(self, filename=RUN_REPORT_PATH):
        """Write a machine-readable per-source run report (for CI)"""
        sources = {}
        for name, count in self.stats['by_source'].items():
            if name in self.stats['failed_scrapers']:
                status = 'error'
            elif name in self.stats['successful_scrapers']:
                status = 'success'
            else:
                status = 'empty'
            sources[name] = {
                'status': status,
                'count': count,
                'error': self.stats['errors'].get(name)
            }

        report = {
            'scraped_at': datetime.now().isoformat(),
            'total_grants': self.stats['total'],
            'successful_sources': len(self.stats['successful_scrapers']),
            'failed_sources': len(self.stats['failed_scrapers']),
            'sources': sources
        }

        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📋 Run report saved to: {filename}\n")

    def export_examples(self, count: int = 5):
        """Print example grants"""
        if not self.all_grants:
            return

        print(f"📝 Example Grants ({min(count, len(self.all_grants))} of {len(self.all_grants)}):")
        print("-" * 70)

        for i, grant in enumerate(self.all_grants[:count], 1):
            print(f"\n{i}. {grant.get('name', 'Unknown')[:65]}")
            print(f"   Organization: {grant.get('organization', 'N/A')}")
            print(f"   Source: {grant.get('source', 'N/A')}")
            print(f"   URL: {grant.get('url', 'N/A')[:60]}...")
            if grant.get('description'):
                print(f"   Description: {grant['description'][:80]}...")

        print("\n" + "-" * 70 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Scrape research/OSS grants from all configured sources"
    )
    parser.add_argument(
        '--output', type=Path, default=DEFAULT_OUTPUT,
        help=f"Output JSON file (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        '--max-per-source', type=int, default=50,
        help="Maximum grants to collect per source (default: 50)"
    )
    args = parser.parse_args()

    scraper = MasterGrantScraper()

    # Scrape from all sources
    scraper.scrape_all(max_per_source=args.max_per_source)

    # Always write the machine-readable run report (used by CI)
    scraper.save_run_report(RUN_REPORT_PATH)

    # Fail loudly if every source came back empty/failed, so CI does not
    # commit an empty dataset.
    if not scraper.stats['successful_scrapers']:
        print("✗ ERROR: All scrapers failed or returned no grants. "
              "Not writing output; exiting with status 1.", file=sys.stderr)
        sys.exit(1)

    # Save results
    scraper.save_to_json(args.output)

    # Show examples
    scraper.export_examples(count=10)

    print("✨ Scraping complete!")
    print(f"📁 Check '{args.output}' for full dataset")


if __name__ == "__main__":
    main()
