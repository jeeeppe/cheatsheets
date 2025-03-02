"""
Utilities module for the Cheat Sheet Collection.

This module provides common utility functions used throughout the application.
"""
import os
import re
from pathlib import Path
from typing import Optional, Tuple


def get_file_format(file_path: str) -> str:
    """
    Determine the format of a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Format string (e.g., 'md', 'html', 'png')
    """
    path = Path(file_path)
    # Get the extension without the dot and convert to lowercase
    return path.suffix[1:].lower() if path.suffix else ''


def normalize_path(path: str) -> str:
    """
    Normalize a path string.
    
    Args:
        path: Path string to normalize
        
    Returns:
        Normalized path string
    """
    # Replace backslashes with forward slashes
    normalized = path.replace('\\', '/')
    
    # Remove leading/trailing slashes
    normalized = normalized.strip('/')
    
    # Collapse multiple slashes
    normalized = re.sub(r'/+', '/', normalized)
    
    return normalized


def get_user_data_dir() -> Path:
    """
    Get the appropriate directory for storing user data.
    
    Returns:
        Path object for the data directory
    """
    if os.name == 'nt':  # Windows
        data_dir = Path(os.environ.get('APPDATA', '')) / 'CheatSheetCollection'
    else:  # macOS and Linux
        data_dir = Path.home() / '.config' / 'cheatsheet-collection'
        
    # Create the directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir


def split_path(path: str) -> Tuple[str, Optional[str]]:
    """
    Split a path into category path and cheat sheet name.
    
    Args:
        path: Path string (e.g., 'hacking/exploits/shells/p3rev.md')
        
    Returns:
        Tuple of (category_path, cheatsheet_name) or (category_path, None)
    """
    normalized = normalize_path(path)
    parts = normalized.split('/')
    
    if not parts:
        return '', None
        
    # Check if the last part has a file extension
    # If it does, it's a cheat sheet name
    if '.' in parts[-1]:
        return '/'.join(parts[:-1]), parts[-1]
    else:
        return normalized, None


def is_valid_category_name(name: str) -> bool:
    """
    Check if a category name is valid.
    
    Args:
        name: Category name to check
        
    Returns:
        True if valid, False otherwise
    """
    # Category names can only contain alphanumeric characters,
    # underscores, and hyphens
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))


def suggest_category_name(name: str) -> str:
    """
    Suggest a valid category name based on an invalid one.
    
    Args:
        name: Invalid category name
        
    Returns:
        Suggested valid category name
    """
    # Replace spaces with underscores
    suggested = name.replace(' ', '_')
    
    # Remove invalid characters
    suggested = re.sub(r'[^a-zA-Z0-9_-]', '', suggested)
    
    return suggested


def format_search_results(results: list, show_score: bool = False) -> str:
    """
    Format search results for display.
    
    Args:
        results: List of SearchResult objects
        show_score: Whether to show relevance scores
        
    Returns:
        Formatted string for display
    """
    if not results:
        return "No results found."
        
    # Group by category
    by_category = {}
    for result in results:
        if result.category_path not in by_category:
            by_category[result.category_path] = []
        by_category[result.category_path].append(result)
        
    lines = []
    for category, category_results in by_category.items():
        lines.append(f"{category}")
        for result in category_results:
            if show_score:
                lines.append(f"  {result.cheatsheet.name} ({result.score:.1f}%)")
            else:
                lines.append(f"  {result.cheatsheet.name}")
                
    return '\n'.join(lines)
