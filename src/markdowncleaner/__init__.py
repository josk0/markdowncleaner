"""
markdowncleaner - A package for cleaning and normalizing markdown files.
"""

from .markdowncleaner import CleanerOptions, MarkdownCleaner

# Define public API
__all__ = ['CleanerOptions', 'MarkdownCleaner']

try:
    from importlib.metadata import version
    __version__ = version("markdowncleaner")
except ImportError:
    __version__ = "unknown"  # pragma: no cover