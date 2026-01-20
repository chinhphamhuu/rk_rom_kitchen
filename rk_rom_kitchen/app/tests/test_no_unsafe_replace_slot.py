"""
Test No Unsafe Replace Slot
Đảm bảo không còn replace('_a','') / replace('_b','') unsafe trong runtime code
"""
import unittest
from pathlib import Path


class TestNoUnsafeReplaceSlot(unittest.TestCase):
    """Assert không dùng unsafe replace cho slot suffix"""
    
    def test_no_unsafe_replace_in_runtime_code(self):
        """
        Scan tất cả .py trong app/ (exclude app/tests)
        Assert không chứa unsafe replace patterns
        """
        # Find app directory
        this_file = Path(__file__).resolve()
        tests_dir = this_file.parent  # app/tests
        app_dir = tests_dir.parent    # app/
        
        unsafe_patterns = [
            "replace('_a'",
            'replace("_a"',
            "replace('_b'",
            'replace("_b"',
        ]
        
        violations = []
        
        # Walk app/ excluding tests/
        for py_file in app_dir.rglob("*.py"):
            # Skip test files
            if "tests" in py_file.parts:
                continue
            
            # Allow slot_utils.py (nó chứa docstring nói về vấn đề này)
            if py_file.name == "slot_utils.py":
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in unsafe_patterns:
                    if pattern in content:
                        # Find line number
                        for lineno, line in enumerate(content.splitlines(), 1):
                            if pattern in line:
                                violations.append(f"{py_file.name}:{lineno}: {line.strip()[:80]}")
            except Exception:
                pass
        
        self.assertEqual(
            len(violations), 0,
            f"Found unsafe replace patterns in runtime code:\n" +
            "\n".join(violations)
        )


if __name__ == "__main__":
    unittest.main()
