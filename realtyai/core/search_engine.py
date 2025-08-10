"""
Search Engine module for RealtyAI
Handles web search functionality using SerpAPI
"""

import requests
import time
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import logging
from serpapi import GoogleSearch
from ..config import get_settings

logger = logging.getLogger(__name__)


class SearchResult:
    '''Data class for search results'''
    
    def __init__(self, title: str, snippet: str, url: str, source: str = ''):
        self.title = title
        self.snippet = snippet
        self.url = url
        self.source = source
    
    def __repr__(self):
        return f'SearchResult(title={self.title[:50]}..., url={self.url})'


class SearchEngine:
    '''Search engine interface using SerpAPI for real web search'''
    
    def __init__(self):
        settings = get_settings()
        self.config = settings.get_search_config()
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search(self, query: str, num_results: int = None) -> List[SearchResult]:
        '''
        Perform web search using SerpAPI
        
        Args:
            query: Search query string
            num_results: Number of results to return (default from config)
        
        Returns:
            List of SearchResult objects
        '''
        if num_results is None:
            num_results = self.settings.max_search_results
        
        results = []
        
        # Try SerpAPI first (primary search provider)
        if 'serp' in self.config:
            try:
                serp_results = self._serp_search(query, num_results)
                results.extend(serp_results)
                logger.info(f'Retrieved {len(serp_results)} results from SerpAPI')
            except Exception as e:
                logger.error(f'SerpAPI search failed: {str(e)}')
        
        # If no results from any API, log error and return empty list
        if len(results) == 0:
            logger.error('All search APIs failed. No search results available.')
        
        return results[:num_results]
    
    def _serp_search(self, query: str, num_results: int) -> List[SearchResult]:
        '''Perform search using SerpAPI'''
        api_key = self.config['serp']['api_key']
        
        params = {
            'engine': 'google',
            'q': query,
            'api_key': api_key,
            'num': min(num_results, 100),  # SerpAPI limit
            'hl': 'en',
            'gl': 'us'
        }
        
        search = GoogleSearch(params)
        search_results = search.get_dict()
        
        results = []
        
        # Process organic results
        for item in search_results.get('organic_results', []):
            result = SearchResult(
                title=item.get('title', ''),
                snippet=item.get('snippet', ''),
                url=item.get('link', ''),
                source='SerpAPI'
            )
            results.append(result)
        
        return results
