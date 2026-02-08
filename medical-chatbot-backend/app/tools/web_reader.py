"""Web Page Reader tool for fetching specific URLs"""
import httpx
from bs4 import BeautifulSoup
from app.tools.base import BaseTool, ToolResult

class WebPageReaderTool(BaseTool):
    """Fetch and extract text content from a specific URL"""
    
    @property
    def name(self) -> str:
        return "read_url"
    
    @property
    def description(self) -> str:
        return """Read and extract content from a specific URL provided by the user.
Use this when the user explicitly provides a link (http://...) and asks to summarize or read it.
Input: url (string)"""
    
    async def execute(self, url: str) -> ToolResult:
        """
        Fetch URL content
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove scripts and styles
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()
                    
                    text = soup.get_text(separator='\n')
                    
                    # Clean text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    # Truncate if too long (approx 2000 words)
                    text = text[:10000]
                    
                    return ToolResult(
                        success=True,
                        data={"content": text, "url": url, "title": soup.title.string if soup.title else url},
                        sources=[{"title": soup.title.string if soup.title else "Web Page", "url": url, "domain": url, "snippet": text[:200]}]
                    )
                else:
                    return ToolResult(
                        success=False,
                        error=f"Failed to fetch URL: Status {response.status_code}"
                    )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error reading URL: {str(e)}"
            )
