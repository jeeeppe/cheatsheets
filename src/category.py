"""
Category module for the Cheat Sheet Collection.

This module implements the hierarchical category system used to organize
cheat sheets. It provides classes and functions for creating, managing,
and traversing the category structure.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class CheatSheet:
    """
    Represents a single cheat sheet in the collection.
    
    Attributes:
        name: The name of the cheat sheet
        path: File system path to the cheat sheet
        format: File format (md, html, png, etc.)
        tags: List of tags for improved searchability
    """
    name: str
    path: str
    format: str
    tags: List[str] = field(default_factory=list)
    
    def matches_search(self, query: str, fuzzy_threshold: int = 70) -> bool:
        """
        Check if this cheat sheet matches the search query.
        
        Args:
            query: Search string to match against
            fuzzy_threshold: Minimum score (0-100) for fuzzy matching
            
        Returns:
            True if the cheat sheet matches the query
        """
        # This is a placeholder for the actual fuzzy matching implementation
        # In a real implementation, we'd use a library like fuzzywuzzy
        query_lower = query.lower()
        
        # Check name
        if query_lower in self.name.lower():
            return True
            
        # Check tags
        for tag in self.tags:
            if query_lower in tag.lower():
                return True
                
        # More sophisticated matching would be implemented here
        return False
        
    def __str__(self) -> str:
        return f"{self.name} ({self.format})"


@dataclass
class Category:
    """
    Represents a category in the hierarchical structure.
    
    A category can contain both subcategories and cheat sheets.
    
    Attributes:
        name: The name of the category
        subcategories: Dictionary of subcategories, keyed by name
        cheatsheets: List of cheat sheets in this category
        parent: Reference to parent category, if any
    """
    name: str
    subcategories: Dict[str, Category] = field(default_factory=dict)
    cheatsheets: List[CheatSheet] = field(default_factory=list)
    parent: Optional[Category] = None
    
    def add_subcategory(self, name: str) -> Category:
        """
        Add a new subcategory to this category.
        
        Args:
            name: Name of the new subcategory
            
        Returns:
            The newly created Category object
            
        Raises:
            ValueError: If a subcategory with this name already exists
        """
        if name in self.subcategories:
            raise ValueError(f"Subcategory '{name}' already exists")
            
        category = Category(name=name, parent=self)
        self.subcategories[name] = category
        return category
        
    def add_cheatsheet(self, cheatsheet: CheatSheet) -> None:
        """
        Add a cheat sheet to this category.
        
        Args:
            cheatsheet: The CheatSheet object to add
            
        Raises:
            ValueError: If a cheat sheet with the same name already exists
        """
        # Check for duplicate names
        for existing in self.cheatsheets:
            if existing.name == cheatsheet.name:
                raise ValueError(f"Cheat sheet '{cheatsheet.name}' already exists in this category")
                
        self.cheatsheets.append(cheatsheet)
        
    def get_subcategory(self, path: str) -> Optional[Category]:
        """
        Get a subcategory by path.
        
        Args:
            path: Path to the subcategory, using '/' as separator
            
        Returns:
            The Category object if found, None otherwise
        """
        parts = path.split('/')
        current = self
        
        for part in parts:
            if part == '':
                continue
                
            if part not in current.subcategories:
                return None
                
            current = current.subcategories[part]
            
        return current
        
    def get_path(self) -> str:
        """
        Get the full path to this category.
        
        Returns:
            The path as a string, using '/' as separator
        """
        if self.parent is None:
            return self.name
            
        return f"{self.parent.get_path()}/{self.name}"
        
    def search(self, query: str) -> List[Tuple[CheatSheet, str]]:
        """
        Search for cheat sheets matching the query in this category and subcategories.
        
        Args:
            query: Search string to match against
            
        Returns:
            List of tuples containing matching CheatSheet objects and their category paths
        """
        results = []
        
        # Check cheat sheets in this category
        for cheatsheet in self.cheatsheets:
            if cheatsheet.matches_search(query):
                results.append((cheatsheet, self.get_path()))
                
        # Recursively search subcategories
        for subcategory in self.subcategories.values():
            results.extend(subcategory.search(query))
            
        return results
        
    def to_dict(self) -> dict:
        """
        Convert this category to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the category
        """
        return {
            "name": self.name,
            "subcategories": {
                name: category.to_dict() 
                for name, category in self.subcategories.items()
            },
            "cheatsheets": [
                {
                    "name": cs.name,
                    "path": cs.path,
                    "format": cs.format,
                    "tags": cs.tags
                }
                for cs in self.cheatsheets
            ]
        }
        
    @classmethod
    def from_dict(cls, data: dict, parent: Optional[Category] = None) -> Category:
        """
        Create a Category from a dictionary.
        
        Args:
            data: Dictionary representation of the category
            parent: Parent category, if any
            
        Returns:
            The created Category object
        """
        category = cls(
            name=data["name"],
            parent=parent
        )
        
        # Add subcategories
        for name, subcat_data in data.get("subcategories", {}).items():
            subcat_data["name"] = name
            subcategory = cls.from_dict(subcat_data, parent=category)
            category.subcategories[name] = subcategory
            
        # Add cheat sheets
        for cs_data in data.get("cheatsheets", []):
            cheatsheet = CheatSheet(
                name=cs_data["name"],
                path=cs_data["path"],
                format=cs_data["format"],
                tags=cs_data.get("tags", [])
            )
            category.cheatsheets.append(cheatsheet)
            
        return category
        
    def __str__(self) -> str:
        return self.name


class CategoryManager:
    """
    Manages the entire category hierarchy.
    
    This class provides operations for the root categories and
    serves as the main interface for interacting with the category system.
    """
    def __init__(self):
        self.root_categories: Dict[str, Category] = {}
        
    def add_root_category(self, name: str) -> Category:
        """
        Add a new root category.
        
        Args:
            name: Name of the new category
            
        Returns:
            The created Category object
            
        Raises:
            ValueError: If a root category with this name already exists
        """
        if name in self.root_categories:
            raise ValueError(f"Root category '{name}' already exists")
            
        category = Category(name=name)
        self.root_categories[name] = category
        return category
        
    def get_category(self, path: str) -> Optional[Category]:
        """
        Get a category by path.
        
        Args:
            path: Path to the category, using '/' as separator
            
        Returns:
            The Category object if found, None otherwise
        """
        if not path:
            return None
            
        parts = path.split('/')
        root_name = parts[0]
        
        if root_name not in self.root_categories:
            return None
            
        if len(parts) == 1:
            return self.root_categories[root_name]
            
        return self.root_categories[root_name].get_subcategory('/'.join(parts[1:]))
        
    def add_cheatsheet(self, path: str, cheatsheet: CheatSheet) -> bool:
        """
        Add a cheat sheet to a specific category.
        
        Args:
            path: Path to the category
            cheatsheet: The CheatSheet to add
            
        Returns:
            True if successful, False if the category doesn't exist
            
        Raises:
            ValueError: If a cheat sheet with the same name already exists in the category
        """
        category = self.get_category(path)
        if category is None:
            return False
            
        category.add_cheatsheet(cheatsheet)
        return True
        
    def search(self, query: str) -> List[Tuple[CheatSheet, str]]:
        """
        Search for cheat sheets matching the query across all categories.
        
        Args:
            query: Search string to match against
            
        Returns:
            List of tuples containing matching CheatSheet objects and their category paths
        """
        results = []
        
        for category in self.root_categories.values():
            results.extend(category.search(query))
            
        return results
        
    def get_all_categories(self) -> Set[str]:
        """
        Get all category paths in the system.
        
        Returns:
            Set of category paths
        """
        paths = set()
        
        def collect_paths(category: Category, current_path: str):
            path = current_path + '/' + category.name if current_path else category.name
            paths.add(path)
            
            for subcat in category.subcategories.values():
                collect_paths(subcat, path)
        
        for root in self.root_categories.values():
            collect_paths(root, "")
            
        return paths
        
    def to_dict(self) -> dict:
        """
        Convert the category manager to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the category manager
        """
        return {
            "categories": {
                name: category.to_dict()
                for name, category in self.root_categories.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'CategoryManager':
        """
        Create a CategoryManager from a dictionary.
        
        Args:
            data: Dictionary representation of the category manager
            
        Returns:
            The created CategoryManager object
        """
        manager = cls()
        
        for name, category_data in data.get("categories", {}).items():
            category_data["name"] = name
            category = Category.from_dict(category_data)
            manager.root_categories[name] = category
            
        return manager
