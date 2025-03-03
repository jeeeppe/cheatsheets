#!/usr/bin/env python3
"""
Cheat Sheet Collection CLI Tool

A simple command-line tool to manage a personal collection of text-based cheat sheets.
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime
import shutil

# Configuration
DEFAULT_STORAGE_PATH = os.path.expanduser("~/.cheatsheets.json")
DEFAULT_STORAGE_STRUCTURE = {"cheatsheets": []}


class CheatSheetManager:
    """Manages operations on the cheat sheet collection."""

    def __init__(self, storage_path=DEFAULT_STORAGE_PATH):
        """Initialize the CheatSheetManager with the storage path."""
        self.storage_path = storage_path
        self.cheatsheets = self._load_cheatsheets()

    def _load_cheatsheets(self):
        """Load cheatsheets from the storage file or create if it doesn't exist."""
        try:
            if not os.path.exists(self.storage_path):
                with open(self.storage_path, "w") as f:
                    json.dump(DEFAULT_STORAGE_STRUCTURE, f, indent=2)
                return DEFAULT_STORAGE_STRUCTURE
            
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.storage_path}")
            return DEFAULT_STORAGE_STRUCTURE
        except Exception as e:
            print(f"Error loading cheatsheets: {str(e)}")
            return DEFAULT_STORAGE_STRUCTURE

    def _save_cheatsheets(self):
        """Save cheatsheets to the storage file."""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.cheatsheets, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving cheatsheets: {str(e)}")
            return False

    def add_cheatsheet(self, name, content, categories=None, description=None):
        """Add a new cheat sheet to the collection."""
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

        # Add to collection and save
        self.cheatsheets["cheatsheets"].append(new_cheatsheet)
        return self._save_cheatsheets()

    def list_cheatsheets(self, category=None):
        """List available cheat sheets, optionally filtered by category."""
        cheatsheets = self.cheatsheets["cheatsheets"]
        
        if category:
            cheatsheets = [cs for cs in cheatsheets if category in cs["categories"]]
            
        if not cheatsheets:
            print("No cheat sheets found." + (f" (Category: {category})" if category else ""))
            return []
        
        return cheatsheets

    def get_cheatsheet(self, name):
        """Get a specific cheat sheet by name."""
        for cs in self.cheatsheets["cheatsheets"]:
            if cs["name"] == name:
                return cs
        return None

    def search_cheatsheets(self, query):
        """Search for cheat sheets by name, category, or content."""
        results = []
        query = query.lower()
        
        for cs in self.cheatsheets["cheatsheets"]:
            # Search in name
            if query in cs["name"].lower():
                results.append(cs)
                continue
                
            # Search in categories
            if any(query in cat.lower() for cat in cs["categories"]):
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

    def remove_cheatsheet(self, name):
        """Remove a cheat sheet from the collection."""
        initial_count = len(self.cheatsheets["cheatsheets"])
        self.cheatsheets["cheatsheets"] = [
            cs for cs in self.cheatsheets["cheatsheets"] if cs["name"] != name
        ]
        
        if len(self.cheatsheets["cheatsheets"]) == initial_count:
            print(f"Error: Cheat sheet '{name}' not found.")
            return False
            
        return self._save_cheatsheets()

    def export_cheatsheet(self, name, file_path=None):
        """Export a cheat sheet to a file."""
        cheatsheet = self.get_cheatsheet(name)
        if not cheatsheet:
            print(f"Error: Cheat sheet '{name}' not found.")
            return False
            
        try:
            if file_path:
                with open(file_path, "w") as f:
                    f.write(cheatsheet["content"])
                return True
            else:
                print(cheatsheet["content"])
                return True
        except Exception as e:
            print(f"Error exporting cheat sheet: {str(e)}")
            return False


class DisplayFormatter:
    """Handles formatting and displaying cheat sheets in the terminal."""
    
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
        output = f"{'Name':<{name_width}} {'Categories':<20} {'Description'}\n"
        output += f"{'-' * name_width} {'-' * 20} {'-' * desc_width}\n"
        
        # Rows
        for cs in cheatsheets:
            categories = ", ".join(cs["categories"])
            if len(categories) > 20:
                categories = categories[:17] + "..."
                
            description = cs["description"]
            if len(description) > desc_width:
                description = description[:desc_width-3] + "..."
                
            output += f"{cs['name']:<{name_width}} {categories:<20} {description}\n"
            
        return output
    
    @staticmethod
    def format_cheatsheet_content(cheatsheet):
        """Format a cheat sheet's content for display, with basic markdown rendering."""
        if not cheatsheet:
            return "Cheat sheet not found."
            
        output = f"# {cheatsheet['name']}\n\n"
        if cheatsheet["description"]:
            output += f"{cheatsheet['description']}\n\n"
            
        if cheatsheet["categories"]:
            output += f"Categories: {', '.join(cheatsheet['categories'])}\n\n"
            
        # Add the content
        output += "-------------------------------\n"
        output += cheatsheet["content"]
        output += "\n-------------------------------\n"
        
        return output


def parse_args():
    """Parse command line arguments."""
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
    add_parser.add_argument("--categories", help="Comma-separated list of categories")
    add_parser.add_argument("--description", help="Short description of the cheat sheet")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available cheat sheets")
    list_parser.add_argument("--category", help="Filter cheat sheets by category")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Display a specific cheat sheet")
    show_parser.add_argument("name", help="Name of the cheat sheet to display")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for cheat sheets")
    search_parser.add_argument("query", help="Search query")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a cheat sheet")
    remove_parser.add_argument("name", help="Name of the cheat sheet to remove")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export a cheat sheet to a file")
    export_parser.add_argument("name", help="Name of the cheat sheet to export")
    export_parser.add_argument("--file", help="Path to the output file")
    
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
                
        # Parse categories
        categories = []
        if args.categories:
            categories = [cat.strip() for cat in args.categories.split(",")]
            
        # Add the cheat sheet
        success = manager.add_cheatsheet(
            args.name, content, categories, args.description
        )
        
        if success:
            print(f"Cheat sheet '{args.name}' added successfully.")
        return 0 if success else 1
        
    elif args.command == "list":
        cheatsheets = manager.list_cheatsheets(args.category)
        print(formatter.format_cheatsheet_list(cheatsheets))
        return 0
        
    elif args.command == "show":
        cheatsheet = manager.get_cheatsheet(args.name)
        if not cheatsheet:
            print(f"Error: Cheat sheet '{args.name}' not found.")
            return 1
            
        print(formatter.format_cheatsheet_content(cheatsheet))
        return 0
        
    elif args.command == "search":
        results = manager.search_cheatsheets(args.query)
        if not results:
            print(f"No cheat sheets found matching '{args.query}'.")
            return 0
            
        print(f"Found {len(results)} cheat sheet(s) matching '{args.query}':")
        print(formatter.format_cheatsheet_list(results))
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


if __name__ == "__main__":
    sys.exit(main())