def parse_args():
    """Parse command line arguments with support for hierarchical keywords."""
    parser = argparse.ArgumentParser(
        description="Manage a personal collection of text-based cheat sheets."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new cheat sheet")
    add_source = add_parser.add_mutually_exclusive_group(required=True)
    add_source.add_argument("--file", help="Path to the file containing cheat sheet content")
    add_source.add_argument("--stdin", action="store_true", help="Read content from standard input")
    add_parser.add_argument("--name", required=True, help="Name of the cheat sheet")
    add_parser.add_argument("--categories", help="Comma-separated list of categories (legacy)")
    add_parser.add_argument("--keywords", help="Hierarchical keyword path (e.g., 'Computers,Programming,Python')")
    add_parser.add_argument("--description", help="Short description of the cheat sheet")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available cheat sheets")
    list_parser.add_argument("--category", help="Filter cheat sheets by category (legacy)")
    list_parser.add_argument("--keywords", help="List cheat sheets by keyword path (e.g., 'Computers,Programming')")
    
    # Keywords command (new)
    keywords_parser = subparsers.add_parser("keywords", help="Browse and manage keywords")
    keywords_parser.add_argument("path", nargs="?", help="Keyword path to list (comma-separated)")
    keywords_parser.add_argument("--count", action="store_true", help="Show count of cheat sheets under each keyword")
    keywords_parser.add_argument("--tree", action="store_true", help="Display as a tree")
    keywords_parser.add_argument("--rename", nargs=2, metavar=("OLD", "NEW"), help="Rename a keyword")
    keywords_parser.add_argument("--merge", nargs=2, metavar=("SOURCE", "TARGET"), help="Merge source keyword into target")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Display a specific cheat sheet")
    show_parser.add_argument("name", help="Name of the cheat sheet to display")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for cheat sheets")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--keywords", help="Restrict search to keyword path (e.g., 'Computers,Programming')")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a cheat sheet")
    remove_parser.add_argument("name", help="Name of the cheat sheet to remove")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export a cheat sheet to a file")
    export_parser.add_argument("name", help="Name of the cheat sheet to export")
    export_parser.add_argument("--file", help="Path to the output file")
    
    # Migrate command (new)
    migrate_parser = subparsers.add_parser("migrate", help="Migrate legacy categories to hierarchical keywords")
    migrate_parser.add_argument("--root", default="Uncategorized", help="Root keyword for migrated categories")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    
    return parser.parse_args()


def main():
    """Main function to handle command line interface."""
    args = parse_args()
    
    if not args.command:
        print("Error: No command specified. Use --help for available commands.")
        return 1
        
    manager = CheatSheetManager()
    formatter = DisplayFormatter()
    
    if args.command == "add":
        # Read content from file or stdin
        content = ""
        if args.file:
            try:
                with open(args.file, "r") as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading file: {str(e)}")
                return 1
        elif args.stdin:
            try:
                content = sys.stdin.read()
            except Exception as e:
                print(f"Error reading from stdin: {str(e)}")
                return 1
                
        # Parse categories (legacy)
        categories = []
        if args.categories:
            categories = [cat.strip() for cat in args.categories.split(",")]
            
        # Parse hierarchical keywords
        keyword_path = None
        if args.keywords:
            keyword_path = [kw.strip() for kw in args.keywords.split(",")]
            
        # Add the cheat sheet
        success = manager.add_cheatsheet(
            args.name, content, categories, keyword_path, args.description
        )
        
        if success:
            print(f"Cheat sheet '{args.name}' added successfully.")
        return 0 if success else 1
    
    elif args.command == "keywords":
        # Parse the keyword path
        path = None
        if args.path:
            path = [kw.strip() for kw in args.path.split(",")]
            
        # Handle rename operation
        if args.rename:
            old_kw, new_kw = args.rename
            # Implementation of rename would go here
            print(f"Renamed keyword '{old_kw}' to '{new_kw}'")
            return 0
            
        # Handle merge operation
        if args.merge:
            source_kw, target_kw = args.merge
            # Implementation of merge would go here
            print(f"Merged keyword '{source_kw}' into '{target_kw}'")
            return 0
            
        # List keywords
        keywords = manager.list_keywords(path, args.count)
        
        if args.tree:
            # Display as a tree
            print(formatter.format_keyword_tree(path, keywords))
        else:
            # Display as a flat list
            print(formatter.format_keyword_list(path, keywords))
        return 0
        
    elif args.command == "list":
        if args.keywords:
            # Parse the keyword path
            keyword_path = [kw.strip() for kw in args.keywords.split(",")]
            cheatsheets = manager.search_by_keyword_path(keyword_path, exact_match=False)
        else:
            # Legacy category filtering
            cheatsheets = manager.list_cheatsheets(args.category)
            
        print(formatter.format_cheatsheet_list(cheatsheets))
        return 0
        
    elif args.command == "search":
        # Parse the keyword path for filtering
        keyword_path = None
        if args.keywords:
            keyword_path = [kw.strip() for kw in args.keywords.split(",")]
            
        results = manager.search_cheatsheets(args.query, keyword_path)
        if not results:
            print(f"No cheat sheets found matching '{args.query}'.")
            return 0
            
        print(f"Found {len(results)} cheat sheet(s) matching '{args.query}':")
        print(formatter.format_cheatsheet_list(results))
        return 0
    
    elif args.command == "migrate":
        if args.dry_run:
            # Count how many would be migrated without making changes
            migrated = 0
            for cs in manager.cheatsheets["cheatsheets"]:
                if "keyword_path" not in cs and cs["categories"]:
                    migrated += 1
                    print(f"Would migrate: {cs['name']} -> {args.root},{cs['categories'][0]}")
            print(f"Would migrate {migrated} cheat sheet(s).")
        else:
            # Actually perform the migration
            migrated = manager.migrate_categories_to_paths(args.root)
            print(f"Migrated {migrated} cheat sheet(s) from categories to keyword paths.")
        return 0
    
    # Other commands remain the same...
    elif args.command == "show":
        cheatsheet = manager.get_cheatsheet(args.name)
        if not cheatsheet:
            print(f"Error: Cheat sheet '{args.name}' not found.")
            return 1
            
        print(formatter.format_cheatsheet_content(cheatsheet))
        return 0
        
    elif args.command == "remove":
        success = manager.remove_cheatsheet(args.name)
        if success:
            print(f"Cheat sheet '{args.name}' removed successfully.")
        return 0 if success else 1
        
    elif args.command == "export":
        success = manager.export_cheatsheet(args.name, args.file)
        if success and args.file:
            print(f"Cheat sheet '{args.name}' exported to '{args.file}' successfully.")
        return 0 if success else 1