"""
Test AVB Patch Oversize Must Fail
Verify that if patched vbmeta exceeds original size, the process fails hard.
"""
import unittest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.core.project_store import Project
from app.core.workspace import Workspace
from app.core.avb_manager import patch_all_vbmeta

class TestVbmetaOversizeMustFail(unittest.TestCase):
    
    def setUp(self):
        self.tmp_dir = Path("temp_oversize_test")
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir()
        
        self.ws = Workspace(self.tmp_dir)
        self.ws.create_project_structure("test_proj")
        self.project = Project("test_proj", workspace=self.ws)
        
        # Create input vbmeta
        self.target = self.project.in_dir / "vbmeta.img"
        self.target.write_bytes(b"ORIG" * 16) # 64 bytes
        self.target_size = self.target.stat().st_size

    def tearDown(self):
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    @patch("app.tools.registry.get_tool_registry")
    @patch("app.core.avb_manager.scan_vbmeta_targets")
    @patch("subprocess.run")
    def test_oversize_fails_critically(self, mock_run, mock_scan, mock_registry):
        """Mock output size > original size -> TaskResult.error"""
        mock_scan.return_value = [self.target]
        mock_registry.return_value.get_tool_path.return_value = "avbtool_fake"
        
        # Mock successful subprocess BUT writes file larger than orig
        def side_effect(args, **kwargs):
            # args contain --output path
            out_path = Path(args[args.index("--output") + 1])
            # Write larger file
            out_path.write_bytes(b"X" * (self.target_size + 100))
            return MagicMock(returncode=0, stderr="")
        mock_run.side_effect = side_effect
        
        # Run
        res = patch_all_vbmeta(self.project)
        
        self.assertFalse(res.ok, "Should fail on oversize")
        self.assertIn("CRITICAL", res.message or str(res.error))
        self.assertIn("Corrupt risk", res.message or str(res.error))
        
        # Verify no output file in destination (other than what was tried to be written then unlinked? 
        # Logic says unlinked temp_path. out_path never moved.)
        out_file = self.project.out_image_dir / "update" / "partitions" / "vbmeta.img"
        self.assertFalse(out_file.exists(), "Should not leave output file")

if __name__ == "__main__":
    unittest.main()
