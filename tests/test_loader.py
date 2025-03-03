import unittest
from pathlib import Path
import tempfile
from markdowncleaner.config.loader import get_default_patterns


class TestConfigLoader(unittest.TestCase):
    def test_get_default_patterns(self):
        # Test that default patterns are loaded
        patterns = get_default_patterns()
        
        # Verify that patterns contain the expected sections
        self.assertTrue(hasattr(patterns, 'sections_to_remove'))
        self.assertTrue(hasattr(patterns, 'bad_lines_patterns'))
        self.assertTrue(hasattr(patterns, 'bad_inline_patterns'))
        self.assertTrue(hasattr(patterns, 'footnote_patterns'))
        self.assertTrue(hasattr(patterns, 'replacements'))
        
        # Check that at least some expected patterns exist
        self.assertIn('Funding', patterns.sections_to_remove)
            
    def test_patterns_from_yaml(self):
        # Create a temporary YAML file
        with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w+', delete=False) as f:
            yaml_path = Path(f.name)
            yaml_content = """
            sections_to_remove:
              - "Custom Section"
              - "Another Section"
            bad_lines_patterns:
              - "pattern1"
              - "pattern2"
            bad_inline_patterns:
              - "inline1"
              - "inline2"
            footnote_patterns:
              - "footnote1"
            replacements:
              "replace1": "replacement1"
              "replace2": "replacement2"
            """
            f.write(yaml_content)
        
        try:
            # Load the patterns from the file
            patterns = get_default_patterns().from_yaml(yaml_path)
            
            # Verify patterns were loaded correctly
            self.assertIn("Custom Section", patterns.sections_to_remove)
            self.assertEqual(len(patterns.bad_lines_patterns), 2)
            self.assertEqual(len(patterns.bad_inline_patterns), 2)
            self.assertEqual(len(patterns.footnote_patterns), 1)
            self.assertEqual(patterns.replacements.get("replace1"), "replacement1")
        finally:
            # Clean up
            yaml_path.unlink()


if __name__ == '__main__':
    unittest.main()
