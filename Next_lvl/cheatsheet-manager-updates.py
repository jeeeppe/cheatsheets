class CheatSheetManager:
    """Manages operations on the cheat sheet collection with hierarchical keyword support."""

    def __init__(self, storage_path=DEFAULT_STORAGE_PATH):
        """Initialize the CheatSheetManager with the storage path."""
        self.storage_path = storage_path
        self.cheatsheets = self._load_cheatsheets()
        
        # Initialize the taxonomy if it doesn't exist
        if "keyword_taxonomy" not in self.cheatsheets:
            self.cheatsheets["keyword_taxonomy"] = {}
            self._save_cheatsheets()

    def add_cheatsheet(self, name, content, categories=None, keyword_path=None, description=None):
        """
        Add a new cheat sheet to the collection.
        
        Args:
            name (str): Name of the cheat sheet
            content (str): Content of the cheat sheet
            categories (list): Legacy categories (flat list)
            keyword_path (list): Hierarchical path from root to leaf keyword
            description (str): Description of the cheat sheet
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
    
    def _ensure_keyword_path_exists(self, keyword_path):
        """
        Ensure that the given keyword path exists in the taxonomy.
        Creates any missing nodes in the hierarchy.
        
        Args:
            keyword_path (list): List of keywords forming a path in the hierarchy
        """
        current = self.cheatsheets["keyword_taxonomy"]
        
        for keyword in keyword_path:
            if keyword not in current:
                current[keyword] = {}
            current = current[keyword]
    
    def get_keyword_children(self, path=None):
        """
        Get all child keywords at a given path in the taxonomy.
        
        Args:
            path (list): List of keywords forming a path in the hierarchy
                         If None, returns top-level keywords
        
        Returns:
            list: List of child keywords
        """
        if path is None:
            path = []
            
        current = self.cheatsheets["keyword_taxonomy"]
        for keyword in path:
            if keyword not in current:
                return []
            current = current[keyword]
            
        return list(current.keys())
    
    def search_by_keyword_path(self, path, exact_match=False):
        """
        Search for cheat sheets that match the given keyword path.
        
        Args:
            path (list): List of keywords forming a path in the hierarchy
            exact_match (bool): If True, only return cheat sheets that exactly
                               match the full path. If False, return cheat sheets
                               that match the path as a prefix.
        
        Returns:
            list: List of matching cheat sheets
        """
        results = []
        
        for cs in self.cheatsheets["cheatsheets"]:
            if "keyword_path" not in cs:
                continue
                
            if exact_match and cs["keyword_path"] == path:
                results.append(cs)
            elif not exact_match and self._is_prefix(path, cs["keyword_path"]):
                results.append(cs)
                
        return results
    
    def _is_prefix(self, prefix, full_path):
        """Check if prefix is a prefix of full_path."""
        if len(prefix) > len(full_path):
            return False
            
        for i, keyword in enumerate(prefix):
            if full_path[i] != keyword:
                return False
                
        return True
    
    def search_cheatsheets(self, query, path=None):
        """
        Search for cheat sheets by name, category, or content,
        optionally filtered by keyword path.
        
        Args:
            query (str): Search query
            path (list): Optional keyword path to filter results
        
        Returns:
            list: List of matching cheat sheets
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
    
    def list_keywords(self, path=None, include_cheatsheet_count=True):
        """
        List keywords at the specified path, optionally with cheatsheet counts.
        
        Args:
            path (list): Path in the keyword hierarchy
            include_cheatsheet_count (bool): Whether to include the count of 
                                             cheatsheets under each keyword
        
        Returns:
            dict: Dictionary mapping keywords to either empty dict or cheatsheet count
        """
        children = self.get_keyword_children(path)
        result = {}
        
        for child in children:
            if include_cheatsheet_count:
                child_path = (path or []) + [child]
                count = len(self.search_by_keyword_path(child_path, exact_match=False))
                result[child] = count
            else:
                result[child] = {}
                
        return result
    
    def migrate_categories_to_paths(self, default_root="Uncategorized"):
        """
        Migrate legacy category tags to keyword paths.
        For cheatsheets without keyword_path, create paths based on categories.
        
        Args:
            default_root (str): Root keyword for cheatsheets without categories
        
        Returns:
            int: Number of cheatsheets migrated
        """
        migrated = 0
        
        for cs in self.cheatsheets["cheatsheets"]:
            if "keyword_path" not in cs and cs["categories"]:
                # Simple migration: use first category as leaf node
                if cs["categories"]:
                    main_category = cs["categories"][0]
                    cs["keyword_path"] = [default_root, main_category]
                    self._ensure_keyword_path_exists(cs["keyword_path"])
                    migrated += 1
        
        if migrated > 0:
            self._save_cheatsheets()
            
        return migrated