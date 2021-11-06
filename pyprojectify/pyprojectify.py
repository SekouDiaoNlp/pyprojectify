"""Main module."""

import os
import ast
from collections import OrderedDict
from pathlib import Path
from configparser import ConfigParser
import toml

KEYWORDS_CLASSIFIERS_ = ('name', 'version', 'author', 'author_email', 'maintainer', 'maintainer_email', 'url', 'license',
                'description', 'long_description', 'keywords', 'classifiers')

try:
    from utils import logger
except ModuleNotFoundError or ImportError:
    from .utils import logger


class PyProject:
    """Main class."""

    def __init__(self, package_path=None):
        self.package_path = Path(package_path)

        return

    def __str__(self):
        return "PyProject"

    def __repr__(self):
        return "PyProject"

    @staticmethod
    def _get_current_working_directory():
        """Get current working directory."""
        return Path.cwd()

    @staticmethod
    def _has_setup_py(path: Path):
        """Check if setup.py exists."""
        setup_py = Path(path / "setup.py")
        return setup_py.is_file()

    @staticmethod
    def _has_setup_cfg(path: Path):
        """Check if setup.cfg exists."""
        setup_cfg = Path(path / "setup.cfg")
        return setup_cfg.is_file()

    @staticmethod
    def _has_manifest_in_(path: Path):
        """Check if MANIFEST.in exists."""
        manifest = Path(path / "MANIFEST.in")
        return manifest.is_file()

    @staticmethod
    def _has_pyproject(path: Path):
        """Check if pyproject.toml exists."""
        pyproject = Path(path / "pyproject.toml")
        return pyproject.is_file()

    @staticmethod
    def _parse_config_file(config_file: Path):
        """Parse config file."""
        try:
            if config_file.suffix == '.toml':
                config = toml.load(config_file)
            elif config_file.suffix in ('.ini', '.cfg'):
                config = ConfigParser()
                config.read(config_file)
            elif config_file.suffix == '.in':
                with open(config_file, 'r') as f:
                    config = [line.rstrip() for line in f.readlines() if not line.startswith('#')]
                    config = [line for line in config if line]
            else:
                raise ValueError("Unknown config file type: {}".format(config_file.suffix))
        except Exception as e:
            logger.error("Failed to parse config file: {}".format(e))
            raise e

        return config

    def _parse_setup_py(self, file_path: Path):
        """Parse setup.py."""
        try:
            with open(file_path, 'r') as f:
                setup_py = f.read()
                setup_py_ast = ast.parse(setup_py, mode='exec')
                functions = [node for node in setup_py_ast.body if
                             isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
                setup_function = [node for node in functions if node.value.func.id == 'setup'][0]
                setup_function_args = [arg.value for arg in setup_function.value.args]
                setup_function_kwargs = {arg.arg: self._pluck_value(arg.value) for arg in setup_function.value.keywords}
                print('ok')
        except Exception as e:
            logger.error("Failed to parse setup.py: {}".format(e))
            raise e

        return setup_function_kwargs

    @staticmethod
    def _pluck_value(node):
        """Pluck constant."""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Tuple):
            return tuple(PyProject._pluck_value(n) for n in node.elts)
        elif isinstance(node, ast.List):
            return [PyProject._pluck_value(n) for n in node.elts]
        elif isinstance(node, ast.Dict):
            return {PyProject._pluck_value(k): PyProject._pluck_value(n) for k, n in zip(node.keys, node.values)}
        else:
            logger.warning("Unknown value type: {}".format(type(node)))
            return None  # TODO: Better handling of unknown types
            # raise ValueError("Unknown value type: {}".format(type(node)))

    @staticmethod
    def _build_toml(setup_py, setup_cfg, manifest_in):
        """Build pyproject.toml."""
        pyproject = OrderedDict()
        pyproject['build-system'] = OrderedDict()
        pyproject['build-system']['build-backend'] = 'setuptools.build_meta'
        pyproject['build-system']['requires'] = ['setuptools', 'wheel']
        pyproject['metadata'] = OrderedDict()
        for key, value in setup_py.items():
            if key in KEYWORDS_CLASSIFIERS_:
                pyproject['metadata'][key] = value

        pyproject['script'] = OrderedDict()
        for elmt in setup_py['entry_points']['console_scripts']:
            script_name = elmt[:elmt.index('=')]
            pyproject['script'][script_name] = elmt[elmt.index('=') + 1:]

        if setup_cfg:
            # update pyproject with metadata from setup.cfg
            for key, value in setup_cfg.items():
                if key in KEYWORDS_CLASSIFIERS_:
                    pyproject['metadata'][key] = value

        if manifest_in:
            # update pyproject metadata with metadata from MANIFEST.in
            pyproject['metadata']['packages'] = []    # TODO: Implement packages detection
            pyproject['metadata']['include'] = [line[8:] for line in manifest_in if line.startswith('include ')]
            pyproject['metadata']['exclude'] = [line[8:] for line in manifest_in if line.startswith('exclude ')]

        return pyproject

    @staticmethod
    def _save_toml(pyproject, file_path):
        """Save pyproject.toml."""
        try:
            with open(file_path, 'w') as f:
                toml.dump(pyproject, f)
        except Exception as e:
            logger.error("Failed to save pyproject.toml: {}".format(e))
            raise e
        return

    def migrate(self):
        """Migrate setuptools project to pyproject.toml"""
        if self.package_path:
            package_dir = self.package_path
        else:
            package_dir = self._get_current_working_directory()

        if not self._has_setup_py(package_dir):
            logger.error("No setup.py found in {}".format(package_dir))
            raise FileNotFoundError

        if self._has_pyproject(package_dir):
            logger.warning("pyproject.toml already exists in {}".format(package_dir))
            # return

        # parse setup.py
        setup_py = self._parse_setup_py(package_dir / "setup.py")

        # parse setup.cfg
        if self._has_setup_cfg(package_dir):
            setup_cfg = self._parse_config_file(package_dir / "setup.cfg")
        else:
            setup_cfg = None

        # parse MANIFEST.in
        if self._has_manifest_in_(package_dir):
            manifest_in = self._parse_config_file(package_dir / "MANIFEST.in")
        else:
            manifest_in = None

        # build pyproject dict
        pyproject = self._build_toml(setup_py, setup_cfg, manifest_in)

        # save pyproject.toml
        self._save_toml(pyproject, package_dir / "pyproject.toml")

        # validate pyproject.toml
        try:
            generated_pyproject = toml.load(package_dir / "pyproject.toml")
        except Exception as e:
            logger.error("Failed to parse generated pyproject.toml: {}".format(e))
            raise e

        return
