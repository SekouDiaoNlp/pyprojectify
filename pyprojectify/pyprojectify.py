"""Main module."""

import os
from collections import OrderedDict
from pathlib import Path
from configparser import ConfigParser
import toml

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
                    config = f.readlines()
            else:
                raise ValueError("Unknown config file type: {}".format(config_file.suffix))
        except Exception as e:
            logger.error("Failed to parse config file: {}".format(e))
            raise e

        return config

    @staticmethod
    def _parse_setup_py(file_path: Path):
        """Parse setup.py."""
        try:
            with open(file_path, 'r') as f:
                setup_py = f.readlines()
        except Exception as e:
            logger.error("Failed to parse setup.py: {}".format(e))
            raise e

        return setup_py

    def _build_toml(self, setup_py, setup_cfg, manifest_in):
        """Build pyproject.toml."""
        pyproject = OrderedDict()
        pyproject['tool'] = 'setuptools'
        pyproject['build-backend'] = 'setuptools.build_meta'
        pyproject['requires'] = ['setuptools', 'wheel']
        pyproject['metadata'] = OrderedDict()
        pyproject['metadata']['name'] = 'name'
        pyproject['metadata']['version'] = 'version'
        pyproject['metadata']['author'] = 'author'
        pyproject['metadata']['author_email'] = 'author_email'
        pyproject['metadata']['url'] = 'url'
        pyproject['metadata']['description'] = 'description'
        pyproject['metadata']['long_description'] = 'long_description'
        pyproject['metadata']['long_description_content_type'] = 'text/markdown'
        pyproject['metadata']['classifiers'] = ['Programming Language :: Python :: 3.6', ]
        pyproject['metadata']['keywords'] = []
        pyproject['metadata']['license'] = 'license'
        pyproject['metadata']['packages'] = []
        pyproject['metadata']['package_dir'] = {}
        pyproject['metadata']['package_data'] = {}
        pyproject['metadata']['install_requires'] = []
        pyproject['metadata']['extras_require'] = {}
        pyproject['metadata']['python_requires'] = '>=3.6'
        pyproject['metadata']['zip_safe'] = False
        pyproject['metadata']['entry_points'] = {}
        pyproject['metadata']['test_suite'] = 'tests'
        pyproject['metadata']['tests_require'] = []
        pyproject['metadata']['setup_requires'] = []
        pyproject['metadata']['use_scm_version'] = {}
        pyproject['metadata']['use_scm_version']['write_to'] = '{}/version.py'.format(pyproject['metadata']['name'])
        pyproject['metadata']['use_scm_version']['write_to_template'] = '{version}'
        pyproject['metadata']['use_scm_version']['relative_to'] = '{}'.format(pyproject['metadata']['name'])
        pyproject['metadata']['use_scm_version']['local_scheme'] = 'no-local-version'
        pyproject['metadata']['use_scm_version']['fallback_version'] = '0.0.0'
        pyproject['metadata']['use_scm_version']['version_scheme'] = 'guess-next-dev'
        pyproject['metadata']['use_scm_version']['local_scheme'] = 'dirty-tag'

        if setup_cfg:
            # add setup.cfg
            pyproject['metadata']['setup_requires'] = ['setuptools_scm']

        if manifest_in:
            # add MANIFEST.in
            pyproject['metadata']['packages'] = ['{}'.format(pyproject['metadata']['name'])]
            pyproject['metadata']['package_dir'] = {'{}'.format(pyproject['metadata']['name']): ''}
            pyproject['metadata']['package_data'] = {'{}'.format(pyproject['metadata']['name']): ['*']}

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
            return

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
