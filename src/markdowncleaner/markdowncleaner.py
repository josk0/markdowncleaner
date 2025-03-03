from pathlib import Path
from dataclasses import dataclass
from typing import Pattern, Optional
import logging
import re
import ftfy
from markdowncleaner.config.loader import get_default_patterns, CleaningPatterns

_logger = logging.getLogger(__name__)

@dataclass
class CleanerOptions:
    """Countainer for Cleaner options"""
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


class MarkdownCleaner:
    """Class to handle markdown document cleaning operations."""

    def __init__(self, patterns: CleaningPatterns = None, options: Optional[CleanerOptions] = None):
        """
        Initialize the cleaner with patterns.

        Args:
            patterns: CleaningPatterns instance, or None to use defaults
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
        if ftfy.is_bad(content):
            content = ftfy.fix_text(content)

        # Reduce two or more subsequent spaces to a single space
        content = re.sub(r' {2,}', ' ', content)

        # Normalize quotes
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

        # Replace footnote pattern (numbers at end of sentence) with '.'
        if self.options.remove_footnotes_in_text:
            content = self._replace_within_lines(content, self.patterns.footnote_patterns, '.')

        # Remove remaining unwanted inline patterns (some may have been replaced by replacements)
        if self.options.remove_within_lines:
            content = self._replace_within_lines(content, self.patterns.bad_inline_patterns, '')

        # Clean up formatting
        if self.options.crimp_linebreaks:
            content = self._crimp_linebreaks(content)
        if self.options.contract_empty_lines:
            content = self._contract_empty_lines(content)

        return content
    
    def _normalize_quotation_symbols(self, text: str) -> str:
        """
        Normalizes quotation symbols in the input text.

        Args:
            text (str): Input text to clean
        Returns:
            str: Text with all single and double quotation symbols replaced with standard ones.
        """
        double_quotes = [
            "«",
            "‹",
            "»",
            "›",
            "„",
            "“",
            "‟",
            "”",
            "❝",
            "❞",
            "❮",
            "❯",
            "〝",
            "〞",
            "〟",
            "＂",
        ]
        single_quotes = ["‘", "‛", "’", "❛", "❜", "`", "´", "‘", "’"]

        double_quotes_regex = re.compile("|".join(double_quotes))
        single_quotes_regex = re.compile("|".join(single_quotes))

        text = single_quotes_regex.sub("'", text)
        text = double_quotes_regex.sub('"', text)

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

        # Filter out lines that are shorter than length but that are neither empty nor start with '#'
        filtered_lines = []
        for line in lines:
            if not line.strip() == '' and not line.startswith('#') and len(line) < length:
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
            if line.startswith(('#', '##')):
                # Extract the heading text
                heading_text = line.lstrip('#').strip() #.lower()

                # Check if heading matches the pattern
                if pattern.search(heading_text):
                    # Skip this heading and find the end of its section
                    i += 1
                    section_level = line.count('#')

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
        1. Hyphenated words split across lines (even with one empty line in between)
        2. Paragraphs incorrectly split by empty lines when a line ends with a letter

        Returns:
            str: Text with all patterns removed
        """

        lines = markdown_text.splitlines()
        result_lines = []
        i = 0

        while i < len(lines):
            current_line = lines[i].strip()
            
            # Try to join as many consecutive lines as possible
            while True:
                joined = False
                
                # Case 1: Handle hyphenated words
                if current_line.endswith('-'):
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    
                    if j < len(lines) and lines[j].strip() and lines[j].strip()[0].islower():
                        current_line = current_line[:-1] + lines[j].strip()
                        i = j  # Update i to the last joined line
                        joined = True
                        continue  # Skip to next join check
                
                # Case 2: Handle paragraph merging
                if not current_line.startswith('#') and current_line and (current_line[-1].isalpha() or current_line[-1] in ',;\'\"'):
                    _logger.debug(f'Crimping line:... {current_line[-50:]}')
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    
                    if j < len(lines) and lines[j].strip() and \
                       not lines[j].strip().startswith('#') and \
                       not lines[j].strip().startswith('*') and \
                       not lines[j].strip().startswith('-'):
                        current_line = current_line + ' ' + lines[j].strip()
                        i = j  # Update i to the last joined line
                        joined = True # noqa: F841
                        continue  # Skip to next join check
                
                # If no joins were made, break the loop
                break
            
            # Add the fully processed line to results
            result_lines.append(current_line)
            i += 1  # Move to the next line
        
        return '\n'.join(result_lines)