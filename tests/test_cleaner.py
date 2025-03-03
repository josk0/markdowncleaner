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
        
    def test_crimp_linebreaks(self):
        text = "This line ends \nwith an awkward break."
        result = self.cleaner._crimp_linebreaks(text)
        self.assertEqual(result, "This line ends with an awkward break.")
        
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
