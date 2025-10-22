#!/usr/bin/env python3
"""
Script to clean all markdown files in a folder and its subfolders in parallel.
Processes files in-place using ProcessPoolExecutor for efficient parallel processing.
"""

import argparse
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Tuple, Optional
import multiprocessing

try:
    from tqdm import tqdm
except ImportError:
    print("Error: tqdm is required for progress tracking.", file=sys.stderr)
    print("Install it with: pip install tqdm", file=sys.stderr)
    sys.exit(1)

from markdowncleaner import MarkdownCleaner
from markdowncleaner.config.loader import get_default_patterns, CleaningPatterns


def clean_single_file(file_path: Path, config_path: Optional[Path] = None) -> Tuple[Path, bool, Optional[str]]:
    """
    Clean a single markdown file in-place.

    Args:
        file_path: Path to the markdown file to clean
        config_path: Optional path to custom YAML configuration

    Returns:
        Tuple of (file_path, success, error_message)
    """
    try:
        # Load patterns
        if config_path:
            patterns = CleaningPatterns.from_yaml(config_path)
        else:
            patterns = get_default_patterns()

        # Initialize cleaner
        cleaner = MarkdownCleaner(patterns=patterns)

        # Clean the file in-place
        cleaner.clean_markdown_file(input_file=file_path, output_file=file_path)

        return (file_path, True, None)
    except Exception as e:
        return (file_path, False, str(e))


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean all markdown files in a folder and its subfolders in parallel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s documents/
  %(prog)s documents/ --yes
  %(prog)s documents/ --workers 8
  %(prog)s documents/ --config custom_patterns.yaml
        """
    )

    parser.add_argument(
        "folder",
        type=Path,
        help="Folder containing markdown files to clean"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt and proceed immediately"
    )

    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        help=f"Number of parallel workers (default: {multiprocessing.cpu_count()})"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to custom YAML configuration file with cleaning patterns"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for the script."""
    args = parse_args()

    # Validate folder exists
    if not args.folder.exists():
        print(f"Error: Folder '{args.folder}' does not exist.", file=sys.stderr)
        return 1

    if not args.folder.is_dir():
        print(f"Error: '{args.folder}' is not a directory.", file=sys.stderr)
        return 1

    # Find all markdown files recursively
    print(f"Searching for markdown files in '{args.folder}'...")
    md_files = list(args.folder.rglob("*.md"))

    if not md_files:
        print("No markdown files found.")
        return 0

    # Show count and ask for confirmation
    print(f"Found {len(md_files)} markdown file(s).")

    if not args.yes:
        response = input("Proceed with cleaning? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("Aborted.")
            return 0

    # Determine number of workers
    max_workers = args.workers or multiprocessing.cpu_count()
    print(f"Processing files using {max_workers} parallel worker(s)...")

    # Process files in parallel with progress bar
    successful = []
    failed = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(clean_single_file, file_path, args.config): file_path
            for file_path in md_files
        }

        # Process completed tasks with progress bar
        with tqdm(total=len(md_files), unit="file") as pbar:
            for future in as_completed(future_to_file):
                file_path, success, error = future.result()

                if success:
                    successful.append(file_path)
                else:
                    failed.append((file_path, error))

                pbar.update(1)

    # Report results
    print(f"\n{'='*60}")
    print(f"Successfully cleaned: {len(successful)} file(s)")

    if failed:
        print(f"Failed: {len(failed)} file(s)")
        print("\nFailed files:")
        for file_path, error in failed:
            print(f"  - {file_path}")
            print(f"    Error: {error}")
        return 1
    else:
        print("All files processed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
