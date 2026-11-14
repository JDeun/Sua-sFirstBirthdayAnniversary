#!/usr/bin/env python3
"""Run isolated standard-library tests; numerical tests use the bounded dependencies."""
from pathlib import Path
import sys
import unittest


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent / 'tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
