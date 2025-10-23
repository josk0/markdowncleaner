import unittest
from pathlib import Path
import tempfile
import shutil
import os
from markdowncleaner.cli import main, parse_args


class TestCLI(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.test_dir)

    def test_parse_args_basic(self):
        # Test default arguments
        args = parse_args(['somefile.md'])
        self.assertEqual(args.input_file, Path('somefile.md'))
        self.assertIsNone(args.output)
        self.assertIsNone(args.output_dir)
        self.assertFalse(args.keep_short_lines)
        self.assertEqual(args.min_line_length, 70)

    def test_parse_args_all_options(self):
        # Test with all options
        args = parse_args([
            'somefile.md',
            '--output', 'outfile.md',
            '--output-dir', 'outdir',
            '--config', 'custom_config.yaml',
            '--keep-short-lines',
            '--min-line-length', '50',
            '--keep-bad-lines',
            '--keep-sections',
            '--keep-duplicate-headlines',
            '--keep-footnotes',
            '--no-replacements',
            '--keep-inline-patterns',
            '--keep-empty-lines',
            '--no-crimping',
        ])

        self.assertEqual(args.input_file, Path('somefile.md'))
        self.assertEqual(args.output, Path('outfile.md'))
        self.assertEqual(args.output_dir, Path('outdir'))
        self.assertEqual(args.config, Path('custom_config.yaml'))
        self.assertTrue(args.keep_short_lines)
        self.assertEqual(args.min_line_length, 50)
        self.assertTrue(args.keep_bad_lines)
        self.assertTrue(args.keep_sections)
        self.assertTrue(args.keep_duplicate_headlines)
        self.assertTrue(args.keep_footnotes)
        self.assertTrue(args.no_replacements)
        self.assertTrue(args.keep_inline_patterns)
        self.assertTrue(args.keep_empty_lines)
        self.assertTrue(args.no_crimping)

    def test_main_success(self):
        # Create a test markdown file
        test_file = self.test_dir / "test.md"
        test_content = "# Test Document\nThis is a test.\n\n# References\n1. Test reference."

        with open(test_file, 'w') as f:
            f.write(test_content)

        # Run the CLI command
        output_dir = self.test_dir / "output"
        output_dir.mkdir()

        exit_code = main([str(test_file), '--output-dir', str(output_dir)])

        # Check exit code
        self.assertEqual(exit_code, 0)

        # Verify output exists
        output_files = list(output_dir.glob('*.md'))
        self.assertEqual(len(output_files), 1)

        # Verify content was cleaned (actual cleaning logic is tested elsewhere)
        self.assertTrue(os.path.getsize(output_files[0]) > 0)

    def test_main_error_nonexistent_file(self):
        # Test with nonexistent file
        exit_code = main(['nonexistent_file.md'])
        self.assertEqual(exit_code, 1)

if __name__ == '__main__':
    unittest.main()