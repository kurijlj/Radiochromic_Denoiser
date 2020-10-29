#!/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2020 Ljubomir Kurij <kurijlj@gmail.com>
#
# This file is part of Radiochromic Denoiser.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================


# =============================================================================
#
# 2020-10-24 Ljubomir Kurij <ljubomir_kurij@protonmail.com.com>
#
# * models.py: created.
#
# =============================================================================


# ============================================================================
#
# TODO:
#
#
# ============================================================================


# ============================================================================
#
# References (this section should be deleted in the release version)
#
#
# ============================================================================

# =============================================================================
# Modules import section
# =============================================================================

from pathlib import Path


# =============================================================================
# Module level constants
# =============================================================================


# =============================================================================
# Models classes and functions
# =============================================================================

class DataDir():
    """TODO: Put class docstring here.
    """

    def __init__(self, data_dir=None, data_file_type=None):
        if data_dir is not None:
            self._data_path = Path(data_dir)
        else:
            self._data_path = data_dir

        self._data_file_type = data_file_type

    @property
    def absolutePath(self):
        """TODO: Put method docstring here.
        """

        if self._data_path is not None:
            return self._data_path.resolve()

        return None

    @property
    def dataFileType(self):
        """TODO: Put method docstring here.
        """

        if self._data_file_type is None:
            return 'Any'

        return self._data_file_type

    @property
    def exists(self):
        """TODO: Put method docstring here.
        """

        if self._data_path is not None:
            return self._data_path.exists()

        return False

    @property
    def isDir(self):
        """TODO: Put method docstring here.
        """

        if self._data_path is not None:
            return self._data_path.is_dir()

        return False

    @property
    def isFile(self):
        """TODO: Put method docstring here.
        """

        if self._data_path is not None:
            return self._data_path.is_file()

        return False

    @property
    def isNone(self):
        """TODO: Put method docstring here.
        """

        if self._data_path is None:
            return True

        return False

    @property
    def name(self):
        """TODO: Put method docstring here.
        """

        if self._data_path is not None:
            return self._data_path.name

        return None


    def listDataFiles(self):
        """TODO: Put method docstring here.
        """

        if self._data_path is not None:
            pattern = self._data_file_type
            if pattern is None:
                # None means serch for all files.
                pattern = '*'
            else:
                # Prepend asterix to a file type.
                pattern = '*' + pattern

            fl = list()
            for fp in sorted(self._data_path.glob(pattern)):
                fl.append(fp.resolve())

            if fl:
                return tuple(fl)

            return None

        return None


def res_unit_string(res_unit):
    """TODO: Put function docstring here.
    """

    if res_unit == 2:
        return 'dpi'

    if res_unit == 3:
        return 'dpcm'

    return 'none'
