import importlib
import sys
from pathlib import Path
from app.plugins.base import DataSourcePlugin


class PluginLoader:
    def __init__(self):
        self._plugins: dict[str, DataSourcePlugin] = {}
        self._extension_map: dict[str, DataSourcePlugin] = {}

    def load_builtin(self):
        builtin_dir = Path(__file__).parent / "builtin"
        for py_file in builtin_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            module_name = f"app.plugins.builtin.{py_file.stem}"
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and issubclass(attr, DataSourcePlugin)
                        and attr is not DataSourcePlugin):
                    instance = attr()
                    self._plugins[py_file.stem] = instance
                    for ext in instance.supported_extensions():
                        self._extension_map[ext] = instance

    def load_community(self, community_dir: Path):
        if not community_dir.exists():
            return
        sys.path.insert(0, str(community_dir))
        for py_file in community_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            module = importlib.import_module(py_file.stem)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and issubclass(attr, DataSourcePlugin)
                        and attr is not DataSourcePlugin):
                    instance = attr()
                    self._plugins[py_file.stem] = instance
                    for ext in instance.supported_extensions():
                        self._extension_map[ext] = instance
        sys.path.pop(0)

    def get_plugin(self, file_path: Path) -> DataSourcePlugin | None:
        return self._extension_map.get(file_path.suffix.lower())

    def get_all_plugins(self) -> list[DataSourcePlugin]:
        return list(self._plugins.values())
