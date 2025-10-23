import unittest
from pathlib import Path
import tempfile
import shutil
from markdowncleaner.markdowncleaner import MarkdownCleaner, CleanerOptions
from markdowncleaner.config.loader import get_default_patterns


class TestMarkdownCleaner(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        # Initialize cleaner with default options
        self.cleaner = MarkdownCleaner(patterns=get_default_patterns())
        
    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.test_dir)
        
    def test_remove_short_lines(self):
        text = "This is a long line that should be kept in the output.\n" + \
               "Short line.\n" + \
               "Another long line that should remain in the cleaned output."
        
        # Test with default settings (should remove short lines)
        result = self.cleaner._remove_short_lines(text, 50)
        self.assertIn("This is a long line", result)
        self.assertNotIn("Short line", result)
        
        # Test with option disabled
        options = CleanerOptions()
        options.remove_short_lines = False
        cleaner_with_options = MarkdownCleaner(options=options)
        result = cleaner_with_options.clean_markdown_string(text)
        self.assertIn("Short line", result)
        
    def test_remove_whole_lines(self):
        text = "Normal content line.\n" + \
               "Copyright © 2023 All rights reserved.\n" + \
               "Another normal line."
        
        # Should remove the copyright line with default patterns, disabling short line removal for test
        options = CleanerOptions()
        options.remove_short_lines = False
        cleaner_with_options = MarkdownCleaner(options=options)
        result = cleaner_with_options.clean_markdown_string(text)
        self.assertIn("Normal content line", result)
        self.assertNotIn("Copyright", result)
        
    def test_remove_sections(self):
        text = "# Introduction\n" + \
               "This is the introduction text.\n\n" + \
               "# References\n" + \
               "1. Author, A. (2023). Title. Journal.\n" + \
               "2. Another reference.\n\n" + \
               "# Conclusion\n" + \
               "This is the conclusion."
        
        # Should remove the References section
        result = self.cleaner.clean_markdown_string(text)
        self.assertIn("# Introduction", result)
        self.assertIn("# Conclusion", result)
        self.assertNotIn("# References", result)
        self.assertNotIn("1. Author", result)
        
    def test_contract_empty_lines(self):
        text = "Line 1\n\n\n\nLine 2"
        result = self.cleaner._contract_empty_lines(text)
        self.assertEqual(result, "Line 1\n\nLine 2")
        
    def test_replace_within_lines(self):
        text = "This text contains [1] a citation reference."
        # Use a pattern that matches citation markers
        result = self.cleaner._replace_within_lines(text, r'\[\d+\]', '')
        self.assertEqual(result, "This text contains  a citation reference.")
        
    def test_remove_footnotes(self):
        text = ".1 Footnote\n" + \
               "Normal Line 1.\n\n" + \
               "Another line" + \
               ".18 Footnote.\n" + \
               ". 191 Stranger Footnote.\n\n" + \
               "Normal line" + \
               ". A Funny line"
        
        # disabling short line removal for test
        options = CleanerOptions()
        options.remove_short_lines = False
        cleaner_with_options = MarkdownCleaner(options=options)
        
        result = cleaner_with_options.clean_markdown_string(text)
        self.assertTrue("Normal Line 1." in result)
        self.assertTrue(". A Funny line" in result)
        self.assertFalse(".1 Footnote" in result)

    def test_remove_duplicate_headlines(self):
        """Test all headline removal scenarios in a single test function."""
        # Test with an empty string
        self.assertEqual(self.cleaner._remove_duplicate_headlines(""), "")
        
        # Test with text that contains no headlines
        text_no_headlines = "This is just regular text\nwith no headlines at all."
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_no_headlines), text_no_headlines)
        
        # Test with text that contains unique headlines
        text_unique = "# Headline 1\nSome content\n## Headline 2\nMore content\n# Headline 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_unique), text_unique)
        
        # Test with text that contains duplicate headlines
        text_duplicate = "# Duplicate\n" +\
                        "Content 1\n" +\
                        "# Unique\nContent 2\n" +\
                        "# Duplicate\n" +\
                        "Content 3"
        expected_duplicate = "Content 1\n" +\
                        "# Unique\n" +\
                        "Content 2\n" +\
                        "Content 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_duplicate), expected_duplicate)
        
        # Test with empty lines 
        text_with_empty_lines = "# Duplicate\n" +\
                        "\n" +\
                        "Content 1\n" +\
                        "# Unique\n" +\
                        "Content 2\n" +\
                        "\n" +\
                        "\n" +\
                        "# Duplicate\n" +\
                        "Content 3"
        expected_with_empty_lines = "\n" +\
                        "Content 1\n" +\
                        "# Unique\n" +\
                        "Content 2\n" +\
                        "\n" +\
                        "\n" +\
                        "Content 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_with_empty_lines), expected_with_empty_lines)
        
        # Test with different headline levels where some are duplicates
        text_mixed_levels = "# Level 1\n" +\
                            "Content\n" +\
                            "## Level 2\n" +\
                            "More content\n" +\
                            "# Level 1\n" +\
                            "More content\n" +\
                            "### Level 3"
        expected_mixed_levels = "Content\n" +\
                            "## Level 2\n" +\
                            "More content\n" +\
                            "More content\n" +\
                            "### Level 3"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_mixed_levels), expected_mixed_levels)

        # Test with multiple sets of duplicate headlines
        text_multiple_dups = "# H1\n" +\
                            "A\n" +\
                            "## H2\n" +\
                            "B\n" +\
                            "# H1\n" +\
                            "C\n" +\
                            "## H2\n" +\
                            "D\n" +\
                            "### H3\n" +\
                            "E"
        expected_multiple_dups = "A\n" +\
                            "B\n" +\
                            "C\n" +\
                            "D\n" +\
                            "### H3\n" +\
                            "E"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_multiple_dups), expected_multiple_dups)
        
        # Test that headline matching is case-sensitive
        text_case = "# Headline\n" +\
                    "Content\n" +\
                    "# headline\n" +\
                    "More content"
        self.assertEqual(self.cleaner._remove_duplicate_headlines(text_case), text_case)

    def test_crimp_linebreaks(self):
        # Test connective-based crimping (line ending with hyphen)
        text = "This line ends with a hy-\nphenated word that continues."
        result = self.cleaner._crimp_linebreaks(text)
        self.assertEqual(result, "This line ends with a hyphenated word that continues.")
        
    def test_clean_markdown_file(self):
        # Create a test markdown file
        test_file = self.test_dir / "test.md"
        test_content = "# Test Document\nThis is a test.\n\n# References\n1. Test reference."
        
        with open(test_file, 'w') as f:
            f.write(test_content)
            
        # Clean the file
        output_file = self.cleaner.clean_markdown_file(test_file, self.test_dir)
        
        # Verify output exists
        self.assertTrue(output_file.exists())
        
        # Verify content was cleaned
        with open(output_file) as f:
            content = f.read()
            self.assertIn("# Test Document", content)
            self.assertNotIn("# References", content)


if __name__ == '__main__':
    unittest.main()
