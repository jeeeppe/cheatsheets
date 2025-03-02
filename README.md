# Cheat Sheet Collection CLI Tool

A simple command-line tool to manage a personal collection of text-based cheat sheets. The tool stores cheat sheet content directly in a JSON file, making the collection portable and self-contained.

## Features

- Store cheat sheets directly in a JSON file in your home directory
- Add cheat sheets from files or standard input
- Organize cheat sheets with categories (tags)
- Search functionality to find cheat sheets by name, category, or content
- Display cheat sheets directly in the terminal
- Export cheat sheets to files

## Installation

### Requirements

- Python 3.6+ (Recommended: Python 3.13.2)
- No external dependencies (uses only the Python standard library)

### Setup

1. Clone or download the repository:

```bash
git clone https://github.com/yourusername/cheatsheet-cli.git
cd cheatsheet-cli
```

2. Make the script executable:

```bash
chmod +x cheatsheet.py
```

3. Create a symbolic link to make it available system-wide (optional):

```bash
ln -s "$(pwd)/cheatsheet.py" /usr/local/bin/cheatsheet
```

### Using UV (Optional)

If you prefer to use a virtual environment with UV:

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install for development (if needed)
pip install -e .
```

## Usage

### Adding a Cheat Sheet

From a file:

```bash
cheatsheet add --file path/to/file.md --name git_commands --categories git,version-control --description "Common Git commands"
```

From standard input:

```bash
echo "# My Notes" | cheatsheet add --stdin --name my_notes --categories notes,personal
```

Or interactively:

```bash
cat > temp.md << EOF
# Bash Commands

- ls: List directory contents
- cd: Change directory
- pwd: Print working directory
EOF

cheatsheet add --file temp.md --name bash_commands --categories bash,terminal
rm temp.md
```

### Listing Cheat Sheets

List all:

```bash
cheatsheet list
```

Filter by category:

```bash
cheatsheet list --category git
```

### Viewing a Cheat Sheet

```bash
cheatsheet show bash_commands
```

### Searching

```bash
cheatsheet search "directory"
```

This will search in names, categories, descriptions, and content.

### Removing a Cheat Sheet

```bash
cheatsheet remove bash_commands
```

### Exporting a Cheat Sheet

To a file:

```bash
cheatsheet export bash_commands --file ~/bash_commands.md
```

To standard output:

```bash
cheatsheet export bash_commands
```

## Storage

Cheat sheets are stored in a JSON file at `~/.cheatsheets.json`. The structure is:

```json
{
  "cheatsheets": [
    {
      "name": "bash_commands",
      "content": "# Bash Commands\n\n- ls: list directory\n- cd: change directory\n...",
      "categories": ["bash", "terminal", "commands"],
      "description": "Common bash commands",
      "created_at": "2025-03-02T12:00:00",
      "updated_at": "2025-03-02T12:00:00"
    }
  ]
}
```

## Examples

### Create a Git cheat sheet:

```bash
cat > git.md << EOF
# Git Quick Reference

## Basic Commands
- git init - Initialize a new repository
- git clone <url> - Clone a repository
- git add <file> - Add file to staging
- git commit -m "message" - Commit changes
- git push - Push changes to remote
- git pull - Pull changes from remote

## Branching
- git branch - List branches
- git branch <name> - Create a branch
- git checkout <branch> - Switch to branch
- git merge <branch> - Merge branch into current branch
EOF

cheatsheet add --file git.md --name git_commands --categories git,version-control --description "Common Git commands"
rm git.md
```

### Create a Python cheat sheet:

```bash
cat > python.md << EOF
# Python Quick Reference

## Data Types
- int: Integer numbers
- float: Floating-point numbers
- str: Text strings
- list: Ordered collections
- dict: Key-value stores
- tuple: Immutable sequences
- set: Unordered unique elements

## Control Flow
```python
# If statement
if condition:
    do_something()
elif other_condition:
    do_something_else()
else:
    do_default()

# For loop
for item in iterable:
    process(item)

# While loop
while condition:
    do_something()
```
EOF

cheatsheet add --file python.md --name python_basics --categories python,programming --description "Python basics reference"
rm python.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.