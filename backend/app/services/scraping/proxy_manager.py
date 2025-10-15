"""
Proxy Manager - Handles proxy rotation and management
Harvested and adapted from SchemaChecker project
"""
import os
import random
from typing import List, Optional, Dict
import structlog

logger = structlog.get_logger(__name__)


class ProxyManager:
    """
    Manages proxy rotation for web scraping requests
    Supports both sequential and random rotation strategies
    """
    
    def __init__(
        self,
        proxy_file: Optional[str] = None,
        rotation_strategy: str = "sequential"  # or "random"
    ):
        """
        Initialize proxy manager
        
        Args:
            proxy_file: Path to file containing proxies (one per line)
            rotation_strategy: "sequential" or "random"
        """
        self.proxies: List[str] = []
        self.current_index = 0
        self.rotation_strategy = rotation_strategy
        self.failed_proxies: set = set()
        
        if proxy_file and os.path.exists(proxy_file):
            self.load_proxies(proxy_file)
    
    def load_proxies(self, proxy_file: str) -> int:
        """
        Load proxies from file
        
        Format: username:password@host:port
        Lines starting with # are comments
        
        Args:
            proxy_file: Path to proxy file
            
        Returns:
            Number of proxies loaded
        """
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        # Validate basic format
                        if '@' in line and ':' in line:
                            self.proxies.append(line)
                        else:
                            logger.warning(
                                "invalid_proxy_format",
                                line=line
                            )
            
            logger.info(
                "proxies_loaded",
                count=len(self.proxies),
                file=proxy_file
            )
            return len(self.proxies)
            
        except Exception as e:
            logger.error(
                "proxy_load_failed",
                file=proxy_file,
                error=str(e)
            )
            return 0
    
    def get_next_proxy(self) -> Optional[str]:
        """
        Get next proxy according to rotation strategy
        
        Returns:
            Proxy string or None if no proxies available
        """
        if not self.proxies:
            return None
        
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available_proxies:
            # All proxies failed, reset and try again
            logger.warning("all_proxies_failed_resetting")
            self.failed_proxies.clear()
            available_proxies = self.proxies
        
        if self.rotation_strategy == "random":
            return random.choice(available_proxies)
        else:
            # Sequential rotation
            proxy = available_proxies[self.current_index % len(available_proxies)]
            self.current_index += 1
            return proxy
    
    def mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed"""
        if proxy:
            self.failed_proxies.add(proxy)
            logger.warning(
                "proxy_marked_failed",
                proxy=proxy.split('@')[1] if '@' in proxy else proxy,
                failed_count=len(self.failed_proxies)
            )
    
    def get_proxy_dict(self, proxy: str) -> Dict[str, str]:
        """
        Convert proxy string to requests library format
        
        Args:
            proxy: Proxy string in format username:password@host:port
            
        Returns:
            Dict with 'http' and 'https' keys
        """
        if not proxy:
            return {}
        
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def parse_proxy_for_playwright(self, proxy: str) -> Optional[Dict[str, str]]:
        """
        Parse proxy string into Playwright format
        
        Args:
            proxy: Proxy string in format username:password@host:port
            
        Returns:
            Dict with server, username, password keys
        """
        if not proxy or '@' not in proxy:
            return None
        
        try:
            auth_part, host_part = proxy.split('@', 1)
            username, password = auth_part.split(':', 1)
            host, port = host_part.rsplit(':', 1)
            
            return {
                'server': f'http://{host}:{port}',
                'username': username,
                'password': password
            }
        except Exception as e:
            logger.error(
                "proxy_parse_failed",
                proxy=proxy,
                error=str(e)
            )
            return None
    
    def get_stats(self) -> Dict:
        """Get proxy manager statistics"""
        return {
            'total_proxies': len(self.proxies),
            'failed_proxies': len(self.failed_proxies),
            'available_proxies': len(self.proxies) - len(self.failed_proxies),
            'rotation_strategy': self.rotation_strategy,
            'current_index': self.current_index
        }


def load_proxies_from_file(proxy_file: str) -> List[str]:
    """
    Convenience function to load proxies from file
    
    Args:
        proxy_file: Path to proxy file
        
    Returns:
        List of proxy strings
    """
    manager = ProxyManager()
    manager.load_proxies(proxy_file)
    return manager.proxies

