"""
Main module for the Cheat Sheet Collection CLI.

This module provides the command-line interface for the application.
"""
import os
import sys
from pathlib import Path
from typing import Optional

import click

from .category import CategoryManager, CheatSheet
from .data_manager import JsonDataManager
from .search import SearchEngine
from .viewer import CheatSheetViewer
from .utils import (
    get_file_format,
    get_user_data_dir,
    normalize_path,
    split_path,
    format_search_results
)


# Initialize the data manager
DATA_DIR = get_user_data_dir()
DATA_FILE = DATA_DIR / 'cheatsheets.json'
data_manager = JsonDataManager(DATA_FILE)


@click.group(invoke_without_command=True)
@click.option('-s', '--search', help='Search for cheat sheets')
@click.option('-v', '--view', help='View a specific cheat sheet')
@click.option('-l', '--list', is_flag=True, help='List all categories')
@click.pass_context
def cli(ctx, search, view, list):
    """
    Cheat Sheet Collection CLI.
    
    Manage and access your personal collection of cheat sheets.
    """
    # If no command is provided, show help
    if ctx.invoked_subcommand is None and not (search or view or list):
        click.echo(ctx.get_help())
        return
        
    # Handle the -s/--search option
    if search:
        search_cheatsheets(search)
        return
        
    # Handle the -v/--view option
    if view:
        view_cheatsheet(view)
        return
        
    # Handle the -l/--list option
    if list:
        list_categories()
        return


@cli.command()
@click.argument('query')
def search(query):
    """Search for cheat sheets matching QUERY."""
    search_cheatsheets(query)


def search_cheatsheets(query: str):
    """
    Search for cheat sheets and display results.
    
    Args:
        query: Search query
    """
    manager = data_manager.load()
    engine = SearchEngine(manager)
    results = engine.search(query)
    
    if not results:
        click.echo("No matching cheat sheets found.")
        return
        
    click.echo(f"Search results for '{query}':")
    click.echo(format_search_results(results))


@cli.command()
@click.argument('path')
def view(path):
    """View a specific cheat sheet at PATH."""
    view_cheatsheet(path)


def view_cheatsheet(path: str):
    """
    Open a cheat sheet with the appropriate viewer.
    
    Args:
        path: Path to the cheat sheet
    """
    manager = data_manager.load()
    category_path, cheatsheet_name = split_path(path)
    
    if not cheatsheet_name:
        click.echo(f"Error: Invalid path '{path}'")
        return
        
    category = manager.get_category(category_path)
    if not category:
        click.echo(f"Error: Category not found '{category_path}'")
        return
        
    # Find the cheat sheet
    cheatsheet = None
    for cs in category.cheatsheets:
        if cs.name == cheatsheet_name:
            cheatsheet = cs
            break
            
    if not cheatsheet:
        click.echo(f"Error: Cheat sheet not found '{cheatsheet_name}'")
        return
        
    # Open the cheat sheet
    viewer = CheatSheetViewer()
    success = viewer.view(cheatsheet.path)
    
    if not success:
        click.echo(f"Error: Failed to open cheat sheet '{cheatsheet.path}'")


@cli.command('list')
@click.argument('category', required=False)
def list_command(category):
    """List categories or cheat sheets in CATEGORY."""
    if category:
        list_cheatsheets(category)
    else:
        list_categories()


def list_categories():
    """List all top-level categories."""
    manager = data_manager.load()
    
    if not manager.root_categories:
        click.echo("No categories found.")
        return
        
    click.echo("Categories:")
    for name in sorted(manager.root_categories.keys()):
        click.echo(f"- {name}")


def list_cheatsheets(category_path: str):
    """
    List cheat sheets in a category.
    
    Args:
        category_path: Path to the category
    """
    manager = data_manager.load()
    category = manager.get_category(normalize_path(category_path))
    
    if not category:
        click.echo(f"Error: Category not found '{category_path}'")
        return
        
    click.echo(f"Category: {category_path}")
    
    if category.subcategories:
        click.echo("\nSubcategories:")
        for name in sorted(category.subcategories.keys()):
            click.echo(f"- {name}")
            
    if category.cheatsheets:
        click.echo("\nCheat sheets:")
        for cs in sorted(category.cheatsheets, key=lambda x: x.name):
            click.echo(f"- {cs.name} ({cs.format})")
    elif not category.subcategories:
        click.echo("\nNo cheat sheets or subcategories found.")


@cli.command()
@click.argument('file_path')
@click.option('-c', '--category', help='Category path')
@click.option('-t', '--tags', help='Comma-separated tags')
def add(file_path, category, tags):
    """
    Add a new cheat sheet.
    
    FILE_PATH is the path to the cheat sheet file.
    """
    # Check if the file exists
    path = Path(file_path)
    if not path.exists():
        click.echo(f"Error: File not found '{file_path}'")
        return
        
    # Get the category
    manager = data_manager.load()
    
    if not category:
        category = click.prompt("Enter category path")
        
    category_path = normalize_path(category)
    category_obj = manager.get_category(category_path)
    
    if not category_obj:
        create = click.confirm(f"Category '{category_path}' does not exist. Create it?")
        if not create:
            return
            
        # Create the category
        parts = category_path.split('/')
        current_path = ""
        current_category = None
        
        for i, part in enumerate(parts):
            current_path = f"{current_path}/{part}" if current_path else part
            temp_category = manager.get_category(current_path)
            
            if not temp_category:
                if i == 0:
                    # Root category
                    current_category = manager.add_root_category(part)
                else:
                    # Subcategory
                    current_category = current_category.add_subcategory(part)
            else:
                current_category = temp_category
                
        category_obj = current_category
        
    # Get the file format
    format = get_file_format(file_path)
    
    # Get the cheat sheet name
    default_name = path.stem
    name = click.prompt("Enter cheat sheet name", default=default_name)
    
    # Get tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
    else:
        tags_input = click.prompt("Enter tags (comma-separated)", default="")
        if tags_input:
            tag_list = [tag.strip() for tag in tags_input.split(',')]
            
    # Create the cheat sheet
    cheatsheet = CheatSheet(
        name=name,
        path=str(path.absolute()),
        format=format,
        tags=tag_list
    )
    
    # Add the cheat sheet to the category
    try:
        category_obj.add_cheatsheet(cheatsheet)
    except ValueError as e:
        click.echo(f"Error: {e}")
        return
        
    # Save the changes
    success = data_manager.save(manager)
    
    if success:
        click.echo(f"Added cheat sheet '{name}' to category '{category_path}'")
    else:
        click.echo("Error: Failed to save changes")


@cli.command('add-category')
@click.argument('category_path')
def add_category(category_path):
    """Add a new category at CATEGORY_PATH."""
    manager = data_manager.load()
    path = normalize_path(category_path)
    
    # Check if the category already exists
    existing = manager.get_category(path)
    if existing:
        click.echo(f"Error: Category already exists '{path}'")
        return
        
    # Create the category hierarchy
    parts = path.split('/')
    current_path = ""
    current_category = None
    
    for i, part in enumerate(parts):
        current_path = f"{current_path}/{part}" if current_path else part
        temp_category = manager.get_category(current_path)
        
        if not temp_category:
            if i == 0:
                # Root category
                current_category = manager.add_root_category(part)
            else:
                # Subcategory
                current_category = current_category.add_subcategory(part)
        else:
            current_category = temp_category
            
    # Save the changes
    success = data_manager.save(manager)
    
    if success:
        click.echo(f"Added category '{path}'")
    else:
        click.echo("Error: Failed to save changes")


@cli.command()
@click.argument('path')
@click.option('--force', is_flag=True, help='Force removal without confirmation')
def remove(path, force):
    """
    Remove a cheat sheet or category at PATH.
    
    Use --force to skip confirmation.
    """
    manager = data_manager.load()
    normalized_path = normalize_path(path)
    
    # Check if it's a cheat sheet or a category
    category_path, cheatsheet_name = split_path(normalized_path)
    
    if cheatsheet_name:
        # It's a cheat sheet
        remove_cheatsheet(manager, category_path, cheatsheet_name, force)
    else:
        # It's a category
        remove_category(manager, normalized_path, force)
        
    # Save the changes
    success = data_manager.save(manager)
    
    if not success:
        click.echo("Error: Failed to save changes")


def remove_cheatsheet(manager: CategoryManager, category_path: str, cheatsheet_name: str, force: bool):
    """
    Remove a cheat sheet.
    
    Args:
        manager: CategoryManager instance
        category_path: Path to the category
        cheatsheet_name: Name of the cheat sheet
        force: Whether to skip confirmation
    """
    category = manager.get_category(category_path)
    
    if not category:
        click.echo(f"Error: Category not found '{category_path}'")
        return
        
    # Find the cheat sheet
    cheatsheet = None
    for cs in category.cheatsheets:
        if cs.name == cheatsheet_name:
            cheatsheet = cs
            break
            
    if not cheatsheet:
        click.echo(f"Error: Cheat sheet not found '{cheatsheet_name}'")
        return
        
    # Confirm removal
    if not force:
        confirm = click.confirm(f"Remove cheat sheet '{cheatsheet_name}' from '{category_path}'?")
        if not confirm:
            return
            
    # Remove the cheat sheet
    category.cheatsheets.remove(cheatsheet)
    click.echo(f"Removed cheat sheet '{cheatsheet_name}' from '{category_path}'")


def remove_category(manager: CategoryManager, category_path: str, force: bool):
    """
    Remove a category.
    
    Args:
        manager: CategoryManager instance
        category_path: Path to the category
        force: Whether to skip confirmation
    """
    # Get the parent category and the category to remove
    parts = category_path.split('/')
    
    if len(parts) == 1:
        # It's a root category
        if parts[0] not in manager.root_categories:
            click.echo(f"Error: Category not found '{category_path}'")
            return
            
        # Confirm removal
        if not force:
            confirm = click.confirm(f"Remove category '{category_path}' and all its contents?")
            if not confirm:
                return
                
        # Remove the category
        del manager.root_categories[parts[0]]
        click.echo(f"Removed category '{category_path}'")
    else:
        # It's a subcategory
        parent_path = '/'.join(parts[:-1])
        category_name = parts[-1]
        
        parent = manager.get_category(parent_path)
        if not parent:
            click.echo(f"Error: Parent category not found '{parent_path}'")
            return
            
        if category_name not in parent.subcategories:
            click.echo(f"Error: Category not found '{category_path}'")
            return
            
        # Confirm removal
        if not force:
            confirm = click.confirm(f"Remove category '{category_path}' and all its contents?")
            if not confirm:
                return
                
        # Remove the category
        del parent.subcategories[category_name]
        click.echo(f"Removed category '{category_path}'")


if __name__ == '__main__':
    cli()
    