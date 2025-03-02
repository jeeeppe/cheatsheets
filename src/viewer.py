"""
Viewer module for the Cheat Sheet Collection.

This module handles opening cheat sheets with appropriate applications.
"""
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional


class CheatSheetViewer:
    """
    Opens cheat sheets with appropriate applications based on file format.
    """
    def __init__(self):
        """Initialize the cheat sheet viewer."""
        self.system = platform.system()
        
    def view(self, file_path: str) -> bool:
        """
        Open a cheat sheet with the appropriate application.
        
        Args:
            file_path: Path to the cheat sheet file
            
        Returns:
            True if successful, False otherwise
        """
        path = Path(file_path)
        
        if not path.exists():
            return False
            
        try:
            if self.system == 'Windows':
                # On Windows, use the 'start' command
                os.startfile(path)
            elif self.system == 'Darwin':  # macOS
                # On macOS, use 'open'
                subprocess.run(['open', path], check=True)
            else:  # Linux and other Unix-like systems
                # On Linux, use 'xdg-open'
                subprocess.run(['xdg-open', path], check=True)
                
            return True
        except (OSError, subprocess.SubprocessError):
            return False
            
    def get_default_app(self, file_path: str) -> Optional[str]:
        """
        Get the name of the default application for a file type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Name of the default application, or None if it couldn't be determined
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        # This is a simplistic mapping
        # In a real implementation, we would use system-specific methods
        format_to_app = {
            '.md': 'Markdown viewer',
            '.html': 'Web browser',
            '.png': 'Image viewer',
            '.jpg': 'Image viewer',
            '.jpeg': 'Image viewer',
            '.pdf': 'PDF viewer',
            '.txt': 'Text editor'
        }
        
        return format_to_app.get(suffix)
