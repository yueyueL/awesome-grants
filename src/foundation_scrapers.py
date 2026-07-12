#!/usr/bin/env python3
"""
Foundation Grant Scrapers - Scrape funding opportunities from major foundations
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Repository root (this file lives in src/), so output paths work from any CWD
ROOT = Path(__file__).resolve().parent.parent

# NOTE: These amounts are static defaults, NOT scraped from the sites.
# They reflect the programs' typical/published ranges and may drift out of date.
NLNET_TYPICAL_AMOUNT = "€5,000-€50,000"
PROTOTYPE_FUND_TYPICAL_AMOUNT = "€47,500 over 6 months"
AMOUNT_NOTE = "typical range — verify on site"


class FoundationScraper:
    """Base class for foundation scrapers"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.grants = []

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape grants"""
        raise NotImplementedError

    def clean_text(self, text: str) -> str:
        """Clean text"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()


class SloanFoundationScraper(FoundationScraper):
    """Scrape Sloan Foundation opportunities"""

    def __init__(self):
        super().__init__()
        self.url = "https://sloan.org/grants/apply"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape Sloan opportunities"""
        print(f"\n🔍 Scraping Sloan Foundation...")
        grants = []

        try:
            response = self.session.get(self.url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find program sections
                programs = soup.find_all(['div', 'section'], class_=re.compile(r'program|grant'))

                for prog in programs:
                    grant = self._parse_program(prog)
                    if grant:
                        grants.append(grant)

                if not grants:
                    logging.warning(f"parsed 0 items from {self.url} — selectors may be outdated")

        except Exception as e:
            print(f"  ✗ Error: {e}")

        print(f"  ✓ Scraped {len(grants)} grants from Sloan Foundation")
        return grants[:max_grants]

    def _parse_program(self, element) -> Dict[str, Any]:
        """Parse program from HTML"""
        try:
            title_elem = element.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None

            title = self.clean_text(title_elem.text)

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else self.url
            if url and not url.startswith('http'):
                url = f"https://sloan.org{url}"

            desc_elem = element.find('p')
            desc = self.clean_text(desc_elem.text) if desc_elem else ""

            return {
                "name": title,
                "organization": "Alfred P. Sloan Foundation",
                "url": url,
                "description": desc[:300],
                "source": "Sloan Foundation (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logging.warning(f"Failed to parse Sloan program element: {e}")
            return None


class MozillaGrantsScraper(FoundationScraper):
    """Scrape Mozilla Foundation grants"""

    def __init__(self):
        super().__init__()
        self.url = "https://foundation.mozilla.org/en/what-we-fund/"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape Mozilla grants"""
        print(f"\n🔍 Scraping Mozilla Foundation...")
        grants = []

        try:
            response = self.session.get(self.url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find grant programs
                programs = soup.find_all(['div', 'section'], class_=re.compile(r'program|grant|fund'))

                for prog in programs:
                    grant = self._parse_program(prog)
                    if grant:
                        grants.append(grant)

                if not grants:
                    logging.warning(f"parsed 0 items from {self.url} — selectors may be outdated")

        except Exception as e:
            print(f"  ✗ Error: {e}")

        print(f"  ✓ Scraped {len(grants)} grants from Mozilla")
        return grants[:max_grants]

    def _parse_program(self, element) -> Dict[str, Any]:
        """Parse program"""
        try:
            title_elem = element.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None

            title = self.clean_text(title_elem.text)

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else self.url
            if url and not url.startswith('http'):
                url = f"https://foundation.mozilla.org{url}"

            return {
                "name": title,
                "organization": "Mozilla Foundation",
                "url": url,
                "source": "Mozilla (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logging.warning(f"Failed to parse Mozilla program element: {e}")
            return None


class NLnetScraper(FoundationScraper):
    """Scrape NLnet Foundation calls"""

    def __init__(self):
        super().__init__()
        self.url = "https://nlnet.nl/propose/"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape NLnet calls"""
        print(f"\n🔍 Scraping NLnet Foundation...")
        grants = []

        try:
            response = self.session.get(self.url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find open calls
                calls = soup.find_all(['div', 'section'], class_=re.compile(r'call|theme|program'))

                for call in calls:
                    grant = self._parse_call(call)
                    if grant:
                        grants.append(grant)

                if not grants:
                    logging.warning(f"parsed 0 items from {self.url} — selectors may be outdated")

        except Exception as e:
            print(f"  ✗ Error: {e}")

        print(f"  ✓ Scraped {len(grants)} grants from NLnet")
        return grants[:max_grants]

    def _parse_call(self, element) -> Dict[str, Any]:
        """Parse call"""
        try:
            title_elem = element.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None

            title = self.clean_text(title_elem.text)

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else self.url
            if url and not url.startswith('http'):
                url = f"https://nlnet.nl{url}"

            return {
                "name": f"NLnet - {title}",
                "organization": "NLnet Foundation",
                "url": url,
                "amount": NLNET_TYPICAL_AMOUNT,
                "amount_note": AMOUNT_NOTE,
                "source": "NLnet (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logging.warning(f"Failed to parse NLnet call element: {e}")
            return None


class PrototypeFundScraper(FoundationScraper):
    """Scrape Prototype Fund calls"""

    def __init__(self):
        super().__init__()
        self.url = "https://prototypefund.de/en/"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape Prototype Fund"""
        print(f"\n🔍 Scraping Prototype Fund...")
        grants = []

        try:
            response = self.session.get(self.url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Check for current call
                call_elem = soup.find(['div', 'section'], class_=re.compile(r'call|round|apply'))

                if call_elem:
                    title_elem = call_elem.find(['h1', 'h2', 'h3'])
                    title = self.clean_text(title_elem.text) if title_elem else "Current Call"

                    grants.append({
                        "name": f"Prototype Fund - {title}",
                        "organization": "German Federal Ministry of Education and Research",
                        "url": self.url,
                        "amount": PROTOTYPE_FUND_TYPICAL_AMOUNT,
                        "amount_note": AMOUNT_NOTE,
                        "description": "Funding for public interest technology projects",
                        "source": "Prototype Fund (Web)",
                        "scraped_at": datetime.now().isoformat()
                    })

                if not grants:
                    logging.warning(f"parsed 0 items from {self.url} — selectors may be outdated")

        except Exception as e:
            print(f"  ✗ Error: {e}")

        print(f"  ✓ Scraped {len(grants)} grants from Prototype Fund")
        return grants[:max_grants]


class WellcomeTrustScraper(FoundationScraper):
    """Scrape Wellcome Trust funding"""

    def __init__(self):
        super().__init__()
        self.url = "https://wellcome.org/grant-funding"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape Wellcome funding schemes"""
        print(f"\n🔍 Scraping Wellcome Trust...")
        grants = []

        try:
            response = self.session.get(self.url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find funding schemes
                schemes = soup.find_all(['div', 'article'], class_=re.compile(r'scheme|funding|grant'))

                for scheme in schemes:
                    grant = self._parse_scheme(scheme)
                    if grant:
                        grants.append(grant)

                if not grants:
                    logging.warning(f"parsed 0 items from {self.url} — selectors may be outdated")

        except Exception as e:
            print(f"  ✗ Error: {e}")

        print(f"  ✓ Scraped {len(grants)} grants from Wellcome")
        return grants[:max_grants]

    def _parse_scheme(self, element) -> Dict[str, Any]:
        """Parse funding scheme"""
        try:
            title_elem = element.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None

            title = self.clean_text(title_elem.text)

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else self.url
            if url and not url.startswith('http'):
                url = f"https://wellcome.org{url}"

            return {
                "name": title,
                "organization": "Wellcome Trust",
                "url": url,
                "source": "Wellcome (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logging.warning(f"Failed to parse Wellcome scheme element: {e}")
            return None


class FoundationCollector:
    """Collect grants from all foundations"""

    def __init__(self):
        self.scrapers = {
            'sloan': SloanFoundationScraper(),
            'mozilla': MozillaGrantsScraper(),
            'nlnet': NLnetScraper(),
            'prototype_fund': PrototypeFundScraper(),
            'wellcome': WellcomeTrustScraper()
        }
        self.all_grants = []

    def collect_all(self):
        """Collect from all foundations"""
        print("\n" + "=" * 60)
        print("FOUNDATION GRANT COLLECTION")
        print("=" * 60)

        results = {}

        for name, scraper in self.scrapers.items():
            try:
                grants = scraper.scrape()
                results[name] = grants
                self.all_grants.extend(grants)
            except Exception as e:
                print(f"\n✗ Failed to scrape {name}: {e}")
                results[name] = []

        print(f"\n{'=' * 60}")
        print(f"TOTAL FOUNDATION GRANTS: {len(self.all_grants)}")
        print(f"{'=' * 60}\n")

        return results

    def save_to_json(self, filename):
        """Save to JSON"""
        target = Path(filename)

        # Guard: don't clobber an existing non-empty output file with an empty result
        if len(self.all_grants) == 0 and target.exists():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                if existing.get('total_grants', 0) > 0:
                    logging.warning(
                        f"Scrape returned 0 grants but {target} already contains "
                        f"{existing.get('total_grants')} grants — skipping write to avoid data loss"
                    )
                    return
            except Exception as e:
                logging.warning(f"Could not inspect existing output file {target}: {e}")

        data = {
            "scraped_at": datetime.now().isoformat(),
            "total_grants": len(self.all_grants),
            "grants": self.all_grants
        }

        with open(target, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(self.all_grants)} foundation grants to {target}")


def main():
    """Main function"""
    collector = FoundationCollector()
    results = collector.collect_all()

    collector.save_to_json(ROOT / 'data' / 'grants_foundations.json')

    # Print summary
    print("\n=== FOUNDATION SCRAPING SUMMARY ===")
    for source, grants in results.items():
        print(f"{source}: {len(grants)} grants")
        if grants:
            print(f"  Example: {grants[0].get('name', 'Unknown')[:60]}...")


if __name__ == "__main__":
    main()
