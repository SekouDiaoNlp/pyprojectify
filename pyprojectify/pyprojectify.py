"""Main module."""

import os
import ast
from collections import OrderedDict
from pathlib import Path
from configparser import ConfigParser
import toml
import re

PROJECT_METADATA_ = ('name', 'version', 'author', 'author_email', 'maintainer', 'maintainer_email',
                     'url', 'license', 'description', 'long_description', 'keywords', 'classifiers')

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
        """Parse setup.py into it's Abstract Syntax Tree representation
        and extracts all keyword arguments from the setup() function.
        """
        try:
            with open(file_path, 'r') as f:
                setup_py = f.read()
                setup_py_ast = ast.parse(setup_py, mode='exec')
                assignments = [node for node in setup_py_ast.body if isinstance(node, ast.Assign)]
                self._assignments_dict = {assignment.targets[0].id: self._pluck_value(assignment.value) for assignment in assignments}
                functions = [node for node in setup_py_ast.body if
                             isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
                setup_function = [node for node in functions if node.value.func.id == 'setup'][0]
                setup_function_kwargs = {arg.arg: self._pluck_value(arg.value) for arg in setup_function.value.keywords}
                print('ok')
        except Exception as e:
            logger.error("Failed to parse setup.py: {}".format(e))
            raise e

        return setup_function_kwargs

    def _pluck_value(self, node):
        """Pluck value from ast."""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Name):
            if node.id in self._assignments_dict:
                return self._assignments_dict[node.id]
            else:
                return node.id
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Tuple):
            return tuple(self._pluck_value(n) for n in node.elts)
        elif isinstance(node, ast.List):
            return [self._pluck_value(n) for n in node.elts]
        elif isinstance(node, ast.Dict):
            return {self._pluck_value(k): self._pluck_value(n) for k, n in zip(node.keys, node.values)}
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
        pyproject['build-system']['requires'].extend(setup_py.get('setup_requires', []))

        # populate 'project' key with setup.py metadata
        pyproject['project'] = OrderedDict()
        for key, value in setup_py.items():
            if key in PROJECT_METADATA_:
                if value is not None:
                    pyproject['project'][key] = value
                else:
                    pyproject['project'][key] = ""

        # populate requirements key with setup.py metadata
        pyproject['dependencies'] = setup_py.get('install_requires', [])
        for elmt in setup_py.get('extras_require', {}).values():
            pyproject['dependencies'].extend(elmt)

        # format dependencies
        deps = OrderedDict()
        for i, dep in enumerate(pyproject['dependencies']):
            # split dep on arithmetic comparison operators
            split_dep = re.split(r'([<>=!~]+|\s)', dep)
            deps[split_dep[0]] = ''.join(split_dep[1:])
        pyproject['dependencies'] = deps

        # add project entry-points
        pyproject['script'] = OrderedDict()
        for elmt in setup_py['entry_points']['console_scripts']:
            script_name = elmt[:elmt.index('=')]
            pyproject['script'][script_name] = elmt[elmt.index('=') + 1:]

        if setup_cfg:
            # update pyproject with metadata from setup.cfg
            for key, value in setup_cfg.items():
                if key in PROJECT_METADATA_:
                    pyproject['project'][key] = value

        if manifest_in:
            # update pyproject metadata with metadata from MANIFEST.in
            pyproject['project']['packages'] = []  # TODO: Implement packages detection
            pyproject['project']['include'] = [line[8:] for line in manifest_in if line.startswith('include ')]
            pyproject['project']['exclude'] = [line[8:] for line in manifest_in if line.startswith('exclude ')]

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
            # make a backup of pyproject.toml with pathlib
            pyproject_backup = Path(package_dir) / 'pyproject.toml.bak'
            if pyproject_backup.exists():
                pyproject_backup.unlink()
            old_pyproject = Path(package_dir) / 'pyproject.toml'
            old_pyproject.rename(pyproject_backup)

            # return    # TODO: Prompt user if he wants the file to be over-written

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
            if not generated_pyproject == dict(pyproject):
                raise RuntimeError
        except Exception as e:
            logger.error("Failed to parse generated pyproject.toml: {}".format(e))
            raise e

        return
