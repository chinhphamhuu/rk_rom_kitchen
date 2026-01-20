"""
Test No Patched Sparse in App
Global audit: không có "_patched_sparse.img" trong app/ (ngoại trừ tests)
"""
import unittest
import os
from pathlib import Path


class TestNoPatchedSparseInApp(unittest.TestCase):
    """Assert không có *_patched_sparse.img naming trong runtime code"""
    
    def test_no_patched_sparse_in_app_core(self):
        """
        Scan tất cả .py trong app/ (exclude app/tests)
        Assert không có substring "_patched_sparse.img"
        """
        # Find app directory
        this_file = Path(__file__).resolve()
        tests_dir = this_file.parent  # app/tests
        app_dir = tests_dir.parent    # app/
        
        violations = []
        
        # Walk app/ excluding tests/
        for py_file in app_dir.rglob("*.py"):
            # Skip test files
            if "tests" in py_file.parts:
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "_patched_sparse.img" in content:
                    # Find line number for better debugging
                    for lineno, line in enumerate(content.splitlines(), 1):
                        if "_patched_sparse.img" in line:
                            violations.append(f"{py_file.name}:{lineno}: {line.strip()[:80]}")
            except Exception as e:
                pass  # Skip unreadable files
        
        self.assertEqual(
            len(violations), 0,
            f"Found *_patched_sparse.img in app/ code (violates naming contract):\n" +
            "\n".join(violations)
        )


if __name__ == "__main__":
    unittest.main()
