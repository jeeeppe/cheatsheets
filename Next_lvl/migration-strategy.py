class MigrationTool:
    """Tools for migrating from flat categories to hierarchical keywords."""
    
    def __init__(self, manager):
        """Initialize with a CheatSheetManager instance."""
        self.manager = manager
        
    def suggest_hierarchy(self):
        """
        Analyze existing categories and suggest a hierarchical structure.
        
        Returns:
            dict: Suggested hierarchical taxonomy
        """
        # Collect all categories
        all_categories = set()
        for cs in self.manager.cheatsheets["cheatsheets"]:
            all_categories.update(cs["categories"])
            
        # First-level attempt: group by common prefixes
        taxonomy = {}
        
        # Look for categories that could form hierarchies
        # For example: "python", "python-libraries", "python-web" could form a hierarchy
        prefix_groups = {}
        
        # Group by prefix
        for category in all_categories:
            parts = category.split("-")
            if len(parts) > 1:
                prefix = parts[0]
                if prefix not in prefix_groups:
                    prefix_groups[prefix] = []
                prefix_groups[prefix].append(category)
                
        # Create hierarchy based on prefix groups
        for prefix, categories in prefix_groups.items():
            if prefix in all_categories and len(categories) > 1:
                # This prefix is both a category itself and has sub-categories
                taxonomy[prefix] = {cat.replace(prefix + "-", ""): {} for cat in categories if cat != prefix}
                # Remove these from further processing
                all_categories -= set(categories)
                all_categories.add(prefix)  # Keep the prefix as a top-level category
                
        # Add remaining categories as top-level entries
        for category in all_categories:
            if category not in taxonomy:
                taxonomy[category] = {}
                
        return taxonomy
        
    def apply_suggested_hierarchy(self, taxonomy, root="Computers"):
        """
        Apply the suggested hierarchy to the cheatsheets.
        
        Args:
            taxonomy (dict): The taxonomy to apply
            root (str): The root node of the taxonomy
            
        Returns:
            int: Number of cheatsheets updated
        """
        # Create a mapping from categories to paths
        category_to_path = {}
        
        def build_paths(node, current_path):
            for key, children in node.items():
                path = current_path + [key]
                category_to_path[key] = path
                build_paths(children, path)
                
        build_paths(taxonomy, [root])
        
        # Update cheatsheets with paths
        updated = 0
        for cs in self.manager.cheatsheets["cheatsheets"]:
            # Skip if already has a path
            if "keyword_path" in cs:
                continue
                
            # Find the best matching path based on categories
            best_path = None
            for category in cs["categories"]:
                if category in category_to_path:
                    # Use the first match for now
                    if best_path is None:
                        best_path = category_to_path[category]
                        
            # Apply the path if found
            if best_path:
                cs["keyword_path"] = best_path
                updated += 1
                
        if updated > 0:
            self.manager._save_cheatsheets()
            
        return updated
        
    def suggest_keyword_path(self, cheatsheet):
        """
        Suggest a keyword path for a single cheatsheet based on its content and categories.
        
        Args:
            cheatsheet (dict): The cheatsheet to analyze
            
        Returns:
            list: Suggested keyword path
        """
        # Start with categories as a basis
        if cheatsheet["categories"]:
            main_category = cheatsheet["categories"][0]
            return ["Uncategorized", main_category]
            
        # If no categories, try to extract keywords from content
        content_lower = cheatsheet["content"].lower()
        
        # Check for programming languages
        languages = ["python", "javascript", "java", "c++", "c#", "ruby", "php", "go", "rust"]
        for lang in languages:
            if lang in content_lower:
                return ["Computers", "Programming", lang.capitalize()]
                
        # Check for specific domains
        domains = {
            "git": ["Computers", "Version Control", "Git"],
            "docker": ["Computers", "Containerization", "Docker"],
            "linux": ["Computers", "Operating Systems", "Linux"],
            "windows": ["Computers", "Operating Systems", "Windows"],
            "bash": ["Computers", "Shell", "Bash"],
            "sql": ["Computers", "Databases", "SQL"],
        }
        
        for keyword, path in domains.items():
            if keyword in content_lower:
                return path
                
        # Default path if nothing else matches
        return ["Uncategorized"]
        
    def batch_migrate(self, interactive=True, defaults=None):
        """
        Migrate all cheatsheets that don't have a keyword path.
        
        Args:
            interactive (bool): Whether to prompt for confirmation for each cheatsheet
            defaults (dict): Default paths to use for specific categories
            
        Returns:
            int: Number of cheatsheets migrated
        """
        defaults = defaults or {}
        migrated = 0
        
        for cs in self.manager.cheatsheets["cheatsheets"]:
            if "keyword_path" in cs:
                continue
                
            # Try to find a default path based on categories
            default_path = None
            for category in cs["categories"]:
                if category in defaults:
                    default_path = defaults[category]
                    break
                    
            # If no default found, suggest one
            if default_path is None:
                default_path = self.suggest_keyword_path(cs)
                
            if interactive:
                # Show the suggestion and prompt for confirmation or modification
                print(f"\nCheatsheet: {cs['name']}")
                print(f"Categories: {', '.join(cs['categories'])}")
                print(f"Suggested path: {' → '.join(default_path)}")
                response = input("Accept suggestion? (y/n/m for modify): ")
                
                if response.lower() == 'y':
                    cs["keyword_path"] = default_path
                    migrated += 1
                elif response.lower() == 'm':
                    path_str = input(f"Enter new path (comma-separated): ")
                    cs["keyword_path"] = [p.strip() for p in path_str.split(",")]
                    migrated += 1
                # Skip if 'n'
            else:
                # Apply the default path without prompting
                cs["keyword_path"] = default_path
                migrated += 1
                
        if migrated > 0:
            self.manager._save_cheatsheets()
            
        return migrated