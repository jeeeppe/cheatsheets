# Hierarchical Keyword System Architecture

This document describes the architecture and implementation details of the hierarchical keyword system for the Cheatsheet CLI tool.

## Overview

The hierarchical keyword system organizes cheatsheets in a tree-like structure, allowing for more precise categorization and efficient searching. Each cheatsheet is assigned a path from the root of the taxonomy to a specific leaf node, enabling intuitive navigation and filtering.

## Data Structure

### JSON Storage Format

The system extends the existing JSON storage with two key additions:

1. **Keyword Path**: Each cheatsheet has a `keyword_path` array that contains the full path from root to leaf
2. **Keyword Taxonomy**: A nested object structure that represents the entire taxonomy hierarchy

```json
{
  "cheatsheets": [
    {
      "name": "pandas_syntax_and_tricks",
      "content": "...",
      "categories": ["python", "data"],  // Maintained for backward compatibility
      "keyword_path": ["Computers", "Programming", "Python", "Python Libraries", "Data Processing", "Pandas"],
      "description": "...",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "keyword_taxonomy": {
    "Computers": {
      "Programming": {
        "Python": {
          "Python Libraries": {
            "Data Processing": {
              "Pandas": {},
              "NumPy": {}
            }
          }
        }
      }
    }
  }
}
```

### Backward Compatibility

The system maintains backward compatibility with the existing flat category system:

- The `categories` array is preserved for all cheatsheets
- Legacy search by category continues to work
- Existing cheatsheets can be migrated to the hierarchical system using the migration tools

## Core Components

### CheatSheetManager Extensions

The `CheatSheetManager` class has been extended with methods to support the hierarchical keyword system:

- `add_cheatsheet()`: Updated to accept and store a keyword path
- `_ensure_keyword_path_exists()`: Creates missing nodes in the taxonomy
- `get_keyword_children()`: Lists child keywords at a given path
- `search_by_keyword_path()`: Searches for cheatsheets matching a path
- `search_cheatsheets()`: Enhanced to optionally filter by keyword path
- `list_keywords()`: Lists keywords at a given path with optional counts
- `migrate_categories_to_paths()`: Migrates legacy categories to keyword paths

### SearchEngine

A new `SearchEngine` class provides advanced search capabilities:

- `fuzzy_search()`: Finds close matches using string similarity algorithms
- `semantic_search()`: Uses TF-IDF to rank results by relevance
- `full_text_search()`: Uses an inverted index for efficient text search
- `basic_search()`: Falls back to the original search method

### MigrationTool

The `MigrationTool` class assists in migrating from flat categories to hierarchical keywords:

- `suggest_hierarchy()`: Analyzes existing categories to suggest a hierarchical structure
- `apply_suggested_hierarchy()`: Applies the suggested hierarchy to cheatsheets
- `suggest_keyword_path()`: Suggests a path for a single cheatsheet
- `batch_migrate()`: Migrates multiple cheatsheets with optional interactive confirmation

### DisplayFormatter Extensions

The `DisplayFormatter` class has been enhanced to display hierarchical information:

- `format_cheatsheet_list()`: Updated to show keyword paths
- `format_cheatsheet_content()`: Enhanced to display the full path
- `format_keyword_list()`: Displays keywords at a specific path
- `format_keyword_tree()`: Visualizes the taxonomy as a tree

## CLI Interface

The command-line interface has been extended with several new commands and options:

### New Commands

- `keywords`: Browse and manage the keyword taxonomy
  - `path`: Specify a path to list (comma-separated)
  - `--count`: Show count of cheatsheets under each keyword
  - `--tree`: Display as a tree
  - `--rename`: Rename a keyword
  - `--merge`: Merge one keyword into another

- `migrate`: Migrate legacy categories to hierarchical keywords
  - `--root`: Specify the root keyword for migrated categories
  - `--dry-run`: Show what would be migrated without making changes

### Enhanced Commands

- `add`: Enhanced with `--keywords` option to specify a hierarchical path
- `list`: Enhanced with `--keywords` option to filter by path
- `search`: Enhanced with `--keywords` option to restrict search to a path

## Search Mechanisms

The system implements several search mechanisms to efficiently find cheatsheets:

### 1. Hierarchical Filtering

Filtering by keyword path allows users to narrow down results by navigating the taxonomy hierarchy. This is particularly useful when the collection contains thousands of cheatsheets.

### 2. Fuzzy Matching

Fuzzy matching uses string similarity algorithms to find close matches to the search query, accommodating typos and minor variations in spelling.

### 3. Semantic Search

Semantic search uses TF-IDF (Term Frequency-Inverse Document Frequency) to rank results by relevance, considering word importance rather than just presence.

### 4. Full-Text Search

Full-text search uses an inverted index for efficient content searching, similar to how search engines operate.

### 5. Hybrid Approaches

The system can combine multiple search techniques, such as:
- First filtering by keyword path, then applying semantic search
- Using fuzzy matching for keyword paths and exact matching for content
- Boosting results that match in multiple fields (name, description, content)

## Handling Edge Cases

### Synonyms and Aliases

To handle synonyms and aliases (e.g., "AI" vs. "Artificial Intelligence"), the system could be extended with:

1. A synonym mapping table in the JSON structure
2. Automatic expansion of search queries to include synonyms
3. Suggestions when adding new cheatsheets ("Did you mean: Artificial Intelligence?")

### Path Conflicts and Migrations

When migrating or reorganizing the taxonomy, conflicts may arise. The system handles these with:

1. Interactive confirmation for significant changes
2. Batch operations with previews and dry runs
3. Path validation to ensure consistency

### Performance Considerations

For large collections with thousands of cheatsheets, performance optimizations include:

1. Inverted indices for text search
2. Caching of common queries and paths
3. Lazy loading of cheatsheet content when displaying lists

## Future Enhancements

### 1. Advanced Visualization

- Interactive tree visualization for the web interface
- Graph representation showing relationships between keywords

### 2. AI-Assisted Categorization

- Automatic suggestion of keyword paths based on content analysis
- Clustering of similar cheatsheets to identify potential new categories

### 3. User Preferences and Personalization

- Personal favorite paths for quick access
- Usage-based recommendations

### 4. Database Backend

- SQLite or other database backend for improved performance with large collections
- Full-text search capabilities of modern databases

## Conclusion

The hierarchical keyword system significantly enhances the organization and searchability of cheatsheets, making it easier to manage thousands of entries while maintaining a clean, intuitive interface. The design balances power with simplicity, ensuring that users can find what they need quickly without being overwhelmed by complexity.