from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Any

# Type aliases for the hierarchical structure
KeywordTaxonomy = dict[str, "KeywordTaxonomy"]


class CheatSheetDataExtended:
    """Type definition for extended cheat sheet data."""
    name: str
    content: str
    categories: list[str]
    description: str
    created_at: str
    updated_at: str
    keyword_path: list[str]


class CheatSheetCollectionExtended:
    """Type definition for extended cheat sheet collection."""
    cheatsheets: list[dict[str, Any]]
    keyword_taxonomy: KeywordTaxonomy


# Placeholder for actual storage path
DEFAULT_STORAGE_PATH: str = ""


class CheatSheetManager:
    """Manages operations on the cheat sheet collection with hierarchical keyword support."""

    storage_path: str
    cheatsheets: dict[str, Any]

    def __init__(self, storage_path: str = DEFAULT_STORAGE_PATH) -> None:
        """Initialize the CheatSheetManager with the storage path."""
        self.storage_path = storage_path
        self.cheatsheets = self._load_cheatsheets()

        # Initialize the taxonomy if it doesn't exist
        if "keyword_taxonomy" not in self.cheatsheets:
            self.cheatsheets["keyword_taxonomy"] = {}
            self._save_cheatsheets()

    def _load_cheatsheets(self) -> dict[str, Any]:
        """Load cheatsheets from storage (placeholder)."""
        return {"cheatsheets": [], "keyword_taxonomy": {}}

    def _save_cheatsheets(self) -> bool:
        """Save cheatsheets to storage (placeholder)."""
        return True

    def add_cheatsheet(
        self,
        name: str,
        content: str,
        categories: Optional[list[str]] = None,
        keyword_path: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> bool:
        """
        Add a new cheat sheet to the collection.

        Args:
            name: Name of the cheat sheet
            content: Content of the cheat sheet
            categories: Legacy categories (flat list)
            keyword_path: Hierarchical path from root to leaf keyword
            description: Description of the cheat sheet
        """
        # Validate name
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            print("Error: Cheat sheet name must contain only alphanumeric characters, underscores, and hyphens.")
            return False

        # Check for duplicate
        if any(cs["name"] == name for cs in self.cheatsheets["cheatsheets"]):
            print(f"Error: A cheat sheet with the name '{name}' already exists.")
            return False

        # Create new cheat sheet
        now = datetime.now().isoformat()
        new_cheatsheet = {
            "name": name,
            "content": content,
            "categories": categories or [],
            "description": description or "",
            "created_at": now,
            "updated_at": now
        }
        
        # Add keyword_path if provided
        if keyword_path:
            new_cheatsheet["keyword_path"] = keyword_path
            # Ensure the path exists in the taxonomy
            self._ensure_keyword_path_exists(keyword_path)

        # Add to collection and save
        self.cheatsheets["cheatsheets"].append(new_cheatsheet)
        return self._save_cheatsheets()

    def _ensure_keyword_path_exists(self, keyword_path: list[str]) -> None:
        """
        Ensure that the given keyword path exists in the taxonomy.
        Creates any missing nodes in the hierarchy.

        Args:
            keyword_path: List of keywords forming a path in the hierarchy
        """
        current: dict[str, Any] = self.cheatsheets["keyword_taxonomy"]

        for keyword in keyword_path:
            if keyword not in current:
                current[keyword] = {}
            current = current[keyword]

    def get_keyword_children(self, path: Optional[list[str]] = None) -> list[str]:
        """
        Get all child keywords at a given path in the taxonomy.

        Args:
            path: List of keywords forming a path in the hierarchy
                  If None, returns top-level keywords

        Returns:
            List of child keywords
        """
        if path is None:
            path = []

        current: dict[str, Any] = self.cheatsheets["keyword_taxonomy"]
        for keyword in path:
            if keyword not in current:
                return []
            current = current[keyword]

        return list(current.keys())

    def search_by_keyword_path(
        self, path: list[str], exact_match: bool = False
    ) -> list[dict[str, Any]]:
        """
        Search for cheat sheets that match the given keyword path.

        Args:
            path: List of keywords forming a path in the hierarchy
            exact_match: If True, only return cheat sheets that exactly
                         match the full path. If False, return cheat sheets
                         that match the path as a prefix.

        Returns:
            List of matching cheat sheets
        """
        results: list[dict[str, Any]] = []

        for cs in self.cheatsheets["cheatsheets"]:
            if "keyword_path" not in cs:
                continue

            if exact_match and cs["keyword_path"] == path:
                results.append(cs)
            elif not exact_match and self._is_prefix(path, cs["keyword_path"]):
                results.append(cs)

        return results

    def _is_prefix(self, prefix: list[str], full_path: list[str]) -> bool:
        """Check if prefix is a prefix of full_path."""
        if len(prefix) > len(full_path):
            return False

        for i, keyword in enumerate(prefix):
            if full_path[i] != keyword:
                return False

        return True

    def search_cheatsheets(
        self, query: str, path: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        """
        Search for cheat sheets by name, category, or content,
        optionally filtered by keyword path.

        Args:
            query: Search query
            path: Optional keyword path to filter results

        Returns:
            List of matching cheat sheets
        """
        # First filter by path if provided
        if path:
            cheatsheets = self.search_by_keyword_path(path, exact_match=False)
        else:
            cheatsheets = self.cheatsheets["cheatsheets"]
        
        # Then filter by query
        results = []
        query = query.lower()
        
        for cs in cheatsheets:
            # Search in name
            if query in cs["name"].lower():
                results.append(cs)
                continue
                
            # Search in categories
            if any(query in cat.lower() for cat in cs["categories"]):
                results.append(cs)
                continue
                
            # Search in keyword_path if it exists
            if "keyword_path" in cs and any(query in kw.lower() for kw in cs["keyword_path"]):
                results.append(cs)
                continue
                
            # Search in description
            if query in cs["description"].lower():
                results.append(cs)
                continue
                
            # Search in content
            if query in cs["content"].lower():
                results.append(cs)
                continue

        return results

    def list_keywords(
        self, path: Optional[list[str]] = None, include_cheatsheet_count: bool = True
    ) -> dict[str, int | dict[str, Any]]:
        """
        List keywords at the specified path, optionally with cheatsheet counts.

        Args:
            path: Path in the keyword hierarchy
            include_cheatsheet_count: Whether to include the count of
                                      cheatsheets under each keyword

        Returns:
            Dictionary mapping keywords to either empty dict or cheatsheet count
        """
        children = self.get_keyword_children(path)
        result: dict[str, int | dict[str, Any]] = {}

        for child in children:
            if include_cheatsheet_count:
                child_path = (path or []) + [child]
                count = len(self.search_by_keyword_path(child_path, exact_match=False))
                result[child] = count
            else:
                result[child] = {}

        return result

    def migrate_categories_to_paths(self, default_root: str = "Uncategorized") -> int:
        """
        Migrate legacy category tags to keyword paths.
        For cheatsheets without keyword_path, create paths based on categories.

        Args:
            default_root: Root keyword for cheatsheets without categories

        Returns:
            Number of cheatsheets migrated
        """
        migrated = 0

        for cs in self.cheatsheets["cheatsheets"]:
            if "keyword_path" not in cs and cs["categories"]:
                # Simple migration: use first category as leaf node
                if cs["categories"]:
                    main_category: str = cs["categories"][0]
                    cs["keyword_path"] = [default_root, main_category]
                    self._ensure_keyword_path_exists(cs["keyword_path"])
                    migrated += 1

        if migrated > 0:
            self._save_cheatsheets()

        return migrated