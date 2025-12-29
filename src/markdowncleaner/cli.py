#!/usr/bin/env python3
"""
Command-line interface for the markdowncleaner package.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from markdowncleaner.markdowncleaner import MarkdownCleaner, CleanerOptions
from markdowncleaner.config.loader import get_default_patterns, CleaningPatterns


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean and format markdown files by removing unwanted sections, lines, and patterns."
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the markdown file to clean"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Path to save the cleaned markdown file (default: input_file with '_cleaned' suffix)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save the cleaned file (default: same as input file)"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to custom YAML configuration file with cleaning patterns"
    )

    # Options for customizing the cleaning process
    parser.add_argument(
        "--fix-encoding",
        action="store_true",
        help="Fix encoding mojibake"
    )

    parser.add_argument(
        "--normalize-quotation",
        action="store_true",
        help="Normalize quotation symbols"
    )    

    parser.add_argument(
        "--keep-short-lines",
        action="store_true",
        help="Don't remove lines shorter than minimum length"
    )

    parser.add_argument(
        "--min-line-length",
        type=int,
        default=70,
        help="Minimum line length to keep (default: 70)"
    )

    parser.add_argument(
        "--keep-bad-lines",
        action="store_true",
        help="Don't remove lines matching bad line patterns"
    )

    parser.add_argument(
        "--keep-sections",
        action="store_true",
        help="Don't remove sections like References, Acknowledgements, etc."
    )

    parser.add_argument(
        "--keep-duplicate-headlines",
        action="store_true",
        help="Don't remove headlines that occur multiple times in text"
    )

    parser.add_argument(
        "--keep-footnotes",
        action="store_true",
        help="Don't remove footnote references in text"
    )

    parser.add_argument(
        "--no-replacements",
        action="store_true",
        help="Don't perform text replacements"
    )

    parser.add_argument(
        "--keep-inline-patterns",
        action="store_true",
        help="Don't remove inline patterns like citations"
    )

    parser.add_argument(
        "--keep-empty-lines",
        action="store_true",
        help="Don't contract consecutive empty lines"
    )

    parser.add_argument(
        "--no-crimping",
        action="store_true",
        help="Don't crimp linebreaks"
    )

    parser.add_argument(
        "--keep-references",
        action="store_true",
        help="Don't heuristically detect and remove references"
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parsed_args = parse_args(args)

    # Configure cleaner options based on arguments
    options = CleanerOptions(
        fix_encoding_mojibake=parsed_args.fix_encoding,
        normalize_quotation_symbols=parsed_args.normalize_quotation,
        remove_short_lines=not parsed_args.keep_short_lines,
        min_line_length=parsed_args.min_line_length,
        remove_whole_lines=not parsed_args.keep_bad_lines,
        remove_sections=not parsed_args.keep_sections,
        remove_duplicate_headlines=not parsed_args.keep_duplicate_headlines,
        remove_footnotes_in_text=not parsed_args.keep_footnotes,
        replace_within_lines=not parsed_args.no_replacements,
        remove_within_lines=not parsed_args.keep_inline_patterns,
        contract_empty_lines=not parsed_args.keep_empty_lines,
        crimp_linebreaks=not parsed_args.no_crimping,
        remove_references_heuristically=not parsed_args.keep_references,
    )

    # Load patterns from custom config or use defaults
    if parsed_args.config:
        try:
            patterns = CleaningPatterns.from_yaml(parsed_args.config)
        except Exception as e:
            print(f"Error loading custom configuration: {e}", file=sys.stderr)
            return 1
    else:
        patterns = get_default_patterns()

    # Initialize the cleaner with patterns and configured options
    cleaner = MarkdownCleaner(patterns=patterns, options=options)

    try:
        # Clean the markdown file
        output_file = cleaner.clean_markdown_file(
            input_file=parsed_args.input_file,
            output_path=parsed_args.output_dir,
            output_file=parsed_args.output
        )
        print(f"Cleaned markdown saved to: {output_file}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())