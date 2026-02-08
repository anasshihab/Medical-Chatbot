"""Robust search tool using DuckDuckGo library with WebTeb prioritization"""
from typing import List, Dict
from ddgs import DDGS
from app.tools.base import BaseTool, ToolResult
from app.utils.constants import APPROVED_DOMAINS, DOMAIN_PRIORITY

class SearchTool(BaseTool):
    """Medical search tool that prioritizes WebTeb, then searches other trusted sources"""
    
    @property
    def name(self) -> str:
        return "medical_search"
    
    @property
    def description(self) -> str:
        return "Search medical information. ALWAYS searches WebTeb.com FIRST as the primary source, then searches other trusted medical sources (WHO, Mayo Clinic, NIH, CDC) if needed. Returns all URLs searched and found."

    def _get_domain_priority(self, url: str) -> int:
        """Get priority score for a URL based on its domain"""
        for domain, priority in DOMAIN_PRIORITY.items():
            if domain in url:
                return priority
        return 999  # Unknown domains get lowest priority

    def _extract_domain_name(self, url: str) -> str:
        """Extract readable domain name from URL"""
        for domain in APPROVED_DOMAINS:
            if domain in url:
                if "webteb" in domain:
                    return "WebTeb"
                elif "mayoclinic" in domain:
                    return "Mayo Clinic"
                elif "who.int" in domain:
                    return "WHO"
                elif "cdc.gov" in domain:
                    return "CDC"
                elif "nih.gov" in domain:
                    return "NIH"
                elif "webmd" in domain:
                    return "WebMD"
                elif "healthline" in domain:
                    return "Healthline"
                elif "pubmed" in domain:
                    return "PubMed"
                elif "medlineplus" in domain:
                    return "MedlinePlus"
        return "Medical Source"

    async def execute(self, query: str, timelimit: str = None) -> ToolResult:
        try:
            all_results = []
            
            with DDGS() as ddgs:
                # STEP 1: Search WebTeb FIRST (Primary Source)
                webteb_query = f"site:webteb.com {query}"
                try:
                    # Added timelimit parameter for recency
                    webteb_results = ddgs.text(
                        webteb_query, 
                        max_results=5,
                        timelimit=timelimit
                    )
                    for r in webteb_results:
                        all_results.append({
                            "title": r.get("title"),
                            "url": r.get("href"),
                            "snippet": r.get("body"),
                            "source": "WebTeb",
                            "priority": 0
                        })
                except:
                    pass  # Continue even if WebTeb search fails
                
                # STEP 2: Search other trusted sources (if needed)
                other_domains = [d for d in APPROVED_DOMAINS if d != "webteb.com"]
                sites_query = " OR ".join([f"site:{domain}" for domain in other_domains])
                full_query = f"({sites_query}) {query}"
                
                other_results = ddgs.text(
                    full_query, 
                    max_results=6,
                    timelimit=timelimit
                )
                for r in other_results:
                    url = r.get("href", "")
                    all_results.append({
                        "title": r.get("title"),
                        "url": url,
                        "snippet": r.get("body"),
                        "source": self._extract_domain_name(url),
                        "priority": self._get_domain_priority(url)
                    })
            
            # Sort by priority (WebTeb first, then by domain priority)
            all_results.sort(key=lambda x: x["priority"])
            
            # Extract sources for the agent to cite
            sources = [
                {"title": r["title"], "url": r["url"], "source": r["source"]} 
                for r in all_results
            ]
            
            return ToolResult(
                success=True,
                data=all_results,
                sources=sources,
                metadata={
                    "webteb_results": sum(1 for r in all_results if r["source"] == "WebTeb"),
                    "total_results": len(all_results),
                    "search_note": "Searched WebTeb.com first, then other trusted medical sources"
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )
