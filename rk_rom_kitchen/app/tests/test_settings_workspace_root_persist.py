"""
Test Settings Persistence for Workspace Root
Verifies BUG P0-1 fix: workspace_root must be saved/loaded correctly
"""
import unittest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch

from app.core import settings_store
from app.core import workspace

class TestSettingsWorkspacePersist(unittest.TestCase):
    
    def setUp(self):
        # 1. Create temp appdata
        self.temp_appdata = Path(tempfile.mkdtemp(prefix="rk_test_appdata_"))
        
        # 2. Patch env APPDATA
        self.env_patcher = patch.dict(os.environ, {"APPDATA": str(self.temp_appdata)})
        self.env_patcher.start()
        
        # 3. Reset SettingsStore Singleton
        settings_store.SettingsStore._instance = None
        
        # 4. Create temp workspace dir
        self.temp_ws = Path(tempfile.mkdtemp(prefix="rk_test_ws_"))

    def tearDown(self):
        self.env_patcher.stop()
        settings_store.SettingsStore._instance = None
        shutil.rmtree(self.temp_appdata, ignore_errors=True)
        shutil.rmtree(self.temp_ws, ignore_errors=True)

    def test_workspace_root_persist(self):
        """Test set_workspace_root persists to settings.json and survives reload"""
        
        # Initial check logic: get_workspace_root should fail
        with self.assertRaises(workspace.WorkspaceNotConfiguredError):
            workspace.get_workspace_root()
            
        # Set workspace
        workspace.set_workspace_root(self.temp_ws)
        
        # Verify immediately
        current = workspace.get_workspace_root()
        self.assertEqual(current.resolve(), self.temp_ws.resolve())
        
        # Verify settings file content
        settings_path = self.temp_appdata / 'rk_kitchen' / 'settings.json'
        self.assertTrue(settings_path.exists())
        content = settings_path.read_text(encoding='utf-8')
        self.assertIn(str(self.temp_ws).replace("\\", "\\\\"), content) # Check JSON escaped path
        
        # Reset Singleton to force reload from disk
        settings_store.SettingsStore._instance = None
        
        # Verify load
        loaded = workspace.get_workspace_root()
        self.assertEqual(loaded.resolve(), self.temp_ws.resolve())

if __name__ == "__main__":
    unittest.main()
