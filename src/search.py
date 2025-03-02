"""
Search module for the Cheat Sheet Collection.

This module provides functionality for searching cheat sheets
using fuzzy matching and ranking results by relevance.
"""
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Union

try:
    from fuzzywuzzy import fuzz, process
    HAVE_FUZZYWUZZY = True
except ImportError:
    HAVE_FUZZYWUZZY = False

from .category import CategoryManager, CheatSheet


class SearchResult:
    """
    Represents a single search result with relevance score.
    """
    def __init__(self, cheatsheet: CheatSheet, category_path: str, score: float):
        """
        Initialize a search result.
        
        Args:
            cheatsheet: The matching CheatSheet
            category_path: Path to the category containing the cheat sheet
            score: Relevance score (0-100)
        """
        self.cheatsheet = cheatsheet
        self.category_path = category_path
        self.score = score
        
    def __str__(self) -> str:
        return f"{self.category_path}/{self.cheatsheet.name} ({self.score:.1f}%)"
        
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.cheatsheet.name,
            "path": self.cheatsheet.path,
            "format": self.cheatsheet.format,
            "category": self.category_path,
            "score": self.score,
            "tags": self.cheatsheet.tags
        }


class SearchEngine:
    """
    Handles searching for cheat sheets and ranking results.
    """
    def __init__(self, category_manager: CategoryManager):
        """
        Initialize the search engine.
        
        Args:
            category_manager: The CategoryManager to search in
        """
        self.category_manager = category_manager
        
    def _calculate_score(self, query: str, text: str) -> float:
        """
        Calculate similarity score between query and text.
        
        Args:
            query: Search query
            text: Text to compare against
            
        Returns:
            Similarity score (0-100)
        """
        if HAVE_FUZZYWUZZY:
            # Use fuzzywuzzy if available
            return fuzz.partial_ratio(query.lower(), text.lower())
        else:
            # Fall back to SequenceMatcher from difflib
            matcher = SequenceMatcher(None, query.lower(), text.lower())
            return matcher.ratio() * 100
            
    def search(self, query: str, min_score: float = 50.0) -> List[SearchResult]:
        """
        Search for cheat sheets matching the query.
        
        Args:
            query: Search string
            min_score: Minimum relevance score (0-100)
            
        Returns:
            List of SearchResult objects, sorted by relevance
        """
        if not query:
            return []
            
        results = []
        raw_matches = self.category_manager.search(query)
        
        for cheatsheet, category_path in raw_matches:
            # Calculate match scores for various attributes
            name_score = self._calculate_score(query, cheatsheet.name)
            tag_scores = [self._calculate_score(query, tag) for tag in cheatsheet.tags]
            max_tag_score = max(tag_scores) if tag_scores else 0
            
            # Weight the name match more heavily than tag matches
            final_score = max(name_score * 0.7 + max_tag_score * 0.3, 
                              name_score, 
                              max_tag_score)
            
            if final_score >= min_score:
                results.append(SearchResult(
                    cheatsheet=cheatsheet,
                    category_path=category_path,
                    score=final_score
                ))
                
        # Sort by score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        return results
        
    def search_categories(self, query: str, min_score: float = 50.0) -> Dict[str, float]:
        """
        Search for categories matching the query.
        
        Args:
            query: Search string
            min_score: Minimum relevance score (0-100)
            
        Returns:
            Dictionary mapping category paths to relevance scores
        """
        if not query:
            return {}
            
        results = {}
        all_categories = self.category_manager.get_all_categories()
        
        for category_path in all_categories:
            # For categories, just match against the name
            # (which is the last part of the path)
            category_name = category_path.split('/')[-1]
            score = self._calculate_score(query, category_name)
            
            if score >= min_score:
                results[category_path] = score
                
        return results
        
    def get_completion_suggestions(self, partial_query: str, max_results: int = 5) -> List[str]:
        """
        Get suggestions for tab completion.
        
        Args:
            partial_query: Partial query string
            max_results: Maximum number of suggestions to return
            
        Returns:
            List of suggested completions
        """
        if not partial_query:
            return []
            
        # Search categories
        category_matches = self.search_categories(partial_query, min_score=30.0)
        
        # Sort by score
        sorted_matches = sorted(
            category_matches.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Extract just the category paths
        suggestions = [path for path, _ in sorted_matches[:max_results]]
        return suggestions
