"""Main module."""

import os
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

        return



