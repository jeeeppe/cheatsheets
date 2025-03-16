class DisplayFormatter:
    """Handles formatting and displaying cheat sheets and keywords in the terminal."""
    
    @staticmethod
    def get_terminal_width():
        """Get the width of the terminal."""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80  # Default width if unable to determine
    
    @staticmethod
    def format_cheatsheet_list(cheatsheets):
        """Format a list of cheat sheets for display."""
        if not cheatsheets:
            return "No cheat sheets found."
            
        # Calculate width of each column
        name_width = max(len(cs["name"]) for cs in cheatsheets) + 2
        name_width = min(name_width, 30)  # Cap at 30 chars
        
        term_width = DisplayFormatter.get_terminal_width()
        desc_width = term_width - name_width - 25  # 25 for categories column
        
        # Header
        output = f"{'Name':<{name_width}} {'Keywords/Categories':<20} {'Description'}\n"
        output += f"{'-' * name_width} {'-' * 20} {'-' * desc_width}\n"
        
        # Rows
        for cs in cheatsheets:
            # Display keyword path if available, otherwise categories
            if "keyword_path" in cs:
                path_str = " → ".join(cs["keyword_path"])
                if len(path_str) > 20:
                    path_str = "..." + path_str[-17:]
            else:
                path_str = ", ".join(cs["categories"])
                if len(path_str) > 20:
                    path_str = path_str[:17] + "..."
                
            description = cs["description"]
            if len(description) > desc_width:
                description = description[:desc_width-3] + "..."
                
            output += f"{cs['name']:<{name_width}} {path_str:<20} {description}\n"
            
        return output
    
    @staticmethod
    def format_cheatsheet_content(cheatsheet):
        """Format a cheat sheet's content for display, with basic markdown rendering."""
        if not cheatsheet:
            return "Cheat sheet not found."
            
        output = f"# {cheatsheet['name']}\n\n"
        if cheatsheet["description"]:
            output += f"{cheatsheet['description']}\n\n"
        
        # Display keyword path if available
        if "keyword_path" in cheatsheet:
            output += f"Keyword Path: {' → '.join(cheatsheet['keyword_path'])}\n\n"
        # Display legacy categories
        elif cheatsheet["categories"]:
            output += f"Categories: {', '.join(cheatsheet['categories'])}\n\n"
            
        # Add the content
        output += "-------------------------------\n"
        output += cheatsheet["content"]
        output += "\n-------------------------------\n"
        
        return output
    
    @staticmethod
    def format_keyword_list(path, keywords):
        """
        Format a list of keywords for display.
        
        Args:
            path (list): Current path in the hierarchy
            keywords (dict): Dictionary of keywords and their counts or empty dicts
        
        Returns:
            str: Formatted string for display
        """
        if not keywords:
            if not path:
                return "No keywords found in the taxonomy."
            else:
                return f"No keywords found under '{' → '.join(path)}'."
                
        # Current location
        output = "Current location: "
        if path:
            output += f"{' → '.join(path)}\n"
        else:
            output += "Root\n"
            
        output += "\nKeywords:\n"
        
        # Format based on whether we have counts or not
        if isinstance(next(iter(keywords.values())), int):
            # We have counts
            for keyword, count in sorted(keywords.items()):
                output += f"  {keyword} ({count} cheatsheet{'s' if count != 1 else ''})\n"
        else:
            # We don't have counts
            for keyword in sorted(keywords.keys()):
                output += f"  {keyword}\n"
                
        output += "\nUsage:\n"
        output += "  To navigate deeper: cheatsheet keywords 'current,path,next_level'\n"
        output += "  To list cheatsheets: cheatsheet list --keywords 'path,to,keyword'\n"
        
        return output
    
    @staticmethod
    def format_keyword_tree(path, keywords, depth=0, prefix=""):
        """
        Format a keyword tree for display.
        
        Args:
            path (list): Current path in the hierarchy
            keywords (dict): Dictionary of keywords and their children
            depth (int): Current depth in the tree
            prefix (str): Prefix for the current line
            
        Returns:
            str: Formatted tree string
        """
        if not path and depth == 0:
            output = "Keyword Taxonomy:\n"
        else:
            output = ""
            
        # Sort keywords alphabetically
        sorted_keywords = sorted(keywords.keys())
        
        for i, keyword in enumerate(sorted_keywords):
            is_last = i == len(sorted_keywords) - 1
            
            # Determine the branch character
            if depth == 0:
                branch = "├── " if not is_last else "└── "
                next_prefix = "│   " if not is_last else "    "
            else:
                branch = prefix + ("├── " if not is_last else "└── ")
                next_prefix = prefix + ("│   " if not is_last else "    ")
            
            # Add the keyword with count if available
            if isinstance(keywords[keyword], int):
                count = keywords[keyword]
                output += f"{branch}{keyword} ({count} cheatsheet{'s' if count != 1 else ''})\n"
            else:
                output += f"{branch}{keyword}\n"
                
                # Recursively add children if any
                if isinstance(keywords[keyword], dict) and keywords[keyword]:
                    # This is normally where we'd recurse, but since we're simulating,
                    # we'll just add a placeholder
                    output += next_prefix + "...\n"
        
        return output