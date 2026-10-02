from pathlib import Path
from tempfile import TemporaryDirectory

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestImportsResolveRelativeToImporter(DyngleTestCase):
    """Test that import paths are resolved relative to the importing file,
    not relative to the current working directory."""

    def test_import_with_relative_path(self):
        """Test that a config can import another config using a relative
        path."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create a subdirectory
            subdir = tmppath / "configs"
            subdir.mkdir()

            # Create an imported config in the subdirectory
            imported_config = subdir / "imported.yml"
            y1 = {"dyngle": {"operations": {"task_a": ["echo imported"]}}}
            with open(imported_config, "w") as f:
                safe_dump(y1, f)

            # Create a main config in the subdirectory that imports using
            # relative path
            main_config = subdir / "main.yml"
            y2 = {
                "dyngle": {
                    "imports": [
                        "imported.yml"
                    ],  # Relative to main.yml location
                    "operations": {"task_b": ["echo main"]},
                }
            }
            with open(main_config, "w") as f:
                safe_dump(y2, f)

            # Run from a different directory (tmppath, not subdir)
            # This tests that the import is resolved relative to main.yml,
            # not relative to CWD
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start(
                    "--config", str(main_config), "run", "task_a", debug=True
                )

            # Should find task_a from imported.yml
            c = p.call_args.args[0]
            self.assertEqual(c, ["echo", "imported"])

    def test_nested_imports_with_relative_paths(self):
        """Test that nested imports resolve paths relative to each importing
        file."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create directory structure:
            # tmpdir/
            #   level1/
            #     config1.yml (imports ../level2/config2.yml)
            #   level2/
            #     config2.yml (imports sibling.yml)
            #     sibling.yml

            level1 = tmppath / "level1"
            level1.mkdir()
            level2 = tmppath / "level2"
            level2.mkdir()

            # Create sibling.yml in level2
            sibling_config = level2 / "sibling.yml"
            y1 = {"dyngle": {"operations": {"task_deep": ["echo sibling"]}}}
            with open(sibling_config, "w") as f:
                safe_dump(y1, f)

            # Create config2.yml in level2 that imports sibling.yml
            config2 = level2 / "config2.yml"
            y2 = {
                "dyngle": {
                    "imports": ["sibling.yml"],  # Relative to config2.yml
                    "operations": {"task_mid": ["echo level2"]},
                }
            }
            with open(config2, "w") as f:
                safe_dump(y2, f)

            # Create config1.yml in level1 that imports ../level2/config2.yml
            config1 = level1 / "config1.yml"
            y3 = {
                "dyngle": {
                    # Relative to config1.yml
                    "imports": ["../level2/config2.yml"],
                    "operations": {"task_top": ["echo level1"]},
                }
            }
            with open(config1, "w") as f:
                safe_dump(y3, f)

            # Run from tmppath (different from all config locations)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start(
                    "--config", str(config1), "run", "task_deep", debug=True
                )

            # Should find task_deep from sibling.yml through nested imports
            c = p.call_args.args[0]
            self.assertEqual(c, ["echo", "sibling"])

    def test_import_from_parent_directory(self):
        """Test importing a config from a parent directory using relative
        path."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create:
            # tmpdir/
            #   parent.yml
            #   subdir/
            #     child.yml (imports ../parent.yml)

            subdir = tmppath / "subdir"
            subdir.mkdir()

            # Create parent.yml in root
            parent_config = tmppath / "parent.yml"
            y1 = {"dyngle": {"operations": {"task_parent": ["echo parent"]}}}
            with open(parent_config, "w") as f:
                safe_dump(y1, f)

            # Create child.yml that imports from parent directory
            child_config = subdir / "child.yml"
            y2 = {
                "dyngle": {
                    "imports": ["../parent.yml"],  # Relative to child.yml
                    "operations": {"task_child": ["echo child"]},
                }
            }
            with open(child_config, "w") as f:
                safe_dump(y2, f)

            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start(
                    "--config",
                    str(child_config),
                    "run",
                    "task_parent",
                    debug=True,
                )

            # Should find task_parent from parent.yml
            c = p.call_args.args[0]
            self.assertEqual(c, ["echo", "parent"])

    def test_absolute_path_still_works(self):
        """Test that absolute import paths still work as expected."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            imported_config = tmppath / "imported.yml"
            y1 = {"dyngle": {"operations": {"task_abs": ["echo absolute"]}}}
            with open(imported_config, "w") as f:
                safe_dump(y1, f)

            main_config = tmppath / "main.yml"
            y2 = {
                "dyngle": {
                    "imports": [str(imported_config)],  # Absolute path
                    "operations": {"task_main": ["echo main"]},
                }
            }
            with open(main_config, "w") as f:
                safe_dump(y2, f)

            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start(
                    "--config", str(main_config), "run", "task_abs", debug=True
                )

            # Should still work with absolute paths
            c = p.call_args.args[0]
            self.assertEqual(c, ["echo", "absolute"])
