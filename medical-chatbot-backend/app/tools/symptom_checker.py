"""Symptom checker tool using WebTeb API"""
import httpx
from typing import List, Dict
from app.tools.base import BaseTool, ToolResult
from app.config import settings


class SymptomCheckerTool(BaseTool):
    """Check symptoms using WebTeb Symptom Checker API"""
    
    @property
    def name(self) -> str:
        return "symptom_checker"
    
    @property
    def description(self) -> str:
        return """Analyze symptoms using WebTeb Symptom Checker API.
Use this when users describe specific symptoms they're experiencing.
Input: symptoms (list of strings), age (int), gender (string)"""
    
    async def execute(
        self,
        symptoms: List[str],
        age: int = None,
        gender: str = None
    ) -> ToolResult:
        """
        Execute symptom checker
        
        Args:
            symptoms: List of symptom descriptions
            age: User age (optional)
            gender: User gender (optional)
        
        Returns:
            ToolResult with possible conditions and advice
        """
        try:
            # Validate inputs
            if not symptoms or len(symptoms) == 0:
                return ToolResult(
                    success=False,
                    error="No symptoms provided"
                )
            
            # Call WebTeb API
            # ملاحظة: هذا مثال على استدعاء API
            # قم بتعديله حسب المواصفات الفعلية لـ WebTeb API
            results = await self._call_webteb_api(symptoms, age, gender)
            
            if not results:
                return ToolResult(
                    success=False,
                    error="Symptom checker API returned no results"
                )
            
            # Normalize results
            normalized = self._normalize_results(results)
            
            return ToolResult(
                success=True,
                data=normalized,
                sources=[{
                    "title": "WebTeb Symptom Checker",
                    "url": "https://www.webteb.com",
                    "domain": "webteb.com",
                    "snippet": "Symptom analysis from WebTeb"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Symptom checker failed: {str(e)}"
            )
    
    async def _call_webteb_api(
        self,
        symptoms: List[str],
        age: int = None,
        gender: str = None
    ) -> Dict:
        """
        Call WebTeb Symptom Checker API
        
        ملاحظة: هذا مثال توضيحي
        قم بتعديل الطلب حسب المواصفات الفعلية لـ WebTeb API
        """
        if not settings.WEBTEB_API_KEY:
            # Return mock data if API key not configured
            return self._get_mock_results(symptoms)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    settings.WEBTEB_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.WEBTEB_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "symptoms": symptoms,
                        "age": age,
                        "gender": gender
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"WebTeb API error: {response.status_code}")
                    return self._get_mock_results(symptoms)
        
        except Exception as e:
            print(f"WebTeb API call failed: {str(e)}")
            return self._get_mock_results(symptoms)
    
    def _normalize_results(self, results: Dict) -> Dict:
        """
        Normalize API results to consistent format
        
        Returns:
            {
                "possible_conditions": [...],
                "advice": "...",
                "disclaimer": "..."
            }
        """
        return {
            "possible_conditions": results.get("conditions", []),
            "advice": results.get("advice", "Please consult a healthcare provider for proper evaluation"),
            "disclaimer": "This is not a diagnosis. These are possible conditions based on reported symptoms. Always consult a licensed healthcare provider."
        }
    
    def _get_mock_results(self, symptoms: List[str]) -> Dict:
        """
        Return mock results when API is not available
        For development/testing purposes
        """
        return {
            "conditions": [
                {
                    "name": "Common condition related to symptoms",
                    "probability": "moderate",
                    "description": "This is a placeholder result"
                }
            ],
            "advice": "Based on these symptoms, you should consult a healthcare provider for proper evaluation."
        }
