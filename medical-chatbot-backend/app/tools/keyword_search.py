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
        return """Search trusted medical sources (WebTeb, WHO, Mayo Clinic) for information.
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
            
            # Rank results by domain priority
            results.sort(key=lambda x: DOMAIN_PRIORITY.get(x["domain"], 999))
            
            # Limit to top 5 results
            results = results[:5]
            
            # Extract sources
            sources = [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "domain": r["domain"],
                    "snippet": r["snippet"]
                }
                for r in results
            ]
            
            return ToolResult(
                success=True,
                data=results,
                sources=sources
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )
    
    async def _search_domain(self, domain: str, query: str) -> List[Dict]:
        """
        Search a specific domain using Google site search
        
        This is a simplified implementation. In production, you might want to:
        1. Use official APIs from each source
        2. Implement caching
        3. Add rate limiting
        """
        results = []
        
        try:
            # Use Google site search (simplified approach)
            # In production, consider using official APIs or a search service
            search_url = f"https://www.google.com/search?q=site:{domain}+{quote_plus(query)}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(search_url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Parse search results (this is simplified)
                    # In production, use proper APIs
                    for result in soup.select('.g')[:3]:  # Top 3 per domain
                        title_elem = result.select_one('h3')
                        link_elem = result.select_one('a')
                        snippet_elem = result.select_one('.VwiC3b')
                        
                        if title_elem and link_elem:
                            results.append({
                                "title": title_elem.get_text(),
                                "url": link_elem.get('href', ''),
                                "domain": domain,
                                "snippet": snippet_elem.get_text() if snippet_elem else ""
                            })
        
        except Exception as e:
            # Log error but don't fail the entire search
            print(f"Error searching {domain}: {str(e)}")
        
        return results
