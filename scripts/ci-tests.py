#!/usr/bin/env python3
"""Run the unittest suite and expose failures as Actions annotations."""
from pathlib import Path
import sys
import unittest


def main():
    root = Path(__file__).resolve().parents[1]
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    for test, detail in result.failures + result.errors:
        message = (str(test) + "\n" + detail).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print("::error title=unittest failure::" + message)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
