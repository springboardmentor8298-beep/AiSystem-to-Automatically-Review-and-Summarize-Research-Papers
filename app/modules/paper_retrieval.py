import requests
import aiohttp
import asyncio
from typing import List, Optional
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from app.config import Config
from app.models.paper import Paper, SearchQuery

class PaperRetrievalModule:
    def __init__(self):
        self.api_base = Config.SEMANTIC_SCHOLAR_API
        self.max_papers = Config.MAX_PAPERS
        self.api_key = Config.S2_API_KEY
        self.cache_file = "storage/downloaded_papers_cache.json"
        self.downloaded_papers_cache = self._load_cache()
        
        # Rate limiting tracking - Conservative settings for public API
        self.last_request_time = None
        self.min_interval_seconds = 3.0  # 3 seconds between requests
        self.request_times = []  # Track recent request times for minute limit
        self.max_requests_per_minute = 10  # Conservative limit
        
    def _load_cache(self) -> dict:
        """Load the cache of downloaded papers"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save the cache of downloaded papers"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.downloaded_papers_cache, f, indent=2)
    
    def _is_paper_downloaded(self, paper_id: str) -> bool:
        """Check if a paper is already downloaded"""
        if paper_id in self.downloaded_papers_cache:
            # Verify the file still exists
            if os.path.exists(self.downloaded_papers_cache[paper_id]['local_path']):
                return True
            else:
                # Remove from cache if file missing
                del self.downloaded_papers_cache[paper_id]
                self._save_cache()
        return False
    
    def _get_cached_paper(self, paper_id: str) -> Optional[str]:
        """Get cached paper path if exists"""
        if self._is_paper_downloaded(paper_id):
            return self.downloaded_papers_cache[paper_id]['local_path']
        return None
    
    async def _wait_for_rate_limit(self):
        """Ensure we never exceed rate limits with sliding window"""
        now = datetime.now()
        
        # Clean up old request times (older than 60 seconds)
        self.request_times = [t for t in self.request_times if (now - t).total_seconds() < 60]
        
        # Check per-minute limit
        if len(self.request_times) >= self.max_requests_per_minute:
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest).total_seconds()
            if wait_time > 0:
                print(f"⏳ Minute rate limit reached ({self.max_requests_per_minute} requests/min). Waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
                return await self._wait_for_rate_limit()
        
        # Check per-request delay
        if self.last_request_time:
            elapsed = (now - self.last_request_time).total_seconds()
            if elapsed < self.min_interval_seconds:
                wait_time = self.min_interval_seconds - elapsed
                print(f"⏳ Rate limit: waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.last_request_time = datetime.now()
        self.request_times.append(self.last_request_time)
    
    def _get_headers(self):
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Paper-Review-System/1.0"
        }
        return headers
    
    async def search_papers_arxiv(self, query: SearchQuery, retry_count: int = 0) -> List[Paper]:
        """Search arXiv for papers (100% open access with PDFs)"""
        
        max_retries = 3
        
        await self._wait_for_rate_limit()
        
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query.topic}",
            "max_results": query.max_papers,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        print(f"🔍 Searching arXiv for: {query.topic}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    print(f"📡 arXiv Response: {response.status}")
                    
                    if response.status == 200:
                        text = await response.text()
                        papers = []
                        
                        # Parse XML response
                        root = ET.fromstring(text)
                        
                        # XML namespace
                        ns = {'atom': 'http://www.w3.org/2005/Atom'}
                        
                        for entry in root.findall('atom:entry', ns):
                            # Extract title
                            title_elem = entry.find('atom:title', ns)
                            title = title_elem.text if title_elem is not None else "No title"
                            title = title.replace('\n', ' ').strip()
                            
                            # Extract authors
                            authors = []
                            for author in entry.findall('atom:author', ns):
                                name = author.find('atom:name', ns)
                                if name is not None and name.text:
                                    authors.append(name.text)
                            
                            # Extract abstract
                            summary_elem = entry.find('atom:summary', ns)
                            abstract = summary_elem.text if summary_elem is not None else "Abstract not available"
                            abstract = abstract.replace('\n', ' ').strip()
                            
                            # Extract PDF URL (arXiv provides PDF)
                            pdf_url = None
                            for link in entry.findall('atom:link', ns):
                                if link.get('title') == 'pdf' or link.get('type') == 'application/pdf':
                                    pdf_url = link.get('href')
                                    break
                            
                            # If no PDF link found, try alternate link
                            if not pdf_url:
                                for link in entry.findall('atom:link', ns):
                                    if link.get('rel') == 'alternate':
                                        pdf_url = link.get('href').replace('abs', 'pdf')
                                        break
                            
                            # Extract year from published date
                            year = 2024
                            published_elem = entry.find('atom:published', ns)
                            if published_elem is not None and published_elem.text:
                                try:
                                    year = int(published_elem.text[:4])
                                except:
                                    pass
                            
                            # Extract paper ID from arXiv URL
                            arxiv_id = None
                            for link in entry.findall('atom:link', ns):
                                if link.get('rel') == 'alternate':
                                    url_parts = link.get('href', '').split('/')
                                    if url_parts:
                                        arxiv_id = url_parts[-1]
                                    break
                            
                            if not arxiv_id:
                                arxiv_id = title[:50]
                            
                            paper = Paper(
                                paper_id=arxiv_id,
                                title=title,
                                authors=authors,
                                abstract=abstract[:5000],
                                year=year,
                                venue="arXiv",
                                citation_count=0,
                                pdf_url=pdf_url
                            )
                            papers.append(paper)
                        
                        print(f"📚 Found {len(papers)} papers from arXiv (all have PDFs)")
                        return papers[:self.max_papers]
                        
                    elif response.status == 429 and retry_count < max_retries:
                        wait_time = (2 ** retry_count) * 10  # 10, 20, 40 seconds
                        print(f"❌ arXiv rate limit (429). Waiting {wait_time} seconds before retry {retry_count + 1}/{max_retries}...")
                        await asyncio.sleep(wait_time)
                        return await self.search_papers_arxiv(query, retry_count + 1)
                        
                    elif response.status == 503 and retry_count < max_retries:
                        wait_time = 5
                        print(f"❌ arXiv service unavailable (503). Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        return await self.search_papers_arxiv(query, retry_count + 1)
                    else:
                        print(f"❌ arXiv error: {response.status}")
                        return []
                        
            except asyncio.TimeoutError:
                print(f"❌ arXiv timeout - server slow, skipping...")
                return []
            except Exception as e:
                print(f"❌ arXiv search error: {e}")
                return []
    
    async def search_papers_openalex(self, query: SearchQuery, retry_count: int = 0) -> List[Paper]:
        """Search for open access papers using OpenAlex API (PDFs only)"""
        
        max_retries = 2
        
        await self._wait_for_rate_limit()
        
        url = "https://api.openalex.org/works"
        
        # Build search query - only open access papers with PDFs
        params = {
            "search": query.topic,
            "per-page": self.max_papers * 2,
            "sort": "relevance_score:desc",
            "filter": "open_access.is_oa:true",  # Only open access papers
        }
        
        # Add email for better rate limits
        params["mailto"] = "323114611038@andhrauniversity.edu.in"
        
        # Add year filter if specified
        if query.year_from:
            params["filter"] = f"publication_year:>{query.year_from-1},open_access.is_oa:true"
        
        print(f"🔍 Searching OpenAlex for: {query.topic} (open access only)")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    print(f"📡 OpenAlex Response: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        papers = []
                        
                        for result in data.get("results", []):
                            # Extract authors
                            authors = []
                            for authorship in result.get("authorships", [])[:5]:
                                author = authorship.get("author", {})
                                authors.append(author.get("display_name", "Unknown"))
                            
                            # Extract PDF URL
                            pdf_url = None
                            for oa_location in result.get("open_access", {}).get("oa_locations", []):
                                if oa_location.get("url"):
                                    pdf_url = oa_location.get("url")
                                    break
                            
                            # Check best_oa_location as fallback
                            if not pdf_url:
                                best_oa = result.get("open_access", {}).get("best_oa_location")
                                if best_oa and best_oa.get("url"):
                                    pdf_url = best_oa.get("url")
                            
                            # Only add if PDF URL exists
                            if pdf_url:
                                paper = Paper(
                                    paper_id=result["id"].split("/")[-1],
                                    title=result.get("title", "No title"),
                                    authors=authors,
                                    abstract=result.get("abstract", "Abstract not available") or "Abstract not available",
                                    year=result.get("publication_year", 0),
                                    venue=result.get("host_venue", {}).get("display_name", ""),
                                    citation_count=result.get("cited_by_count", 0),
                                    pdf_url=pdf_url
                                )
                                papers.append(paper)
                            
                            # Stop if we have enough papers
                            if len(papers) >= self.max_papers:
                                break
                        
                        print(f"📚 Found {len(papers)} open access papers from OpenAlex")
                        return papers[:self.max_papers]
                        
                    elif response.status == 429 and retry_count < max_retries:
                        wait_time = (2 ** retry_count) * 5  # 5, 10 seconds
                        print(f"❌ OpenAlex rate limit (429). Waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)
                        return await self.search_papers_openalex(query, retry_count + 1)
                    else:
                        print(f"❌ OpenAlex error: {response.status}")
                        return []
                        
            except asyncio.TimeoutError:
                print(f"❌ OpenAlex timeout - server slow, skipping...")
                return []
            except Exception as e:
                print(f"❌ OpenAlex search error: {e}")
                return []
    
    async def search_papers(self, query: SearchQuery) -> List[Paper]:
        """Search for papers - try arXiv first (100% PDFs), then OpenAlex"""
        
        print("📚 Searching for open access papers...")
        print("⏳ Note: API rate limits may cause delays. Please be patient.")
        
        # Try arXiv first (all papers have PDFs)
        print("📚 Using arXiv API for paper search (100% open access)...")
        papers = await self.search_papers_arxiv(query)
        
        if papers:
            print("✅ Successfully retrieved papers with PDFs from arXiv")
            return papers
        
        # If arXiv fails, try OpenAlex (open access only)
        print("⚠️ arXiv rate limited or unavailable, trying OpenAlex...")
        papers = await self.search_papers_openalex(query)
        
        if papers:
            print("✅ Successfully retrieved open access papers from OpenAlex")
            return papers
        
        # If no papers found
        print("❌ No open access papers found for this topic.")
        print("💡 Try these topics instead: 'machine learning', 'deep learning', 'artificial intelligence'")
        print("💡 Or wait a few minutes for rate limits to reset.")
        return []
    
    async def download_pdf(self, paper: Paper, retry_count: int = 0) -> str:
        """Download PDF only if not already cached (with rate limiting and retry logic)"""
        
        max_retries = 3
        
        # Check cache first
        if paper.local_pdf_path and os.path.exists(paper.local_pdf_path):
            print(f"📁 Using existing PDF: {paper.title}")
            return paper.local_pdf_path
        
        # Check if already downloaded
        cached_path = self._get_cached_paper(paper.paper_id)
        if cached_path:
            paper.local_pdf_path = cached_path
            print(f"📁 Using cached PDF: {paper.title}")
            return cached_path
        
        # Download only if not cached
        if not paper.pdf_url:
            print(f"⚠️ No PDF URL available for: {paper.title}")
            return None
        
        # Wait for rate limit before downloading
        await self._wait_for_rate_limit()
        
        os.makedirs(Config.PDF_STORAGE, exist_ok=True)
        filepath = f"{Config.PDF_STORAGE}/{paper.paper_id}.pdf"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(paper.pdf_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        with open(filepath, 'wb') as f:
                            f.write(await response.read())
                        paper.local_pdf_path = filepath
                        
                        # Save to cache
                        self.downloaded_papers_cache[paper.paper_id] = {
                            'title': paper.title,
                            'local_path': filepath,
                            'downloaded_at': datetime.now().isoformat(),
                            'paper_id': paper.paper_id
                        }
                        self._save_cache()
                        print(f"📥 Downloaded new PDF: {paper.title}")
                        return filepath
                    elif response.status == 429 and retry_count < max_retries:
                        wait_time = (2 ** retry_count) * 3
                        print(f"❌ Rate limit during download. Waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)
                        return await self.download_pdf(paper, retry_count + 1)
                    else:
                        print(f"❌ Failed to download {paper.title}: HTTP {response.status}")
                        return None
            except asyncio.TimeoutError:
                print(f"❌ Download timeout for {paper.title}")
                return None
            except Exception as e:
                print(f"❌ Download error for {paper.title}: {e}")
                if retry_count < max_retries:
                    wait_time = 5
                    print(f"🔄 Retrying download in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    return await self.download_pdf(paper, retry_count + 1)
                return None
    
    def clear_cache(self, paper_id: Optional[str] = None):
        """Clear cache for specific paper or all papers"""
        if paper_id:
            if paper_id in self.downloaded_papers_cache:
                file_path = self.downloaded_papers_cache[paper_id]['local_path']
                if os.path.exists(file_path):
                    os.remove(file_path)
                del self.downloaded_papers_cache[paper_id]
                print(f"🗑️ Removed from cache: {paper_id}")
        else:
            for paper_id, info in self.downloaded_papers_cache.items():
                if os.path.exists(info['local_path']):
                    os.remove(info['local_path'])
            self.downloaded_papers_cache = {}
            print(f"🗑️ Cleared entire cache")
        
        self._save_cache()
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'total_cached_papers': len(self.downloaded_papers_cache),
            'cache_size_mb': self._get_cache_size(),
            'papers': list(self.downloaded_papers_cache.keys())
        }
    
    def _get_cache_size(self) -> float:
        """Calculate total cache size in MB"""
        total_size = 0
        for paper_id, info in self.downloaded_papers_cache.items():
            if os.path.exists(info['local_path']):
                total_size += os.path.getsize(info['local_path'])
        return round(total_size / (1024 * 1024), 2)