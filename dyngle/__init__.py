import sys

from pathlib import Path
from wizlib.app import WizApp
from wizlib.stream_handler import StreamHandler
from wizlib.config_handler import ConfigHandler
from wizlib.ui_handler import UIHandler

from dyngle.command import DyngleCommand
from dyngle.error import DyngleError
from dyngle.model.toolset import Toolset
from dyngle.model.expression import expression
from dyngle.model.operation import Operation
from dyngle.model.template import Template


class DyngleApp(WizApp):

    base = DyngleCommand
    name = "dyngle"
    handlers = [StreamHandler, ConfigHandler, UIHandler]

    @property
    def toolset(self):
        """Offload the indexing of operation and expression definitions to
        another class. But we keep import handling here in the app because we
        might want to upstream import/include to WizLib at some point."""

        if not hasattr(self, "_toolset"):
            self._toolset = Toolset(self)
            root_definitions = self.config.get("dyngle")
            if root_definitions:
                imports = self._get_imports(self.config, [])

                # Phase 1: Load all constants from all configs
                # This ensures operations can access values from any config
                for imported_config in imports:
                    definitions = imported_config.get("dyngle")
                    self._toolset.load_declarations(definitions)
                self._toolset.load_declarations(root_definitions)

                # Phase 2: Load all operations after constants are loaded
                for imported_config in imports:
                    definitions = imported_config.get("dyngle")
                    self._toolset.load_operations(definitions)
                self._toolset.load_operations(root_definitions)
            else:
                self.warn('Config is missing at .dyngle.yml.')
        return self._toolset

    def warn(self, message:str):
        self.ui.send(f'WARNING: {message} See https://dyngle.steamwiz.io for documentation.')


    def _get_imports(
        self, config_handler: ConfigHandler, no_loops: list
    ) -> dict:
        definitions = config_handler.get("dyngle")
        imports = definitions.get("imports")
        confs = []
        if imports:
            for filename in imports:
                import_path = Path(filename).expanduser()
                if not import_path.is_absolute() and config_handler.file:
                    config_dir = Path(config_handler.file).parent
                    full_filename = (config_dir / import_path).resolve()
                else:
                    full_filename = import_path
                if full_filename not in no_loops:
                    no_loops.append(full_filename)
                    child_handler = ConfigHandler(full_filename)
                    confs += self._get_imports(child_handler, no_loops)
                    confs.append(ConfigHandler(full_filename))
        return confs
