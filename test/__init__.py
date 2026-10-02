from contextlib import contextmanager
from io import StringIO
from tempfile import NamedTemporaryFile
from unittest.mock import Mock, patch
import subprocess

from wizlib.test_case import WizLibTestCase

from dyngle import DyngleApp
from dyngle.model.operation import run_subprocess

DyngleApp.initialize()

class TestableSubprocessRunner:
    """For testing - a patch for run_subprocess that always captures outputs
    for assertions. If the production code is not capturing output, then also
    route to stdio as usual."""

    def __init__(self):
        self.captured = ''

    def __call__(self, command:list, input:str='', show_stdout:bool=True, capture_stdout:bool=False):
        designated_capture = capture_stdout
        returncode, captured = run_subprocess(command, input, show_stdout, True)
        self.captured += captured if show_stdout else ''
        return returncode, captured if designated_capture else None


class DyngleTestCase(WizLibTestCase):

    def mock_subprocess_runner(self):
        mock_run = Mock()
        mock_run.return_value = 0, ''
        return patch("dyngle.model.operation.run_subprocess", mock_run)

    def subprocess_runner_trap(self):
        return patch("dyngle.model.operation.run_subprocess", TestableSubprocessRunner())

    @contextmanager
    def configured_app(self, config_string):
        with NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write(config_string)
            f.seek(0)
            f.flush()
            try:
                app = DyngleApp(config=f.name)
                with self.patchout() as o, self.patcherr() as e:
                    try:
                        yield app, o, e
                    finally:
                        o.seek(0)
                        e.seek(0)
            finally:
                pass
