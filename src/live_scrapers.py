#!/usr/bin/env python3
"""
Live Grant Scrapers - Actually scrape and fetch real grant data from websites and APIs
"""

import html
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Repository root (this file lives in <root>/src/), so output paths work
# regardless of the current working directory.
ROOT = Path(__file__).resolve().parent.parent


class GrantScraper:
    """Base class for grant scrapers"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape grants - to be implemented by subclasses"""
        raise NotImplementedError

    def clean_text(self, text: str) -> str:
        """Clean scraped text (unescape HTML entities, collapse whitespace)"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', html.unescape(text)).strip()


class GrantsGovScraper(GrantScraper):
    """Scrape Grants.gov for active opportunities"""

    def __init__(self):
        super().__init__()
        self.search_url = "https://www.grants.gov/search-grants"
        self.api_url = "https://apply07.grants.gov/grantsws/rest/opportunities/search"

    def scrape(self, max_grants: int = 100) -> List[Dict[str, Any]]:
        """Scrape active grants from Grants.gov"""
        print(f"\n🔍 Scraping Grants.gov...")
        grants = []

        try:
            # Use the REST API endpoint
            # Note: This is a public search endpoint
            payload = {
                "oppStatuses": "forecasted|posted",
                "sortBy": "openDate|desc",
                "rows": max_grants,
                "startRecordNum": 0
            }

            print(f"  → Fetching from API: {self.api_url}")
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Parse opportunities
                opps = data.get('oppHits', [])
                print(f"  ✓ Found {len(opps)} opportunities")

                skipped = 0
                for opp in opps[:max_grants]:
                    grant = self._parse_opportunity(opp)
                    if grant:
                        grants.append(grant)
                    else:
                        skipped += 1
                if skipped:
                    logger.warning(
                        "Grants.gov: skipped %d invalid/unparseable opportunities",
                        skipped
                    )

            else:
                logger.warning(
                    "Grants.gov API returned HTTP %d", response.status_code
                )
                # Fallback: Try scraping the website
                grants = self._scrape_website(max_grants)

        except Exception as e:
            logger.warning("Grants.gov API error: %s", e)
            # Try scraping as fallback
            try:
                grants = self._scrape_website(max_grants)
            except Exception as e:
                logger.warning("Grants.gov website fallback failed: %s", e)

        print(f"  ✓ Scraped {len(grants)} grants from Grants.gov")
        return grants

    def _parse_opportunity(self, opp: Dict) -> Dict[str, Any]:
        """Parse opportunity from the search API response.

        Note: the search API's oppHits only contain id, number, title,
        agencyCode, agency, openDate, closeDate, oppStatus, docType and
        cfdaList. Richer fields (description, award floor/ceiling,
        eligibility) require a per-opportunity detail fetch and are NOT
        available here, so we use honest placeholder values instead.

        Detail-page URLs on grants.gov are keyed by the numeric
        opportunity id, not the FOA number.
        """
        try:
            title = self.clean_text(opp.get('title') or '')
            opp_id = opp.get('id')
            if not title or not opp_id:
                # Records without a title or id produce empty names and
                # broken URLs downstream; skip them.
                return None

            number = opp.get('number', '')
            agency = self.clean_text(opp.get('agency') or 'Federal Government')

            return {
                "name": title,
                "organization": agency,
                "url": f"https://www.grants.gov/search-results-detail/{opp_id}",
                "opportunity_number": number,
                "amount": "See grant page",
                "deadline": opp.get('closeDate') or 'See website',
                "description": "See grant page",
                "category": opp.get('cfdaList', []),
                "agency_code": opp.get('agencyCode', ''),
                "posted_date": opp.get('openDate', ''),
                "source": "Grants.gov (API)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning("Grants.gov: error parsing opportunity: %s", e)
            return None

    def _scrape_website(self, max_grants: int) -> List[Dict[str, Any]]:
        """Fallback: Scrape the website directly"""
        print(f"  → Attempting to scrape website...")
        grants = []

        try:
            response = self.session.get(
                "https://www.grants.gov/search-results",
                params={'oppStatuses': 'posted'},
                timeout=30
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find grant listings
                grant_items = soup.find_all('div', class_=re.compile(r'opportunity|grant'))

                skipped = 0
                for item in grant_items[:max_grants]:
                    grant = self._parse_html_grant(item)
                    if grant:
                        grants.append(grant)
                    else:
                        skipped += 1
                if skipped:
                    logger.warning(
                        "Grants.gov (Web): skipped %d unparseable listings",
                        skipped
                    )

        except Exception as e:
            logger.warning("Grants.gov website scraping failed: %s", e)

        return grants

    def _parse_html_grant(self, element) -> Dict[str, Any]:
        """Parse grant from HTML element"""
        try:
            title_elem = element.find(['h3', 'h4', 'a'])
            title = self.clean_text(title_elem.text) if title_elem else "Unknown"

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else ""
            if url and not url.startswith('http'):
                url = f"https://www.grants.gov{url}"

            return {
                "name": title,
                "organization": "Federal Government",
                "url": url,
                "source": "Grants.gov (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning("Grants.gov: error parsing HTML grant: %s", e)
            return None


class NSFScraper(GrantScraper):
    """Scrape NSF funding opportunities"""

    def __init__(self):
        super().__init__()
        self.funding_url = "https://www.nsf.gov/funding/opportunities"
        self.rss_url = "https://www.nsf.gov/rss/rss_www_funding.xml"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape NSF opportunities"""
        print(f"\n🔍 Scraping NSF...")
        grants = []

        # Try RSS feed first
        grants = self._scrape_rss()

        # Then try scraping the main page for more details
        if len(grants) < max_grants:
            web_grants = self._scrape_website()
            grants.extend(web_grants)

        # Remove duplicates by URL
        seen_urls = set()
        unique_grants = []
        for grant in grants:
            url = grant.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_grants.append(grant)

        print(f"  ✓ Scraped {len(unique_grants)} grants from NSF")
        return unique_grants[:max_grants]

    def _scrape_rss(self) -> List[Dict[str, Any]]:
        """Scrape NSF RSS feed"""
        grants = []

        try:
            response = self.session.get(self.rss_url, timeout=30)
            if response.status_code == 200:
                root = ET.fromstring(response.content)

                skipped = 0
                for item in root.findall('.//item'):
                    grant = self._parse_rss_item(item)
                    if grant:
                        grants.append(grant)
                    else:
                        skipped += 1
                if skipped:
                    logger.warning("NSF (RSS): skipped %d unparseable items", skipped)

                print(f"  ✓ Parsed {len(grants)} from RSS")
            else:
                logger.warning("NSF RSS feed returned HTTP %d", response.status_code)
        except Exception as e:
            logger.warning("NSF RSS scraping error: %s", e)

        return grants

    def _parse_rss_item(self, item) -> Dict[str, Any]:
        """Parse RSS item"""
        try:
            title = item.find('title')
            link = item.find('link')
            desc = item.find('description')

            if title is not None and link is not None:
                return {
                    "name": self.clean_text(title.text),
                    "organization": "National Science Foundation",
                    "url": link.text,
                    "description": self.clean_text(desc.text) if desc is not None else "",
                    "source": "NSF (RSS)",
                    "scraped_at": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning("NSF: error parsing RSS item: %s", e)
        return None

    def _scrape_website(self) -> List[Dict[str, Any]]:
        """Scrape NSF funding page"""
        grants = []

        try:
            response = self.session.get(self.funding_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find funding opportunities
                opps = soup.find_all(['div', 'article'], class_=re.compile(r'funding|opportunity|program'))

                skipped = 0
                for opp in opps:
                    grant = self._parse_html_opportunity(opp)
                    if grant:
                        grants.append(grant)
                    else:
                        skipped += 1
                if skipped:
                    logger.warning("NSF (Web): skipped %d unparseable listings", skipped)

                print(f"  ✓ Scraped {len(grants)} from website")
        except Exception as e:
            logger.warning("NSF website scraping error: %s", e)

        return grants

    def _parse_html_opportunity(self, element) -> Dict[str, Any]:
        """Parse opportunity from HTML"""
        try:
            title_elem = element.find(['h2', 'h3', 'h4', 'a'])
            if not title_elem:
                return None

            title = self.clean_text(title_elem.text)

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else ""
            if url and not url.startswith('http'):
                url = f"https://www.nsf.gov{url}"

            desc_elem = element.find('p')
            desc = self.clean_text(desc_elem.text) if desc_elem else ""

            return {
                "name": title,
                "organization": "National Science Foundation",
                "url": url,
                "description": desc[:300],
                "source": "NSF (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning("NSF: error parsing HTML opportunity: %s", e)
            return None


class EUFundingScraper(GrantScraper):
    """Scrape EU Funding & Tenders Portal"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape EU opportunities"""
        print(f"\n🔍 Scraping EU Funding & Tenders Portal...")
        grants = []

        try:
            response = self.session.get(self.base_url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find call listings
                calls = soup.find_all(['div', 'article'], class_=re.compile(r'call|opportunity'))

                skipped = 0
                for call in calls[:max_grants]:
                    grant = self._parse_call(call)
                    if grant:
                        grants.append(grant)
                    else:
                        skipped += 1
                if skipped:
                    logger.warning("EU Portal: skipped %d unparseable calls", skipped)

            else:
                logger.warning("EU Portal returned HTTP %d", response.status_code)

        except Exception as e:
            logger.warning("EU Portal scraping error: %s", e)

        print(f"  ✓ Scraped {len(grants)} grants from EU Portal")
        return grants

    def _parse_call(self, element) -> Dict[str, Any]:
        """Parse call from HTML"""
        try:
            title_elem = element.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None

            title = self.clean_text(title_elem.text)

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else ""
            if url and not url.startswith('http'):
                url = f"https://ec.europa.eu{url}"

            return {
                "name": title,
                "organization": "European Commission",
                "url": url,
                "source": "EU Portal (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning("EU Portal: error parsing call: %s", e)
            return None


class NIHScraper(GrantScraper):
    """Scrape NIH funding opportunities"""

    def __init__(self):
        super().__init__()
        self.funding_url = "https://grants.nih.gov/funding/searchguide/index.html"
        # The old searchguide XML URL returns HTTP 403; use the NIH Guide
        # funding-opportunities newsfeed instead.
        self.guide_url = "https://grants.nih.gov/grants/guide/newsfeed/fundingopps.xml"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape NIH opportunities"""
        print(f"\n🔍 Scraping NIH...")
        grants = []

        # Try XML feed
        try:
            response = self.session.get(
                self.guide_url,
                headers={
                    'User-Agent': (
                        'awesome-grants scraper '
                        '(+https://yueyuel.github.io/awesome-grants/)'
                    )
                },
                timeout=30
            )
            if response.status_code == 200:
                root = ET.fromstring(response.content)

                skipped = 0
                for item in root.findall('.//item')[:max_grants]:
                    grant = self._parse_xml_item(item)
                    if grant:
                        grants.append(grant)
                    else:
                        skipped += 1
                if skipped:
                    logger.warning("NIH: skipped %d unparseable feed items", skipped)

                print(f"  ✓ Parsed {len(grants)} from XML feed")
            else:
                logger.warning(
                    "NIH funding-opportunities feed returned HTTP %d",
                    response.status_code
                )
        except Exception as e:
            logger.warning("NIH feed error: %s", e)

        print(f"  ✓ Scraped {len(grants)} grants from NIH")
        return grants

    def _parse_xml_item(self, item) -> Dict[str, Any]:
        """Parse XML item"""
        try:
            title = item.find('title')
            link = item.find('link')
            desc = item.find('description')

            if title is not None and link is not None:
                return {
                    "name": self.clean_text(title.text),
                    "organization": "National Institutes of Health",
                    "url": link.text,
                    "description": self.clean_text(desc.text) if desc is not None else "",
                    "source": "NIH (XML)",
                    "scraped_at": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning("NIH: error parsing XML item: %s", e)
        return None


class UKRIScraper(GrantScraper):
    """Scrape UKRI funding opportunities"""

    def __init__(self):
        super().__init__()
        self.funding_url = "https://www.ukri.org/opportunity"

    def scrape(self, max_grants: int = 50) -> List[Dict[str, Any]]:
        """Scrape UKRI opportunities"""
        print(f"\n🔍 Scraping UKRI...")
        grants = []

        try:
            response = self.session.get(self.funding_url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find opportunity listings
                opps = soup.find_all(['div', 'article'], class_=re.compile(r'opportunity|funding'))

                skipped = 0
                for opp in opps[:max_grants]:
                    grant = self._parse_opportunity(opp)
                    if grant:
                        grants.append(grant)
                    else:
                        skipped += 1
                if skipped:
                    logger.warning("UKRI: skipped %d unparseable listings", skipped)

            else:
                logger.warning("UKRI returned HTTP %d", response.status_code)

        except Exception as e:
            logger.warning("UKRI scraping error: %s", e)

        print(f"  ✓ Scraped {len(grants)} grants from UKRI")
        return grants

    def _parse_opportunity(self, element) -> Dict[str, Any]:
        """Parse opportunity from HTML"""
        try:
            title_elem = element.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None

            title = self.clean_text(title_elem.text)

            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else ""
            if url and not url.startswith('http'):
                url = f"https://www.ukri.org{url}"

            return {
                "name": title,
                "organization": "UK Research and Innovation",
                "url": url,
                "source": "UKRI (Web)",
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning("UKRI: error parsing opportunity: %s", e)
            return None


class LiveGrantCollector:
    """Collects grants from all live scrapers"""

    def __init__(self):
        self.scrapers = {
            'grants_gov': GrantsGovScraper(),
            'nsf': NSFScraper(),
            'nih': NIHScraper(),
            'eu_funding': EUFundingScraper(),
            'ukri': UKRIScraper()
        }
        self.all_grants = []

    def collect_all(self, sources: List[str] = None, max_per_source: int = 50):
        """Collect from all sources"""
        if sources is None:
            sources = list(self.scrapers.keys())

        print("=" * 60)
        print("LIVE GRANT COLLECTION - WEB SCRAPING")
        print("=" * 60)

        results = {}

        for source in sources:
            if source in self.scrapers:
                try:
                    grants = self.scrapers[source].scrape(max_grants=max_per_source)
                    results[source] = grants
                    self.all_grants.extend(grants)
                    time.sleep(1)  # Be polite, don't hammer servers
                except Exception as e:
                    print(f"\n✗ Failed to scrape {source}: {e}")
                    results[source] = []

        print(f"\n{'=' * 60}")
        print(f"TOTAL SCRAPED: {len(self.all_grants)} grants")
        print(f"{'=' * 60}\n")

        return results

    def save_to_json(self, filename):
        """Save scraped grants to JSON"""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "scraped_at": datetime.now().isoformat(),
            "total_grants": len(self.all_grants),
            "grants": self.all_grants
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(self.all_grants)} scraped grants to {path}")


def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )

    collector = LiveGrantCollector()

    # Scrape from all sources
    results = collector.collect_all(
        sources=['grants_gov', 'nsf', 'nih'],  # Start with these
        max_per_source=50
    )

    # Save to file (anchored to the repository root, independent of CWD)
    collector.save_to_json(ROOT / 'data' / 'grants_scraped_live.json')

    # Print summary
    print("\n=== SCRAPING SUMMARY ===")
    for source, grants in results.items():
        print(f"{source}: {len(grants)} grants")
        if grants:
            print(f"  Example: {grants[0].get('name', 'Unknown')[:60]}...")


if __name__ == "__main__":
    main()
