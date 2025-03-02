# Cheat Sheet Collection

A command-line tool for managing and quickly accessing your personal collection of cheat sheets organized in a hierarchical category system.

## Features

- **Organize** your cheat sheets in a hierarchical category structure
- **Search** for cheat sheets with fuzzy matching for quick access
- **Support** for multiple file formats (Markdown, HTML, PNG, etc.)
- **Open** cheat sheets with their appropriate default applications
- **Manage** your collection with simple commands
- **Tab completion** for efficient navigation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cheatsheet-collection.git
cd cheatsheet-collection

# Install the package
pip install -e .

# For development
pip install -r requirements.txt
```

## Usage

### Basic Commands

```bash
# Search for cheat sheets
cheatsheet -s "reverse shells"

# View a specific cheat sheet
cheatsheet view hacking/exploits/shells/reverse_shell_oneliners.html

# List categories
cheatsheet list

# Add a new cheat sheet
cheatsheet add ~/path/to/my_cheatsheet.md -c programming/python

# Add a new category
cheatsheet add-category security/network

# Remove a cheat sheet or category
cheatsheet remove hacking/outdated-technique.md
```

### Tab Completion

The tool supports tab completion for categories and commands:

```bash
cheatsheet exploi<TAB>
# Expands to show matching categories:
# - exploits
#   - shells - zero-day
#     - python3 - python2 - php
```

## Project Structure

For detailed information about the project architecture and design, see:

- [Architecture Documentation](architecture.md)
- [Development Workflow](workflow.md)

## Contributing

Contributions are welcome! Please check the [workflow document](workflow.md) for development guidelines.

## License

[MIT License](LICENSE)
