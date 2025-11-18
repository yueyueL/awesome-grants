#!/usr/bin/env python3
"""
Master Grant Scraper - Production-ready scraper combining all sources
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any
import time

# Import individual scrapers
from live_scrapers import NSFScraper, GrantsGovScraper, NIHScraper
from foundation_scrapers import (
    SloanFoundationScraper, MozillaGrantsScraper, NLnetScraper,
    PrototypeFundScraper, WellcomeTrustScraper
)


class MasterGrantScraper:
    """Master scraper that coordinates all grant collection"""

    def __init__(self):
        self.all_grants = []
        self.stats = {
            'total': 0,
            'by_source': {},
            'successful_scrapers': [],
            'failed_scrapers': []
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
                print(f"    ✗ ERROR: {str(e)[:80]}\n")

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

    def save_to_json(self, filename: str):
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

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved to: {filename}")
        print(f"   {self.stats['total']} grants in JSON format\n")

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
    scraper = MasterGrantScraper()

    # Scrape from all sources
    grants = scraper.scrape_all(max_per_source=50)

    # Save results
    scraper.save_to_json('../data/grants_live_master.json')

    # Show examples
    scraper.export_examples(count=10)

    print("✨ Scraping complete!")
    print(f"📁 Check '../data/grants_live_master.json' for full dataset")


if __name__ == "__main__":
    main()
