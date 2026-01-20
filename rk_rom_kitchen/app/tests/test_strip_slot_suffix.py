"""
Test Strip Slot Suffix
"""
import unittest

from app.core.slot_utils import strip_slot_suffix, normalize_mount_base, get_mount_point


class TestStripSlotSuffix(unittest.TestCase):
    """Test slot suffix stripping"""
    
    def test_strip_slot_a(self):
        """system_a -> system"""
        self.assertEqual(strip_slot_suffix("system_a"), "system")
    
    def test_strip_slot_b(self):
        """vendor_b -> vendor"""
        self.assertEqual(strip_slot_suffix("vendor_b"), "vendor")
    
    def test_no_strip_middle_a(self):
        """data_backup -> data_backup (không cắt _a ở giữa)"""
        self.assertEqual(strip_slot_suffix("data_backup"), "data_backup")
    
    def test_no_strip_no_suffix(self):
        """camera -> camera"""
        self.assertEqual(strip_slot_suffix("camera"), "camera")
    
    def test_normalize_with_slash(self):
        """/vendor_b -> vendor"""
        self.assertEqual(normalize_mount_base("/vendor_b"), "vendor")
    
    def test_get_mount_point(self):
        """system_a -> /system"""
        self.assertEqual(get_mount_point("system_a"), "/system")


if __name__ == "__main__":
    unittest.main()
