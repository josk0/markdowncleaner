from pathlib import Path
import yaml
import re
from typing import List, Pattern, Optional, Dict
from dataclasses import dataclass
import logging

_logger = logging.getLogger(__name__)


@dataclass
class CleaningPatterns:
    """Container for document cleaning patterns."""
    sections_to_remove: List[str]
    bad_inline_patterns: List[Pattern]
    bad_lines_patterns: List[Pattern]
    footnote_patterns: List[Pattern]
    replacements: Dict[Pattern | str, str]

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'CleaningPatterns':
        """
        Create a CleaningPatterns instance from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            CleaningPatterns instance with compiled regex patterns
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            if not isinstance(config, dict):
                raise TypeError(f"Config must be a mapping of keys to patterns, got {type(config).__name__}")

            def get_list(key: str) -> list:
                """Return a list-valued key; a missing or null key gives []."""
                value = config.get(key)
                if value is None:
                    return []
                if not isinstance(value, list):
                    raise TypeError(f"'{key}' must be a list of patterns, got {type(value).__name__}")
                return value

            def compile_pattern(pattern: str) -> Pattern:
                """Safely compile a regex pattern."""
                if not isinstance(pattern, str):
                    raise TypeError(f"Pattern must be a string, got {type(pattern)}: {pattern}")
                try:
                    return re.compile(pattern, re.IGNORECASE)
                except re.error as e:
                    _logger.error(f"Invalid regex pattern '{pattern}': {e}")
                    raise

            # Ensure patterns are strings before compiling
            sections = [str(p).strip() for p in get_list('sections_to_remove')]
            inline_patterns = [str(p).strip() for p in get_list('bad_inline_patterns')]
            line_patterns = [str(p).strip() for p in get_list('bad_lines_patterns')]
            footnotes = [str(p).strip() for p in get_list('footnote_patterns')]
            replacements = config.get('replacements')
            replacements = {} if replacements is None else replacements
            if not isinstance(replacements, dict):
                raise TypeError(f"'replacements' must be a mapping, got {type(replacements).__name__}")
            # Values are not stripped: a replacement may be a single space
            replace = {str(k).strip(): '' if v is None else str(v) for k, v in replacements.items()}

            return cls(
                sections_to_remove=sections,
                bad_inline_patterns=[compile_pattern(p) for p in inline_patterns],
                bad_lines_patterns=[compile_pattern(p) for p in line_patterns],
                footnote_patterns=[compile_pattern(p) for p in footnotes],
                replacements=replace  # just taking this a str dict, no patterns to compile
            )
        except Exception as e:
            _logger.error(f"Error loading cleaning patterns from {yaml_path}: {e}")
            raise


_cached_patterns: Optional[CleaningPatterns] = None


def get_default_patterns() -> CleaningPatterns:
    """Load the default cleaning patterns from the package's configuration file."""
    global _cached_patterns
    if _cached_patterns is None:
        config_dir = Path(__file__).parent
        yaml_path = config_dir / 'default_cleaning_patterns.yaml'
        _cached_patterns = CleaningPatterns.from_yaml(yaml_path)
    # Return fresh containers so one caller's changes do not leak into another's
    return CleaningPatterns(
        sections_to_remove=list(_cached_patterns.sections_to_remove),
        bad_inline_patterns=list(_cached_patterns.bad_inline_patterns),
        bad_lines_patterns=list(_cached_patterns.bad_lines_patterns),
        footnote_patterns=list(_cached_patterns.footnote_patterns),
        replacements=dict(_cached_patterns.replacements),
    )
