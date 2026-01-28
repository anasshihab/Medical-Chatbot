"""Base tool interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from tool execution"""
    success: bool
    data: Any = None
    error: str = None
    sources: List[Dict[str, str]] = []


class BaseTool(ABC):
    """Base class for all agent tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for agent"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool"""
        pass
