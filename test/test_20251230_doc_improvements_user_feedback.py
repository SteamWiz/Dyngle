"""Test cases for issues identified in user feedback on 2025-12-30"""
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
import os

from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestDocImprovementsUserFeedback(DyngleTestCase):

    def test_missing_config_file_error(self):
        """Test for warning message when no config file exists and --config is
        not specified"""
        
        with TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                    with self.patchout() as o, self.patcherr() as e:
                        with self.assertRaises(DyngleError) as context:
                            DyngleApp.start("run", debug=True)
            finally:
                os.chdir(original_cwd)
        e.seek(0)
        self.assertIn('Config is missing', e.read())