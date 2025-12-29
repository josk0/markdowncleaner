from pathlib import Path
from dataclasses import dataclass
from typing import Pattern, Optional
import logging
import re
import ftfy
from markdowncleaner.config.loader import get_default_patterns, CleaningPatterns

_logger = logging.getLogger(__name__)

# Pre-compiled quote normalization regexes
_DOUBLE_QUOTES = ["«", "‹", "»", "›", "„", """, "‟", """, "❝", "❞", "❮", "❯", "〝", "〞", "〟", "＂"]
_SINGLE_QUOTES = ["'", "‛", "'", "❛", "❜", "`", "´", "'", "'"]
_DOUBLE_QUOTES_REGEX = re.compile("|".join(_DOUBLE_QUOTES))
_SINGLE_QUOTES_REGEX = re.compile("|".join(_SINGLE_QUOTES))


def _is_list_item(line: str) -> bool:
    """Check if a line appears to be a list item."""
    if not line:
        return False
    # Starts with list marker
    if line[0] in '-–—*∙•・◦●○':
        return True
    # Contains list punctuation in first 5 chars
    if any(char in line[:5] for char in '.)*]'):
        return True
    # Starts with numeral
    if line[0].isdigit():
        return True
    return False


@dataclass
class CleanerOptions:
    """Container for Cleaner options"""
    fix_encoding_mojibake : bool = False
    normalize_quotation_symbols : bool = False
    remove_short_lines: bool = True
    min_line_length: int = 70
    remove_whole_lines: bool = True
    remove_sections: bool = True
    remove_duplicate_headlines: bool = True
    remove_duplicate_headlines_threshold: int = 2
    remove_footnotes_in_text: bool = True
    replace_within_lines: bool = True
    remove_within_lines: bool = True
    contract_empty_lines: bool = True
    crimp_linebreaks: bool = True
    remove_references_heuristically: bool = True


class MarkdownCleaner:
    """Class to handle markdown document cleaning operations."""

    def __init__(self, patterns: Optional[CleaningPatterns] = None, options: Optional[CleanerOptions] = None):
        """
        Initialize the cleaner with patterns.

        Args:
            patterns: CleaningPatterns instance, or None to use defaults
            options: CleanerOptions instance, or None to use defaults
        """
        self.patterns = patterns or get_default_patterns()
        self.options = options or CleanerOptions()

    def clean_markdown_file(self,
                            input_file: Path,
                            output_path: Optional[Path] = None,
                            output_file: Optional[Path | str] = None) -> Path:
        """
        Clean a markdown file using the configured patterns.

        Args:
            input_file: Path to the input markdown file
            output_path: Optional directory to save the cleaned file
            output_file: Optional path to save the cleaned file directly (overrides output_path)

        Returns:
            Path: The path to the cleaned output file
        """
        # Read the content of the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            cleaned_content = file.read()

        # Apply cleaning operations
        cleaned_content = self.clean_markdown_string(cleaned_content)

        if output_file is not None:
            cleaned_filepath = Path(output_file)
            # Ensure parent directory exists
            cleaned_filepath.parent.mkdir(parents=True, exist_ok=True)
        elif output_path is not None:
            # Determine the output filepath
            output_path.mkdir(parents=True, exist_ok=True)
            cleaned_filepath = output_path / input_file.name
        else:  # both output_path and output_file are None
            # Generate a new filename with "_cleaned" suffix
            cleaned_filename = f"{input_file.stem}_cleaned{input_file.suffix}"
            cleaned_filepath = input_file.parent / cleaned_filename
        # Ensure parent directory exists (might be unnecessary if same as input, but added for safety)
        cleaned_filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write the cleaned content
        with open(cleaned_filepath, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

        _logger.info(f"Cleaned file saved to: {cleaned_filepath}")

        return cleaned_filepath

    def clean_markdown_string(self, content: str) -> str:
        """Apply all cleaning operations to the content."""

        # Apply all default ftfy fixes if mojibake is detected
        if self.options.fix_encoding_mojibake:
            if ftfy.is_bad(content):
                content = ftfy.fix_text(content)

        # Heuristically detect and remove blocks of lines with bibliographic information 
        if self.options.remove_references_heuristically:
            content = self._remove_bibliographic_lines(content)
        
        # Reduce two or more subsequent spaces to a single space
        content = re.sub(r' {2,}', ' ', content)

        # Normalize quotes
        if self.options.normalize_quotation_symbols:
            content = self._normalize_quotation_symbols(content)

        # Remove lines shorter than min_line_length (default: 70 characters)
        if self.options.remove_short_lines:
            content = self._remove_short_lines(content, self.options.min_line_length)
        # Clean out "bad" lines
        if self.options.remove_whole_lines:
            content = self._remove_whole_lines(content, self.patterns.bad_lines_patterns)

        # Remove unwanted sections
        if self.options.remove_sections:
            for title in self.patterns.sections_to_remove:
                content = self._remove_sections(content, title)
        
        # Remove duplicate headlines
        if self.options.remove_duplicate_headlines:
            content = self._remove_duplicate_headlines(content, self.options.remove_duplicate_headlines_threshold)
        
        # Replace strings for string
        if self.options.replace_within_lines:
            for k, v in self.patterns.replacements.items():
                content = self._replace_within_lines(content, k, v)

        # Replace footnote pattern (numbers at end of sentence) with '. '
        if self.options.remove_footnotes_in_text:
            content = self._replace_within_lines(content, self.patterns.footnote_patterns, '. ')

        # Remove remaining unwanted inline patterns (some may have been replaced by replacements)
        if self.options.remove_within_lines:
            content = self._replace_within_lines(content, self.patterns.bad_inline_patterns, '')

        # Clean up formatting
        if self.options.crimp_linebreaks:
            content = self._crimp_linebreaks(content)
        if self.options.contract_empty_lines:
            content = self._contract_empty_lines(content)

        return content
    
    def _remove_bibliographic_lines(self, text: str, score_threshold: int = 3) -> str:
        """
        Remove bibliographic reference lines from text.

        Detects and removes individual lines that appear to be bibliography entries
        by scoring each line based on bibliographic patterns.

        Args:
            text: Input text to clean
            score_threshold: Minimum score for a line to be removed (default: 3)

        Returns:
            Text with bibliographic lines removed
        """
        lines = text.splitlines()
        result_lines = []

        for line in lines:
            score = self._score_bibliography_line(line)
            if score < score_threshold:
                result_lines.append(line)

        return '\n'.join(result_lines)

    def _score_bibliography_line(self, line: str) -> int:
        """
        Score a line based on bibliographic patterns.

        Args:
            line: Line of text to score

        Returns:
            Integer score based on number of bibliographic patterns matched
        """
        score = 0
        stripped = line.strip()

        # Don't score very short lines
        if len(stripped) < 20:
            return 0

        # 1 point patterns

        # Year in parentheses: (1984), (2020), or [1960]
        if re.search(r'\([12][089]\d{2}\)|\[[12][089]\d{2}\]', line):
            score += 1

        # Page ranges: 35-57, pp. 332-487, 283-310
        if re.search(r'\bpp?\.\s*\d+-\d+|\b\d{2,3}-\d{2,3}\b', line):
            score += 1

        # Publisher/location: "Cambridge, MA: Harvard", "Oxford: Clarendon Press"
        if re.search(r'[A-Z][a-z]+(?:,\s*[A-Z]{2})?:\s*[A-Z][a-z]+', line):
            score += 1

        # Numbered list format: starts with "1. ", "14. ", etc.
        if re.match(r'^\s*\d{1,3}\.\s+', line):
            score += 1

        # Bullet format: starts with "- " or "• "
        if re.match(r'^\s*[-•]\s+', line):
            score += 1

        # Italic markers: *Title Text*
        if re.search(r'\*[^*]+\*', line):
            score += 1

        # "In:" followed by capital letter
        if re.search(r'\bIn:\s+[A-Z]', line):
            score += 1

        # Ampersand: " & " in author context
        if ' & ' in line:
            score += 1

        # Multiple initials: "J. B. Wiesner", "M.A.", "H. F."
        if re.search(r'\b[A-Z]\.\s*[A-Z]\.|\b[A-Z]\.[A-Z]\.', line):
            score += 1

        # "et al."
        if 'et al.' in line:
            score += 1

        # Author name patterns: "LastName, FirstInitial." or "LastName, FirstName" at line start
        if re.match(r'^\s*[A-Z][a-z]+,\s+[A-Z]', line):
            score += 1

        # Punctuation density: >8% of characters are . , : ; ( )
        if len(line) > 0:
            punct_chars = sum(1 for c in line if c in '.,;:()')
            if punct_chars / len(line) > 0.08:
                score += 1

        # 2 point patterns
        
        # Common journal names
        if re.search(r'\b(journal|proceedings|review|quarterly|annals|transactions|bulletin|University Press)\b', line, re.IGNORECASE):
            score += 2
        
        # Author initial and date without brackets separated with dots
        if re.search(r' [A-Za-z]\. \d{4}\. ', line):
            score += 2
        if re.search(r' [A-Za-z]\.\, \d{4}\, ', line):
            score += 2
        # Author lastname, first abbreviated, date in brackets, then title, e.g., Axelrod, R. (1984) T
        if re.search(r'\w+,\s+([A-Z]\.)+\s+\(\d{4}\)\s+[A-Z]', line):
            score += 2

        # volumne and page ranges
        if re.search(r' \d{2,3}: \d{1,4}[-–—]\d{2,4}', line):
            score += 2

        # 3 point patterns

        # Volume/issue: 121(3), 14(2), Vol. I, vol(issue)
        if re.search(r'\b\d+\(\d+\)\b|Vol\.\s*[IVX]+|vol\.\s*\d+', line, re.IGNORECASE):
            score += 3

        # DOI: doi.org/, DOI:
        if re.search(r'doi\.org/|DOI:', line, re.IGNORECASE):
            score += 3

        # Editor markers: "Ed." or "Eds." (as standalone word or in parentheses)
        if re.search(r'\bEds?\.\b|\(Eds?\.\)', line):
            score += 3

        return score

    def _normalize_quotation_symbols(self, text: str) -> str:
        """
        Normalizes quotation symbols in the input text.

        Args:
            text (str): Input text to clean
        Returns:
            str: Text with all single and double quotation symbols replaced with standard ones.
        """
        text = _SINGLE_QUOTES_REGEX.sub("'", text)
        text = _DOUBLE_QUOTES_REGEX.sub('"', text)
        return text 

    def _replace_within_lines(self, text: str, patterns: str | Pattern | list[str | Pattern], replacement: str = '') -> str:
        """
        Removes multiple patterns from text, applying them sequentially.

        Args:
            text (str): Input text to clean
            patterns (str | Pattern | list): Single regex pattern or list of regex patterns to remove
            replacement (str, optional): String to replace the matched patterns with. Defaults to ''.

        Returns:
            str: Text with all patterns removed or replaced
        """
        # Ensure patterns is a list, converting single pattern to a list if needed
        if not isinstance(patterns, list):
            patterns = [patterns]

        cleaned_text = text
        for pattern in patterns:
            # Make sure each pattern is a compiled regex
            if isinstance(pattern, str):
                pattern = re.compile(pattern)

            cleaned_text = pattern.sub(replacement, cleaned_text)
        return cleaned_text

    def _remove_short_lines(self, multiline_string: str, length: int = 70) -> str:
        """
        Remove lines from a multiline string that are shorter than a specified length.

        Args:
            multiline_string: The input string to clean
            length: The minimum length of lines to keep

        Returns:
            Cleaned string with matching lines removed
        """

        # Split the content into lines
        lines = multiline_string.splitlines()

        # Filter out lines that are shorter than length but that are neither empty nor start with '#' nor with a pattern indicating a markdown list like '1. '
        filtered_lines = []
        for line in lines:
            if not line.strip() == '' and not line.startswith('#') and not re.match(r'^\d{1,2}\.\s', line) and len(line) < length:
                continue
            filtered_lines.append(line)

        # Join the remaining lines back into a single string
        return '\n'.join(filtered_lines)

    def _remove_whole_lines(self, multiline_string: str, patterns: str | Pattern | list[str | Pattern]) -> str:
        """
        Remove lines from a multiline string that match specified regex pattern(s).

        Args:
            multiline_string: The input string to clean
            patterns: A single regex pattern (str or compiled Pattern) or a list of patterns

        Returns:
            Cleaned string with matching lines removed
        """

        # Split the content into lines
        lines = multiline_string.splitlines()

        # Make sure patterns is a list
        if not isinstance(patterns, list):
            patterns = [patterns]
        # Filter out lines that match any of the patterns, except empty lines
        filtered_lines = []
        for line in lines:
            if line.strip() == '':  # Keep empty lines
                filtered_lines.append(line)
                continue
            if any(pattern.search(line) for pattern in patterns):
                continue
            filtered_lines.append(line)

        # Join the remaining lines back into a single string
        return '\n'.join(filtered_lines)

    def _contract_empty_lines(self, multiline_string: str) -> str:
        """Contract two or more consecutive empty lines from a multiline string."""
        lines = multiline_string.splitlines()
        result = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()
            if not (is_empty and prev_empty):
                result.append(line)
            prev_empty = is_empty

        return '\n'.join(result)

    def _remove_sections(self, markdown_text: str, section_pattern: str) -> str:
        """
        Removes a first or second level section from a markdown document if its title
        matches the given regular expression pattern.

        Args:
            markdown_text (str): The input markdown text
            section_pattern (str): Regular expression pattern to match the section title

        Returns:
            str: The markdown text with the matching section removed
        """
        # Compile the pattern with IGNORECASE flag
        pattern = re.compile(section_pattern, re.IGNORECASE)

        # Split the markdown into lines
        lines = markdown_text.splitlines()
        result_lines = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if line is a first or second level heading
            if line.startswith('#'):
                # Extract the heading text
                heading_text = line.lstrip('#').strip()

                # Check if heading matches the pattern
                if pattern.search(heading_text):
                    # Skip this heading and find the end of its section
                    i += 1
                    section_level = len(line) - len(line.lstrip('#'))

                    # Continue until we find a heading of same or higher level, or end of document
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.startswith('#'):
                            next_level = next_line.count('#')
                            if next_level <= section_level:
                                break
                        i += 1
                    continue

            result_lines.append(lines[i])
            i += 1

        # Return the modified markdown, preserving original line endings
        return '\n'.join(result_lines)

    def _remove_duplicate_headlines(self, markdown_text: str, threshold: Optional[int] = 1) -> str:
        """
        Find all headlines in a markdown string that occur more than threshold times (default: once)
        and remove all instances of such headlines.

        Args:
            markdown_text (str): The markdown text to process
            threshold (Optional[int]): The minimum number of occurrences to consider a duplicate

        Returns:
            str: The markdown text with duplicate headlines removed
        """
        # Split the text into lines
        lines = markdown_text.splitlines()

        # Identify headline lines (lines starting with #)
        headline_lines = []
        headline_indices = []

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line and stripped_line.startswith('#'):
                headline_lines.append(stripped_line)
                headline_indices.append(i)

        # Find headlines that occur more than once
        headline_counts = {}
        for headline in headline_lines:
            headline_counts[headline] = headline_counts.get(headline, 0) + 1

        duplicate_headlines = {headline for headline, count in headline_counts.items() if count > threshold}

        # Create a new list of lines, excluding the duplicate headlines
        filtered_lines = []
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line and stripped_line.startswith('#') and stripped_line in duplicate_headlines:
                continue  # Skip duplicate headlines
            else:
                filtered_lines.append(line)

        # Join the lines back together
        return '\n'.join(filtered_lines)

    def _crimp_linebreaks(self, markdown_text: str) -> str:
        """
        Fix line break errors in markdown text converted from PDF.

        Args:
            markdown_text (str): Input markdown text with potential line break errors

        The function handles two cases:
        1. Connective-based crimping: Lines ending with -, –, —, or ...
        2. Justified text crimping: Adjacent lines of similar length

        Returns:
            str: Text with crimped linebreaks
        """
        lines = markdown_text.splitlines()
        result_lines = []
        i = 0

        while i < len(lines):
            current_line = lines[i].strip()
            
            # Try to join as many consecutive lines as possible
            while True:
                
                # Case 1: Connective-based crimping
                if current_line and current_line.endswith(('-', '–', '—', '...')):
                    # Find next non-empty line within 3 lines (max 2 empty lines between)
                    j = i + 1
                    empty_count = 0
                    while j < len(lines) and empty_count <= 2:
                        if not lines[j].strip():
                            empty_count += 1
                            j += 1
                        else:
                            break
                    
                    # Check if we found a valid next line
                    if j < len(lines) and lines[j].strip():
                        next_line = lines[j].strip()
                        
                        # Check all conditions
                        if (next_line[0].isalpha() and  # Starts with letter
                            not _is_list_item(next_line) and  # Not a list item
                            '.' in next_line[6:]):  # Contains '.' at position 6 or later
                            
                            # Remove hyphen if present, otherwise add space
                            if current_line.endswith(('-', '–', '—')):
                                current_line = current_line[:-1] + next_line
                            else:  # ends with '...'
                                current_line = current_line + ' ' + next_line
                            
                            i = j  # Update i to the last joined line
                            continue
                
                # Case 2: Justified text crimping
                if (current_line and 
                    current_line[-1].isalpha() and  # Ends with letter
                    not current_line.startswith('#') and  # Not a heading
                    not _is_list_item(current_line)):  # Not a list item
                    
                    # Check immediately next line (L+1)
                    j = i + 1
                    if j < len(lines) and lines[j].strip():
                        next_line = lines[j].strip()
                        
                        # Check all conditions
                        if (next_line[0].isalpha() and  # Starts with letter
                            not next_line.startswith('#') and  # Not a heading
                            not _is_list_item(next_line) and  # Not a list item
                            len(next_line) >= 78 and  # Length >= 78
                            abs(len(next_line) - len(current_line)) <= 10):  # Within ±10
                            
                            current_line = current_line + ' ' + next_line
                            i = j  # Update i to the last joined line
                            continue
                
                # If no joins were made, break the loop
                break
            
            # Add the fully processed line to results
            result_lines.append(current_line)
            i += 1  # Move to the next line
        
        return '\n'.join(result_lines)