"""Run all tests."""
import os
import sys
import unittest


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    sys.path.insert(0, root)
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=here, pattern="test_*.py", top_level_dir=root)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
