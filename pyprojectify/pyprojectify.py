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
            logger.info("pyproject.toml already exists in {}".format(package_dir))
            return

        # parse setup.py
        setup_py = Path(package_dir / "setup.py")
        setup_py_content = setup_py.read_text()
        setup_py_lines = [line.strip() for line in setup_py_content.split("\n") if line]
        print('ok')

        # parse setup.cfg
        if self._has_setup_cfg(package_dir):
            setup_cfg = Path(package_dir / "setup.cfg")
            setup_cfg_content = setup_cfg.read_text()
            setup_cfg_lines = [line.strip() for line in setup_cfg_content.split("\n") if line]
            print('ok')

        # parse MANIFEST.in
        if self._has_manifest_in_(package_dir):
            manifest = Path(package_dir / "MANIFEST.in")
            manifest_content = manifest.read_text()
            manifest_lines = [line.strip() for line in manifest_content.split("\n") if line]
            print('ok')

        return



