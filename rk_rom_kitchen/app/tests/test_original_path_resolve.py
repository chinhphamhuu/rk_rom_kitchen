"""
Test Original Path Resolution (Windows Safe)
"""
import unittest
from pathlib import Path
from app.core.utils import resolve_relative_path

class TestOriginalPathResolve(unittest.TestCase):
    """Test resolve_relative_path"""
    
    def test_relative_path_resolution(self):
        """Relative path -> joined with project root (simulate Windows root)"""
        from pathlib import PureWindowsPath
        import ntpath
        
        # Test 1: Windows-style root
        root = PureWindowsPath("C:/fake/project")
        rel = "in/system.img"
        resolved = resolve_relative_path(root, rel)
        
        # Should be C:\fake\project\in\system.img (PureWindowsPath)
        expected = root / rel
        self.assertEqual(str(resolved), str(expected))
        
        # Verify it logic-ally looks absolute according to ntpath
        self.assertTrue(ntpath.isabs(str(resolved)))

    def test_absolute_path_resolution_windows(self):
        """Absolute path (Windows) -> returned as is"""
        from pathlib import PureWindowsPath
        
        root = PureWindowsPath("C:/fake/project")
        abs_path = "D:/tmp/system.img"
        resolved = resolve_relative_path(root, abs_path)
        
        # Normalize to forward slashes for comparison robustness
        self.assertEqual(str(resolved).replace("\\", "/").lower(), "d:/tmp/system.img")
        
        # Should be treated as absolute by internal logic (PureWindowsPath)
        self.assertTrue(resolved.is_absolute())
        



if __name__ == "__main__":
    unittest.main()
