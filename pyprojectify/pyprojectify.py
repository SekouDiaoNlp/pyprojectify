"""Main module."""

import os
from pathlib import Path

try:
    from utils import logger
except ModuleNotFoundError or ImportError:
    from .utils import logger


class PyProject:
    """Main class."""
    def __init__(self, package_path=None):
        self.package_path = package_path

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

    def migrate(self):
        """Migrate setuptools project to pyproject.toml"""
        if self.package_path:
            package_dir = self.package_path
        else:
            package_dir = self._get_current_working_directory()

        if not self._has_setup_py(package_dir):
            logger.error("No setup.py found in {}".format(package_dir))
            raise FileNotFoundError

