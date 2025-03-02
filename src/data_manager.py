"""
Data Manager module for the Cheat Sheet Collection.

This module handles the persistence of the category structure and
cheat sheet metadata to a storage backend (JSON file or SQLite database).
"""
import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .category import Category, CategoryManager, CheatSheet


class DataManager:
    """
    Abstract base class for data storage backends.
    
    Implementations should provide methods for loading, saving,
    and querying the category structure.
    """
    def load(self) -> CategoryManager:
        """
        Load the category structure from storage.
        
        Returns:
            The loaded CategoryManager
        """
        raise NotImplementedError
        
    def save(self, manager: CategoryManager) -> bool:
        """
        Save the category structure to storage.
        
        Args:
            manager: The CategoryManager to save
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError
        
    def get_cheatsheet_path(self, category_path: str, cheatsheet_name: str) -> Optional[str]:
        """
        Get the file system path for a specific cheat sheet.
        
        Args:
            category_path: Path to the category
            cheatsheet_name: Name of the cheat sheet
            
        Returns:
            The file system path if found, None otherwise
        """
        raise NotImplementedError


class JsonDataManager(DataManager):
    """
    Data manager implementation using a JSON file for storage.
    """
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize the JSON data manager.
        
        Args:
            file_path: Path to the JSON file
        """
        self.file_path = Path(file_path)
        self._ensure_data_file()
        
    def _ensure_data_file(self) -> None:
        """Ensure the data file exists."""
        if not self.file_path.exists():
            # Create parent directories if they don't exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create an empty data structure
            empty_data = {"categories": {}}
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(empty_data, f, indent=2)
        
    def load(self) -> CategoryManager:
        """
        Load the category structure from the JSON file.
        
        Returns:
            The loaded CategoryManager
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return CategoryManager.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError):
            # Return an empty manager if the file doesn't exist or is invalid
            return CategoryManager()
        
    def save(self, manager: CategoryManager) -> bool:
        """
        Save the category structure to the JSON file.
        
        Args:
            manager: The CategoryManager to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(manager.to_dict(), f, indent=2)
            return True
        except (IOError, OSError):
            return False
        
    def get_cheatsheet_path(self, category_path: str, cheatsheet_name: str) -> Optional[str]:
        """
        Get the file system path for a specific cheat sheet.
        
        Args:
            category_path: Path to the category
            cheatsheet_name: Name of the cheat sheet
            
        Returns:
            The file system path if found, None otherwise
        """
        manager = self.load()
        category = manager.get_category(category_path)
        
        if category is None:
            return None
            
        for cs in category.cheatsheets:
            if cs.name == cheatsheet_name:
                return cs.path
                
        return None


class SqliteDataManager(DataManager):
    """
    Data manager implementation using a SQLite database for storage.
    
    This implementation provides more efficient querying capabilities
    for large collections.
    """
    def __init__(self, db_path: Union[str, Path]):
        """
        Initialize the SQLite data manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_database()
        
    def _ensure_database(self) -> None:
        """Ensure the database exists and has the correct schema."""
        # Create parent directories if they don't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cheatsheets (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                format TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                cheatsheet_id INTEGER NOT NULL,
                FOREIGN KEY (cheatsheet_id) REFERENCES cheatsheets(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _build_category_tree(self, cursor, parent_id=None) -> Dict[str, Category]:
        """
        Recursively build the category tree from the database.
        
        Args:
            cursor: SQLite cursor
            parent_id: ID of the parent category, or None for root categories
            
        Returns:
            Dictionary of Category objects keyed by name
        """
        categories = {}
        
        # Get categories with the specified parent
        if parent_id is None:
            cursor.execute("SELECT id, name FROM categories WHERE parent_id IS NULL")
        else:
            cursor.execute("SELECT id, name FROM categories WHERE parent_id = ?", (parent_id,))
            
        for cat_id, name in cursor.fetchall():
            # Create the category
            category = Category(name=name)
            
            # Get cheat sheets for this category
            cursor.execute("""
                SELECT id, name, path, format FROM cheatsheets 
                WHERE category_id = ?
            """, (cat_id,))
            
            for cs_id, cs_name, cs_path, cs_format in cursor.fetchall():
                # Get tags for this cheat sheet
                cursor.execute("""
                    SELECT name FROM tags 
                    WHERE cheatsheet_id = ?
                """, (cs_id,))
                
                tags = [tag[0] for tag in cursor.fetchall()]
                
                # Create the cheat sheet
                cheatsheet = CheatSheet(
                    name=cs_name,
                    path=cs_path,
                    format=cs_format,
                    tags=tags
                )
                
                category.cheatsheets.append(cheatsheet)
                
            # Recursively build subcategories
            subcategories = self._build_category_tree(cursor, cat_id)
            for subcat_name, subcat in subcategories.items():
                subcat.parent = category
                category.subcategories[subcat_name] = subcat
                
            categories[name] = category
            
        return categories
        
    def load(self) -> CategoryManager:
        """
        Load the category structure from the SQLite database.
        
        Returns:
            The loaded CategoryManager
        """
        manager = CategoryManager()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build the category tree
            root_categories = self._build_category_tree(cursor)
            manager.root_categories = root_categories
            
            conn.close()
            return manager
        except sqlite3.Error:
            # Return an empty manager if there's a database error
            return CategoryManager()
            
    def _save_category(self, cursor, category: Category, parent_id=None) -> int:
        """
        Recursively save a category and its subcategories to the database.
        
        Args:
            cursor: SQLite cursor
            category: The Category to save
            parent_id: ID of the parent category, or None for root categories
            
        Returns:
            The ID of the saved category
        """
        # Insert or update the category
        cursor.execute("""
            INSERT INTO categories (name, parent_id) VALUES (?, ?)
        """, (category.name, parent_id))
        
        category_id = cursor.lastrowid
        
        # Save cheat sheets
        for cs in category.cheatsheets:
            cursor.execute("""
                INSERT INTO cheatsheets (name, path, format, category_id)
                VALUES (?, ?, ?, ?)
            """, (cs.name, cs.path, cs.format, category_id))
            
            cheatsheet_id = cursor.lastrowid
            
            # Save tags
            for tag in cs.tags:
                cursor.execute("""
                    INSERT INTO tags (name, cheatsheet_id)
                    VALUES (?, ?)
                """, (tag, cheatsheet_id))
                
        # Recursively save subcategories
        for subcat in category.subcategories.values():
            self._save_category(cursor, subcat, category_id)
            
        return category_id
        
    def save(self, manager: CategoryManager) -> bool:
        """
        Save the category structure to the SQLite database.
        
        Args:
            manager: The CategoryManager to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM tags")
            cursor.execute("DELETE FROM cheatsheets")
            cursor.execute("DELETE FROM categories")
            
            # Save all root categories
            for category in manager.root_categories.values():
                self._save_category(cursor, category)
                
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False
            
    def get_cheatsheet_path(self, category_path: str, cheatsheet_name: str) -> Optional[str]:
        """
        Get the file system path for a specific cheat sheet.
        
        Args:
            category_path: Path to the category
            cheatsheet_name: Name of the cheat sheet
            
        Returns:
            The file system path if found, None otherwise
        """
        # This implementation is not optimized for SQLite
        # In a production version, we would use SQL queries instead
        manager = self.load()
        category = manager.get_category(category_path)
        
        if category is None:
            return None
            
        for cs in category.cheatsheets:
            if cs.name == cheatsheet_name:
                return cs.path
                
        return None
