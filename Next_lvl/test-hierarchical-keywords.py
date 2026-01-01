#!/usr/bin/env python3
"""
Tests for the cheat sheet CLI tool with hierarchical keywords support.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from typing import Any, Optional

from cheatsheet import CheatSheetManager


class TestHierarchicalKeywords(unittest.TestCase):
    """Test cases for hierarchical keywords functionality."""

    temp_dir: str
    storage_path: str
    test_data: dict[str, Any]
    manager: CheatSheetManager

    def setUp(self) -> None:
        """Set up test environment with a temporary storage file."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "test_cheatsheets.json")
        
        # Initialize with a known structure
        self.test_data = {
            "cheatsheets": [
                {
                    "name": "test1",
                    "content": "Test content 1",
                    "categories": ["python", "testing"],
                    "keyword_path": ["Computers", "Programming", "Python", "Testing"],
                    "description": "Test cheatsheet 1",
                    "created_at": "2025-03-16T12:00:00",
                    "updated_at": "2025-03-16T12:00:00"
                },
                {
                    "name": "test2",
                    "content": "Test content 2",
                    "categories": ["bash", "terminal"],
                    "keyword_path": ["Computers", "Shell", "Bash"],
                    "description": "Test cheatsheet 2",
                    "created_at": "2025-03-16T12:00:00",
                    "updated_at": "2025-03-16T12:00:00"
                },
                {
                    "name": "test3",
                    "content": "Test content 3 without path",
                    "categories": ["git", "version-control"],
                    "description": "Test cheatsheet 3 without path",
                    "created_at": "2025-03-16T12:00:00",
                    "updated_at": "2025-03-16T12:00:00"
                }
            ],
            "keyword_taxonomy": {
                "Computers": {
                    "Programming": {
                        "Python": {
                            "Testing": {}
                        }
                    },
                    "Shell": {
                        "Bash": {}
                    }
                }
            }
        }
        
        with open(self.storage_path, "w") as f:
            json.dump(self.test_data, f)

        self.manager = CheatSheetManager(self.storage_path)

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_keyword_path_exists(self) -> None:
        """Test that keyword paths are correctly loaded."""
        cheatsheet: Optional[dict[str, Any]] = self.manager.get_cheatsheet("test1")
        assert cheatsheet is not None
        self.assertIn("keyword_path", cheatsheet)
        self.assertEqual(
            cheatsheet["keyword_path"],
            ["Computers", "Programming", "Python", "Testing"],
        )

    def test_search_by_keyword_path_exact(self) -> None:
        """Test searching by exact keyword path."""
        results: list[dict[str, Any]] = self.manager.search_by_keyword_path(
            ["Computers", "Programming", "Python", "Testing"],
            exact_match=True,
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test1")

    def test_search_by_keyword_path_prefix(self) -> None:
        """Test searching by keyword path prefix."""
        results: list[dict[str, Any]] = self.manager.search_by_keyword_path(
            ["Computers", "Programming"],
            exact_match=False,
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test1")

    def test_get_keyword_children(self) -> None:
        """Test getting children of a keyword path."""
        children: list[str] = self.manager.get_keyword_children(
            ["Computers", "Programming"]
        )
        self.assertEqual(children, ["Python"])

    def test_add_cheatsheet_with_keyword_path(self) -> None:
        """Test adding a cheatsheet with a keyword path."""
        self.manager.add_cheatsheet(
            "test4",
            "Test content 4",
            ["rust", "programming"],
            ["Computers", "Programming", "Rust"],
            "Test cheatsheet 4",
        )

        # Check that the cheatsheet was added
        cheatsheet: Optional[dict[str, Any]] = self.manager.get_cheatsheet("test4")
        self.assertIsNotNone(cheatsheet)
        assert cheatsheet is not None
        self.assertEqual(cheatsheet["keyword_path"], ["Computers", "Programming", "Rust"])

        # Check that the path was added to the taxonomy
        children: list[str] = self.manager.get_keyword_children(
            ["Computers", "Programming"]
        )
        self.assertIn("Rust", children)

    def test_migrate_categories_to_paths(self) -> None:
        """Test migrating categories to keyword paths."""
        # Before migration, test3 doesn't have a keyword path
        cheatsheet: Optional[dict[str, Any]] = self.manager.get_cheatsheet("test3")
        assert cheatsheet is not None
        self.assertNotIn("keyword_path", cheatsheet)

        # Perform migration
        migrated: int = self.manager.migrate_categories_to_paths("Uncategorized")
        self.assertEqual(migrated, 1)

        # After migration, test3 should have a keyword path
        cheatsheet = self.manager.get_cheatsheet("test3")
        assert cheatsheet is not None
        self.assertIn("keyword_path", cheatsheet)
        self.assertEqual(cheatsheet["keyword_path"], ["Uncategorized", "git"])

    def test_search_with_keyword_path_filter(self) -> None:
        """Test searching with a keyword path filter."""
        # Add another cheatsheet with Python in the content
        self.manager.add_cheatsheet(
            "test5",
            "Python content but in a different path",
            ["docs"],
            ["Documents", "Programming", "Python"],
            "Test cheatsheet 5",
        )

        # Search for "Python" with a path filter
        results: list[dict[str, Any]] = self.manager.search_cheatsheets(
            "Python", ["Computers"]
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test1")


if __name__ == "__main__":
    unittest.main()