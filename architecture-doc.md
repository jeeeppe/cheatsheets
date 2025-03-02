# Cheat Sheet Collection - Architecture

## Overview
This document outlines the architectural design and structure of the Cheat Sheet Collection CLI tool. The tool allows users to organize, search, and access personal cheat sheets in various file formats through a hierarchical category system.

## Project Goals
- Create a fast and intuitive CLI tool for accessing personal cheat sheets
- Support various file formats (markdown, HTML, mermaid, PNG, TXT, etc.)
- Implement a flexible category hierarchy system for organization
- Provide fuzzy search capabilities to quickly find relevant cheat sheets
- Offer a simple way to add new cheat sheets and categories
- Handle cheat sheet viewing by opening files with appropriate default applications

## Technology Stack
- **Primary Language**: Python 3.13.1
- **CLI Framework**: Click or Typer (for command-line interface)
- **Search Engine**: Fuzzy matching with Python's `fuzzywuzzy` or similar
- **Data Storage**: JSON file or SQLite database
- **File Handling**: Python's standard library (`os`, `subprocess`)
- **Version Control**: Git

## Directory Structure
```
cheatsheet-collection/
├── README.md               # Project overview and getting started guide
├── architecture.md         # This document - architectural reference
├── workflow.md             # Development workflow guidelines
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # Entry point for CLI
│   ├── data_manager.py     # Handles data storage and retrieval
│   ├── category.py         # Category class and operations
│   ├── search.py           # Search functionality
│   ├── viewer.py           # File viewing functionality
│   └── utils.py            # Utility functions
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_data_manager.py
│   ├── test_category.py
│   ├── test_search.py
│   └── test_viewer.py
├── docs/                   # Detailed documentation
│   ├── usage.md            # Usage documentation
│   └── examples.md         # Example scenarios
├── sample_data/            # Sample cheat sheets for testing
│   ├── bash_commands/
│   ├── windows/
│   └── hacking/
├── requirements.txt        # Python dependencies
├── setup.py                # Package configuration for installation
└── .gitignore              # Git ignore configuration
```

## Key Components

### CLI Interface (main.py)
- Provides the command-line interface for user interaction
- Implements commands for searching, viewing, adding, and managing cheat sheets
- Handles command-line arguments and options
- Displays search results and category listings
- Implements tab completion for categories and search terms

### Data Manager (data_manager.py)
- Manages the storage and retrieval of category hierarchy and cheat sheet metadata
- Handles persistence of data to JSON file or SQLite database
- Provides CRUD operations for categories and cheat sheets
- Maintains indexes for efficient searching

### Category System (category.py)
- Implements the hierarchical category structure
- Manages relationships between categories and subcategories
- Provides navigation and traversal of the category tree
- Handles category path resolution

### Search Engine (search.py)
- Implements fuzzy searching across categories and cheat sheet names
- Ranks and sorts search results by relevance
- Handles partial matches and typos in search queries
- Provides filtering capabilities

### Viewer (viewer.py)
- Handles opening cheat sheets with appropriate applications
- Determines file type and launches corresponding viewer
- Manages process creation and cleanup

### Utilities (utils.py)
- Common utility functions
- Path handling and validation
- Configuration management
- Error handling utilities

## Data Flow
1. User inputs a command via CLI
2. CLI parses the command and options
3. For search requests:
   - Search engine queries the data manager for matching categories/cheat sheets
   - Results are ranked by relevance and displayed to the user
4. For view requests:
   - Data manager retrieves the file path
   - Viewer opens the file with appropriate application
5. For add/update requests:
   - Data manager updates the category structure
   - Changes are persisted to storage

## Data Storage
The hierarchical category structure will be stored in one of two ways:

### Option 1: JSON File Structure
```json
{
  "categories": {
    "bash_commands": {
      "subcategories": {},
      "cheatsheets": [
        {
          "name": "common_commands",
          "path": "/path/to/common_commands.md",
          "format": "markdown",
          "tags": ["bash", "terminal", "commands"]
        }
      ]
    },
    "hacking": {
      "subcategories": {
        "exploits": {
          "subcategories": {
            "shells": {
              "subcategories": {},
              "cheatsheets": [
                {
                  "name": "reverse_shell_oneliners",
                  "path": "/path/to/reverse_shell_oneliners.html",
                  "format": "html",
                  "tags": ["reverse", "shell", "oneliners"]
                }
              ]
            }
          },
          "cheatsheets": []
        }
      },
      "cheatsheets": []
    }
  }
}
```

### Option 2: SQLite Database Schema
Three main tables:
1. `categories` - Stores category information and hierarchical relationships
2. `cheatsheets` - Stores cheat sheet metadata
3. `tags` - Stores tags for improved searching

## Error Handling Strategy
- Custom exceptions for different error scenarios
- Clear error messages for user-facing issues
- Proper logging for debugging
- Graceful handling of file access issues or missing dependencies

## Testing Strategy
- Unit tests for individual components
- Integration tests for component interactions
- CLI tests using subprocess
- Mock tests for file system operations
- Test coverage of edge cases like:
  - Deep category nesting
  - Special characters in search
  - Missing files
  - Various file formats

## Command-line Interface Design
```
cheatsheet [COMMAND] [OPTIONS] [ARGS]
```

Commands:
- `search` (or `-s`): Search for cheat sheets
- `view` (or `-v`): View a specific cheat sheet
- `add`: Add a new cheat sheet
- `add-category`: Add a new category
- `list` (or `-l`): List categories or cheat sheets
- `remove`: Remove a cheat sheet or category

Examples:
```
cheatsheet -s "reverse shells"
cheatsheet view hacking/exploits/shells/reverse_shell_oneliners.html
cheatsheet add my_new_cheatsheet.md -c programming/python
cheatsheet list hacking/exploits
```

## Performance Considerations
- Efficient category traversal for deep hierarchies
- Optimized search algorithm for quick results
- Caching strategies for frequently accessed data
- Lazy loading of category tree elements

## Dependencies
- Click/Typer: For CLI interface and command parsing
- fuzzywuzzy: For fuzzy search capabilities
- python-Levenshtein (optional): For faster fuzzy matching
- sqlite3 (standard library): If using SQLite for storage
- pathlib (standard library): For path manipulation
- json (standard library): For JSON file handling

## Development Roadmap
1. Core functionality:
   - Basic category structure
   - Simple file storage (JSON)
   - Basic search capabilities
   - File viewing
   
2. Enhanced features:
   - Improved search with fuzzy matching
   - Tab completion
   - Category management
   - Tags support
   
3. Advanced features:
   - Database storage option
   - Configuration options
   - Import/export functionality
   - Search result caching

## Version History
| Version | Date | Description |
|---------|------|-------------|
| 0.1     | Current Date | Initial architecture draft |

---

This architecture document is a living reference and will be updated as the project evolves.
