import os
import re
import gzip
import asyncio
from typing import List, Optional, Set, Dict, Any
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
from botasaurus.request import request, Request
from botasaurus.task import task
from botasaurus import bt

try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    aiohttp = None

# Standalone decorated functions for fetching URLs
@request(max_retry=3, output=None)  # output=None prevents saving intermediate results
def fetch_text(req: Request, url):
    """
    Fetch text content from a URL.
    """
    try:
        response = req.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

@request(max_retry=3, output=None)
def fetch_binary(req: Request, url):
    """
    Fetch binary content from a URL (for gzip files).
    """
    try:
        response = req.get(url)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

class SitemapScraper:
    def __init__(
        self,
        base_url: str,
        output_dir: str = "sitemap_data",
        same_host_only: bool = True,
    ) -> None:
        """
        Initialize the sitemap scraper with a base URL.
        
        Args:
            base_url: The base URL of the website
            output_dir: Directory to save downloaded sitemaps
            same_host_only: If True, only process sitemaps and URLs from the same host
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.base_host = urlparse(self.base_url).netloc
        self.same_host_only = same_host_only

        self.processed_sitemaps: Set[str] = set()
        self.all_sitemap_urls: List[str] = []
        self.all_extracted_urls: List[str] = []  # Store all extracted URLs
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Async state initialized lazily in async run
        self._lock: Optional[asyncio.Lock] = None
    
    @staticmethod
    def _dedupe_preserve_order(items: List[str]) -> List[str]:
        seen: Set[str] = set()
        deduped: List[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        return deduped
    
    def _is_same_host(self, url: str) -> bool:
        if not self.same_host_only:
            return True
        parsed = urlparse(url)
        if not parsed.netloc:
            # relative URL considered same host
            return True
        return parsed.netloc == self.base_host
    
    def fetch_robots_txt(self):
        """
        Fetch and parse robots.txt file to find sitemap URLs.
        """
        robots_url = urljoin(self.base_url, '/robots.txt')
        print(f"Fetching robots.txt from: {robots_url}")
        
        content = fetch_text(robots_url)
        
        if content:
            return content
        else:
            print(f"robots.txt not found or empty")
            return None
    
    def parse_sitemaps_from_robots(self, robots_content):
        """
        Extract sitemap URLs from robots.txt content.
        """
        if not robots_content:
            return []
        
        sitemap_urls = []
        sitemap_pattern = re.compile(r'^Sitemap:\s*(.+)$', re.MULTILINE | re.IGNORECASE)
        matches = sitemap_pattern.findall(robots_content)
        
        for match in matches:
            sitemap_url = match.strip()
            if sitemap_url:
                sitemap_urls.append(sitemap_url)
        
        return sitemap_urls
    
    def download_sitemap(self, sitemap_url: str) -> Optional[str]:
        """
        Download a sitemap file (handles both regular XML and .gz compressed files).
        """
        print(f"\nProcessing: {sitemap_url}")
        
        # Always fetch as binary then decide how to decode
        binary_content = fetch_binary(sitemap_url)
        if not binary_content:
            print(f"  ✗ Failed to download sitemap")
            return None

        try:
            # GZIP magic header 1f 8b
            if len(binary_content) >= 2 and binary_content[0] == 0x1F and binary_content[1] == 0x8B:
                decompressed = gzip.decompress(binary_content)
                print("  ✓ Downloaded and decompressed successfully")
                return decompressed.decode('utf-8', errors='replace')
            # Not gzip; decode as UTF-8
            text_content = binary_content.decode('utf-8', errors='replace')
            print("  ✓ Downloaded successfully")
            return text_content
        except Exception as e:
            print(f"  ⚠ Error decoding sitemap content: {e}")
            # As a last resort try text endpoint
            text_fallback = fetch_text(sitemap_url)
            if text_fallback:
                print("  ✓ Fallback text download succeeded")
                return text_fallback
            print("  ✗ Fallback text download failed")
            return None
    
    def save_sitemap(self, sitemap_url, content):
        """
        Save sitemap content to a file.
        """
        if not content:
            return None
        
        # Generate filename from URL
        parsed_url = urlparse(sitemap_url)
        filename = parsed_url.path.replace('/', '_').strip('_')
        if not filename:
            filename = 'sitemap.xml'
        elif not filename.endswith('.xml'):
            filename = filename.replace('.gz', '') + '.xml'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Avoid overwriting by adding a number suffix
        counter = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            base, ext = os.path.splitext(original_filepath)
            filepath = f"{base}_{counter}{ext}"
            counter += 1
        
        # Save the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Saved as: {os.path.basename(filepath)}")
        return filepath
    
    def extract_nested_sitemaps(self, sitemap_content: str) -> List[str]:
        """
        Extract nested sitemap URLs from a sitemap index file.
        """
        if not sitemap_content:
            return []
        
        nested_sitemap_urls: List[str] = []
        try:
            root = ET.fromstring(sitemap_content)
        except Exception as e:
            print(f"  ⚠ Failed to parse XML for nested sitemaps: {e}")
            return []

        # Only treat as sitemapindex when root indicates so
        if not root.tag.lower().endswith('sitemapindex'):
            return []

        for sitemap_element in root:
            if not isinstance(sitemap_element.tag, str):
                continue
            if sitemap_element.tag.lower().endswith('sitemap'):
                for child in sitemap_element:
                    if isinstance(child.tag, str) and child.tag.lower().endswith('loc') and child.text:
                        url = child.text.strip()
                        if url:
                            nested_sitemap_urls.append(url)

        return nested_sitemap_urls
    
    def extract_urls_from_sitemap(self, sitemap_content: str) -> List[str]:
        """
        Extract all URLs from a sitemap XML content.
        """
        if not sitemap_content:
            return []
        
        try:
            root = ET.fromstring(sitemap_content)
        except Exception as e:
            print(f"  ⚠ Failed to parse XML for URL extraction: {e}")
            return []

        # Regular sitemap with <urlset>
        if root.tag.lower().endswith('urlset'):
            urls: List[str] = []
            for url_element in root:
                if not isinstance(url_element.tag, str):
                    continue
                if url_element.tag.lower().endswith('url'):
                    for child in url_element:
                        if isinstance(child.tag, str) and child.tag.lower().endswith('loc') and child.text:
                            url = child.text.strip()
                            if url:
                                urls.append(url)
            return urls
        
        # Not a urlset; likely a sitemap index
        return []
    
    def process_sitemap_recursively(self, sitemap_url: str) -> None:
        """
        Process a sitemap and recursively process any nested sitemaps.
        """
        # Skip if already processed
        if sitemap_url in self.processed_sitemaps:
            print(f"  ⚠ Skipping already processed: {sitemap_url}")
            return
        
        self.processed_sitemaps.add(sitemap_url)
        self.all_sitemap_urls.append(sitemap_url)
        
        # Download the sitemap
        sitemap_content = self.download_sitemap(sitemap_url)
        
        if sitemap_content:
            # Save the sitemap
            self.save_sitemap(sitemap_url, sitemap_content)
            
            # Extract regular URLs from this sitemap
            extracted_urls = self.extract_urls_from_sitemap(sitemap_content)
            if extracted_urls:
                # Normalize to absolute and enforce host policy
                normalized_urls: List[str] = []
                for url in extracted_urls:
                    absolute_url = url if url.startswith('http') else urljoin(self.base_url, url)
                    if self._is_same_host(absolute_url):
                        normalized_urls.append(absolute_url)
                self.all_extracted_urls.extend(normalized_urls)
                print(f"  ✓ Extracted {len(normalized_urls)} URL(s)")
            
            # Check for nested sitemaps
            nested_sitemaps = self.extract_nested_sitemaps(sitemap_content)
            
            if nested_sitemaps:
                print(f"  ➜ Found {len(nested_sitemaps)} nested sitemaps")
                for nested_url in nested_sitemaps:
                    # Make sure URL is absolute
                    if not nested_url.startswith('http'):
                        nested_url = urljoin(self.base_url, nested_url)
                    # Enforce host restriction if enabled
                    if not self._is_same_host(nested_url):
                        continue
                    # Recursively process
                    self.process_sitemap_recursively(nested_url)
    
    def run(self):
        """
        Main method to scrape all sitemaps from a website.
        """
        print(f"\n{'='*60}")
        print(f"Starting sitemap scraper for: {self.base_url}")
        print(f"{'='*60}\n")
        
        # Step 1: Fetch robots.txt
        robots_content = self.fetch_robots_txt()
        
        sitemap_urls = []
        
        if robots_content:
            # Save robots.txt
            robots_path = os.path.join(self.output_dir, 'robots.txt')
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            print(f"Saved robots.txt to: {robots_path}\n")
            
            # Step 2: Parse sitemap URLs from robots.txt
            sitemap_urls = self.parse_sitemaps_from_robots(robots_content)
            
            if sitemap_urls:
                print(f"Found {len(sitemap_urls)} sitemap(s) in robots.txt:")
                for url in sitemap_urls:
                    print(f"  - {url}")
                print()
        
        # If no sitemaps found in robots.txt, try common sitemap locations
        if not sitemap_urls:
            print("No sitemaps found in robots.txt. Trying common locations...")
            common_locations = [
                '/sitemap.xml',
                '/sitemap_index.xml',
                '/sitemap.xml.gz',
                '/sitemaps/sitemap.xml',
                '/sitemap/sitemap.xml'
            ]
            
            for location in common_locations:
                test_url = urljoin(self.base_url, location)
                # Quick check if sitemap exists
                print(f"Checking: {test_url}")
                test_content = self.download_sitemap(test_url)
                if test_content and ('<urlset' in test_content or '<sitemapindex' in test_content):
                    sitemap_urls.append(test_url)
                    print(f"  ✓ Found sitemap at: {test_url}")
                    break
        
        if not sitemap_urls:
            print("No sitemaps found!")
            return {
                "base_url": self.base_url,
                "status": "No sitemaps found",
                "sitemaps_found": [],
                "output_directory": self.output_dir
            }
        
        # Step 3: Process all sitemaps recursively
        print(f"\n{'='*40}")
        print("Processing sitemaps...")
        print(f"{'='*40}\n")
        
        for sitemap_url in sitemap_urls:
            self.process_sitemap_recursively(sitemap_url)
        
        # Remove duplicates from all extracted URLs while preserving order
        all_urls = self._dedupe_preserve_order(self.all_extracted_urls)

        print(f"\n{'='*40}")
        print("URL Extraction Summary")
        print(f"{'='*40}\n")
        print(f"Total unique URLs found: {len(all_urls)}")
        
        # Save all URLs to a file
        if all_urls:
            urls_file = os.path.join(self.output_dir, 'all_urls.txt')
            with open(urls_file, 'w', encoding='utf-8') as f:
                for url in all_urls:
                    f.write(url + '\n')
            print(f"\nSaved {len(all_urls)} unique URLs to: {urls_file}")
            
            # Also save as JSON for easier processing
            bt.write_json({"urls": all_urls, "count": len(all_urls)}, 
                         os.path.join(self.output_dir, 'all_urls'))

        # Summary
        print(f"\n{'='*60}")
        print("SCRAPING COMPLETE!")
        print(f"{'='*60}")
        print(f"Base URL: {self.base_url}")
        print(f"Total sitemaps processed: {len(self.processed_sitemaps)}")
        print(f"Total unique URLs found: {len(all_urls)}")
        print(f"Output directory: {os.path.abspath(self.output_dir)}")
        print(f"{'='*60}\n")
        
        return {
            "base_url": self.base_url,
            "status": "Success",
            "sitemaps_found": list(self.processed_sitemaps),
            "total_sitemaps": len(self.processed_sitemaps),
            "total_urls": len(all_urls),
            "output_directory": os.path.abspath(self.output_dir),
            "files_created": {
                "robots_txt": os.path.join(self.output_dir, 'robots.txt') if robots_content else None,
                "all_urls_txt": os.path.join(self.output_dir, 'all_urls.txt') if all_urls else None,
                "all_urls_json": os.path.join(self.output_dir, 'all_urls.json') if all_urls else None,
                "sitemaps": [f for f in os.listdir(self.output_dir) if f.endswith('.xml')]
            }
        }

    async def _async_fetch_binary(self, session: Any, url: str, *, max_retry: int = 3) -> Optional[bytes]:
        """Fetch binary content with retries."""
        backoff_seconds = 0.5
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SitemapScraper/1.0)"}
        for attempt in range(1, max_retry + 1):
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        print(f"  ⚠ HTTP {resp.status} for {url}")
            except Exception as e:
                print(f"  ⚠ Error fetching {url} (attempt {attempt}/{max_retry}): {e}")
            await asyncio.sleep(backoff_seconds)
            backoff_seconds *= 2
        return None

    async def _async_download_sitemap(self, session: Any, sitemap_url: str) -> Optional[str]:
        print(f"\nProcessing: {sitemap_url}")
        binary_content = await self._async_fetch_binary(session, sitemap_url)
        if not binary_content:
            print("  ✗ Failed to download sitemap")
            return None
        try:
            if len(binary_content) >= 2 and binary_content[0] == 0x1F and binary_content[1] == 0x8B:
                decompressed = gzip.decompress(binary_content)
                print("  ✓ Downloaded and decompressed successfully")
                return decompressed.decode('utf-8', errors='replace')
            text_content = binary_content.decode('utf-8', errors='replace')
            print("  ✓ Downloaded successfully")
            return text_content
        except Exception as e:
            print(f"  ⚠ Error decoding sitemap content: {e}")
            return None

    async def _async_fetch_text(self, session: Any, url: str) -> Optional[str]:
        binary = await self._async_fetch_binary(session, url)
        if binary is None:
            return None
        try:
            return binary.decode('utf-8', errors='replace')
        except Exception:
            return None

    async def run_async(self, concurrency: int = 10) -> Dict:
        if aiohttp is None:
            print("aiohttp not installed; falling back to synchronous run().")
            return self.run()

        print(f"\n{'='*60}")
        print(f"Starting sitemap scraper (async) for: {self.base_url}")
        print(f"{'='*60}\n")

        self._lock = asyncio.Lock()

        sitemap_urls: List[str] = []
        robots_content: Optional[str] = None

        async with aiohttp.ClientSession() as session:
            # Step 1: Fetch robots.txt
            robots_url = urljoin(self.base_url, '/robots.txt')
            print(f"Fetching robots.txt from: {robots_url}")
            robots_content = await self._async_fetch_text(session, robots_url)

            if robots_content:
                robots_path = os.path.join(self.output_dir, 'robots.txt')
                with open(robots_path, 'w', encoding='utf-8') as f:
                    f.write(robots_content)
                print(f"Saved robots.txt to: {robots_path}\n")

                sitemap_urls = self.parse_sitemaps_from_robots(robots_content)
                if sitemap_urls:
                    print(f"Found {len(sitemap_urls)} sitemap(s) in robots.txt:")
                    for url in sitemap_urls:
                        print(f"  - {url}")
                    print()

            # Step 2: Try common locations in parallel if none found
            if not sitemap_urls:
                print("No sitemaps found in robots.txt. Trying common locations...")
                common_locations = [
                    '/sitemap.xml',
                    '/sitemap_index.xml',
                    '/sitemap.xml.gz',
                    '/sitemaps/sitemap.xml',
                    '/sitemap/sitemap.xml'
                ]
                test_urls = [urljoin(self.base_url, loc) for loc in common_locations]
                print("Checking:")
                for u in test_urls:
                    print(f"  - {u}")

                tasks = [self._async_download_sitemap(session, u) for u in test_urls]
                results = await asyncio.gather(*tasks)
                for u, content in zip(test_urls, results):
                    if content and ('<urlset' in content.lower() or '<sitemapindex' in content.lower()):
                        sitemap_urls.append(u)
                        print(f"  ✓ Found sitemap at: {u}")
                        break

            if not sitemap_urls:
                print("No sitemaps found!")
                return {
                    "base_url": self.base_url,
                    "status": "No sitemaps found",
                    "sitemaps_found": [],
                    "output_directory": self.output_dir
                }

            # Step 3: Process all sitemaps with a worker pool
            print(f"\n{'='*40}")
            print("Processing sitemaps (async)...")
            print(f"{'='*40}\n")

            queue: asyncio.Queue[str] = asyncio.Queue()
            for u in sitemap_urls:
                await queue.put(u)

            async def worker() -> None:
                while True:
                    try:
                        url = await queue.get()
                    except Exception:
                        return
                    # Deduplicate with lock
                    async with self._lock:  # type: ignore[arg-type]
                        if url in self.processed_sitemaps:
                            queue.task_done()
                            continue
                        self.processed_sitemaps.add(url)
                        self.all_sitemap_urls.append(url)

                    content = await self._async_download_sitemap(session, url)
                    if not content:
                        queue.task_done()
                        continue

                    # Save sitemap
                    self.save_sitemap(url, content)

                    # Extract URLs
                    extracted = self.extract_urls_from_sitemap(content)
                    if extracted:
                        normalized: List[str] = []
                        for href in extracted:
                            absolute = href if href.startswith('http') else urljoin(self.base_url, href)
                            if self._is_same_host(absolute):
                                normalized.append(absolute)
                        async with self._lock:  # type: ignore[arg-type]
                            self.all_extracted_urls.extend(normalized)
                        print(f"  ✓ Extracted {len(normalized)} URL(s)")

                    # Enqueue nested sitemaps
                    nested = self.extract_nested_sitemaps(content)
                    for nested_url in nested:
                        if not nested_url.startswith('http'):
                            nested_url = urljoin(self.base_url, nested_url)
                        if not self._is_same_host(nested_url):
                            continue
                        await queue.put(nested_url)

                    queue.task_done()

            workers = [asyncio.create_task(worker()) for _ in range(max(1, concurrency))]
            await queue.join()
            for w in workers:
                w.cancel()
            # swallow cancellation exceptions
            await asyncio.gather(*workers, return_exceptions=True)

        # Finish and summarize using the synchronous summarization path
        # Reuse the end of run() to avoid duplication — mimic it here
        all_urls = self._dedupe_preserve_order(self.all_extracted_urls)

        print(f"\n{'='*40}")
        print("URL Extraction Summary")
        print(f"{'='*40}\n")
        print(f"Total unique URLs found: {len(all_urls)}")

        if all_urls:
            urls_file = os.path.join(self.output_dir, 'all_urls.txt')
            with open(urls_file, 'w', encoding='utf-8') as f:
                for url in all_urls:
                    f.write(url + '\n')
            print(f"\nSaved {len(all_urls)} unique URLs to: {urls_file}")

            bt.write_json({"urls": all_urls, "count": len(all_urls)}, os.path.join(self.output_dir, 'all_urls'))

        print(f"\n{'='*60}")
        print("SCRAPING COMPLETE!")
        print(f"{'='*60}")
        print(f"Base URL: {self.base_url}")
        print(f"Total sitemaps processed: {len(self.processed_sitemaps)}")
        print(f"Total unique URLs found: {len(all_urls)}")
        print(f"Output directory: {os.path.abspath(self.output_dir)}")
        print(f"{'='*60}\n")

        return {
            "base_url": self.base_url,
            "status": "Success",
            "sitemaps_found": list(self.processed_sitemaps),
            "total_sitemaps": len(self.processed_sitemaps),
            "total_urls": len(all_urls),
            "output_directory": os.path.abspath(self.output_dir),
            "files_created": {
                "robots_txt": os.path.join(self.output_dir, 'robots.txt') if robots_content else None,
                "all_urls_txt": os.path.join(self.output_dir, 'all_urls.txt') if all_urls else None,
                "all_urls_json": os.path.join(self.output_dir, 'all_urls.json') if all_urls else None,
                "sitemaps": [f for f in os.listdir(self.output_dir) if f.endswith('.xml')]
            }
        }
        
        print(f"\n{'='*40}")
        print("URL Extraction Summary")
        print(f"{'='*40}\n")
        print(f"Total unique URLs found: {len(all_urls)}")
        
        # Save all URLs to a file
        if all_urls:
            urls_file = os.path.join(self.output_dir, 'all_urls.txt')
            with open(urls_file, 'w', encoding='utf-8') as f:
                for url in all_urls:
                    f.write(url + '\n')
            print(f"\nSaved {len(all_urls)} unique URLs to: {urls_file}")
            
            # Also save as JSON for easier processing
            bt.write_json({"urls": all_urls, "count": len(all_urls)}, 
                         os.path.join(self.output_dir, 'all_urls'))
        
        # Summary
        print(f"\n{'='*60}")
        print("SCRAPING COMPLETE!")
        print(f"{'='*60}")
        print(f"Base URL: {self.base_url}")
        print(f"Total sitemaps processed: {len(self.processed_sitemaps)}")
        print(f"Total unique URLs found: {len(all_urls)}")
        print(f"Output directory: {os.path.abspath(self.output_dir)}")
        print(f"{'='*60}\n")
        
        return {
            "base_url": self.base_url,
            "status": "Success",
            "sitemaps_found": list(self.processed_sitemaps),
            "total_sitemaps": len(self.processed_sitemaps),
            "total_urls": len(all_urls),
            "output_directory": os.path.abspath(self.output_dir),
            "files_created": {
                "robots_txt": os.path.join(self.output_dir, 'robots.txt') if robots_content else None,
                "all_urls_txt": os.path.join(self.output_dir, 'all_urls.txt') if all_urls else None,
                "all_urls_json": os.path.join(self.output_dir, 'all_urls.json') if all_urls else None,
                "sitemaps": [f for f in os.listdir(self.output_dir) if f.endswith('.xml')]
            }
        }

# Wrapper function with task decorator for the main execution
@task(output="sitemap_analysis")
def scrape_sitemaps(data=None):
    """
    Task wrapper for the sitemap scraper.
    """
    # Initialize variables with defaults
    base_url = "https://www.target.com.au"  # Default URL
    output_dir = 'sitemap_data'
    same_host_only = True
    use_async = False
    concurrency = 10
    
    # Get the base URL from data or use default
    if isinstance(data, dict) and 'url' in data:
        base_url = data['url']
        output_dir = data.get('output_dir', 'sitemap_data')
        same_host_only = bool(data.get('same_host_only', True))
        use_async = bool(data.get('use_async', False))
        concurrency = int(data.get('concurrency', 10))
    elif isinstance(data, str):
        base_url = data
    
    # Create and run scraper
    scraper = SitemapScraper(base_url, output_dir, same_host_only=same_host_only)
    if use_async:
        try:
            return asyncio.run(scraper.run_async(concurrency=concurrency))
        except RuntimeError:
            # In case we're already in an event loop (e.g., Jupyter), fall back to nest_asyncio-like pattern
            return scraper.run()
    else:
        return scraper.run()


# Main execution
if __name__ == "__main__":
    # Example usage - you can pass URL in different ways:
    
    # Option 1: Direct URL string
    # result = scrape_sitemaps("https://www.asos.com")
    result = scrape_sitemaps({"url": "https://www.asos.com", "use_async": True, "concurrency": 20})
    
    # Option 2: Dictionary with URL and custom output directory
    # result = scrape_sitemaps({"url": "https://www.bcf.com.au", "output_dir": "bcf_sitemaps"})
    
    # Option 3: Use default (will use BCF)
    # result = scrape_sitemaps()
    
    # The result is automatically saved to output/sitemap_analysis.json
    print("\nResults saved to output/sitemap_analysis.json")