from abc import ABC, abstractmethod

class Browser(ABC):
    """Base class for browser implementations."""

    @abstractmethod
    def get_page_content(self, url: str) -> str:
        """
        Fetch page content from the given URL.
        
        Args:
            url: The URL to fetch content from.
            
        Returns:
            The page content as string.
        """
        pass