"""Keyword search tool for medical information"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote_plus
from app.tools.base import BaseTool, ToolResult
from app.utils.constants import APPROVED_DOMAINS, DOMAIN_PRIORITY


class KeywordSearchTool(BaseTool):
    """Search approved medical domains for information"""
    
    @property
    def name(self) -> str:
        return "keyword_search"
    
    @property
    def description(self) -> str:
        return """Search trusted medical sources (WHO, CDC, NIH, Mayo Clinic, PubMed, etc.) for information.
Use this when users ask general medical questions or need information about conditions, symptoms, or health topics.
Input: search_query (string)"""
    
    async def execute(self, search_query: str) -> ToolResult:
        """
        Execute keyword search across approved domains
        
        Args:
            search_query: The search query
        
        Returns:
            ToolResult with search results
        """
        try:
            results = []
            
            # Search each approved domain
            for domain in APPROVED_DOMAINS:
                domain_results = await self._search_domain(domain, search_query)
                results.extend(domain_results)
            
            # STRICT FILTERING: Remove any result not from approved domains
            validated_results = []
            for r in results:
                # Extract domain from URL
                from urllib.parse import urlparse
                parsed_url = urlparse(r.get("url", ""))
                result_domain = parsed_url.netloc.replace("www.", "")
                
                # Only include if domain matches one of our approved domains
                if any(approved in result_domain for approved in APPROVED_DOMAINS):
                    validated_results.append(r)
            
            # Rank results by domain priority
            validated_results.sort(key=lambda x: DOMAIN_PRIORITY.get(x["domain"], 999))
            
            # Limit to top 5 results
            validated_results = validated_results[:5]
            
            # Extract sources
            sources = [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "domain": r["domain"],
                    "snippet": r["snippet"]
                }
                for r in validated_results
            ]
            
            return ToolResult(
                success=True,
                data=validated_results,
                sources=sources
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )
    
    async def _search_domain(self, domain: str, query: str) -> List[Dict]:
        """
        Search a specific domain using DuckDuckGo HTML (more reliable for scraping)
        """
        results = []
        
        try:
            # Use DuckDuckGo HTML version which is easier to scrape and has fewer blocks
            # q=site:domain.com query
            search_query = f"site:{domain} {query}"
            search_url = "https://html.duckduckgo.com/html/"
            params = {"q": search_query}
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://html.duckduckgo.com/"
            }
            
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.post(search_url, data=params, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # DuckDuckGo HTML results are in .result elements
                    for result in soup.select('.result')[:3]:  # Top 3 per domain
                        title_elem = result.select_one('.result__a')
                        snippet_elem = result.select_one('.result__snippet')
                        url_elem = result.select_one('.result__url')
                        
                        if title_elem and snippet_elem:
                            url = title_elem.get('href', '')
                            # DDG sometimes wraps URLs
                            if 'duckduckgo.com/l/?kh=-1&uddg=' in url:
                                from urllib.parse import unquote
                                url = unquote(url.split('uddg=')[1].split('&')[0])
                            
                            results.append({
                                "title": title_elem.get_text(strip=True),
                                "url": url,
                                "domain": domain,
                                "snippet": snippet_elem.get_text(strip=True)
                            })
                else:
                    print(f"Search failed for {domain}: Status {response.status_code}")
        
        except Exception as e:
            # Log error but don't fail the entire search
            print(f"Error searching {domain}: {str(e)}")
        
        return results
