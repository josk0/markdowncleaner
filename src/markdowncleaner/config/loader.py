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
                config = yaml.safe_load(f)

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
            sections = [str(p).strip() for p in config.get('sections_to_remove', [])]
            inline_patterns = [str(p).strip() for p in config.get('bad_inline_patterns', [])]
            line_patterns = [str(p).strip() for p in config.get('bad_lines_patterns', [])]
            footnotes = [str(p).strip() for p in config.get('footnote_patterns', [])]
            replace = {str(k).strip(): str(v).strip() for k, v in config.get('replacements', {}).items()}

            return cls(
                sections_to_remove=sections,
                bad_inline_patterns=[compile_pattern(p) for p in inline_patterns],
                bad_lines_patterns=[compile_pattern(p) for p in line_patterns],
                footnote_patterns=[compile_pattern(p) for p in footnotes],
                replacements=replace # just taking this a str dict, no patterns to compile
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
    return _cached_patterns