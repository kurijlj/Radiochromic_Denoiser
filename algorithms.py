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
# * algorithms.py: created.
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

from imghdr import what
from pathlib import Path
from tifffile import TiffFile


# =============================================================================
# Module level constants
# =============================================================================

# Supported image types by ImageDir and ImageScan classes.
IMAGE_TYPES = (
    'rgb',
    'gif',
    'pbm',
    'pgm',
    'ppm',
    'tiff',
    'rast',
    'xbm',
    'jpeg',
    'bmp',
    'png',
    'webp',
    'exr'
    )


# =============================================================================
# Models classes and functions
# =============================================================================

class ColorChannelOption():
    """TODO: Put class docstring here.
    """

    valid_channels = ('red', 'green', 'blue')

    def __init__(self, chnl=None):
        self._chnl = chnl

    @property
    def int(self):
        """TODO: Put method docstring here.
        """

        if self._chnl is not None:
            if self.isValid():
                map_to_int = {'blue': 0, 'green': 1, 'red': 2}
                return map_to_int[self._chnl]

        return None

    @property
    def value(self):
        """TODO: Put method docstring here.
        """

        return self._chnl

    def isNone(self):
        """TODO: Put method docstring here.
        """

        if self._chnl is None:
            return True

        return False

    def isValid(self):
        """TODO: Put method docstring here.
        """

        if self._chnl is not None:
            if self._chnl in ColorChannelOption.valid_channels:
                return True

            return False

        return True


class DataDir():
    """TODO: Put class docstring here.
    """

    def __init__(self, data_dir=None, data_file_type=None):
        if data_dir is not None:
            self._data_path = Path(data_dir)
        else:
            self._data_path = data_dir

        self._data_file_type = data_file_type

    def _contents(self):
        """TODO: Put method docstring here.
        """

        if self.isDir:
            srchp = '*'
            if self._data_file_type is not None:
                srchp += '.'
                srchp += self._data_file_type

            contents = list()

            for fp in sorted(self._data_path.glob(srchp)):
                # We skip the subdirectories.
                if not fp.is_dir():
                    contents.append(fp.resolve())

            if not contents:
                return None

            return tuple(contents)

        return None

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
    def isEmpty(self):
        """TODO: Put method docstring here.
        """

        if self.isDir:
            contents = self._contents()

            if contents is None:
                # The directory is empty.
                return True

            # The directory contains files of the target file type.
            return False

        return True

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

        if self.isDir:
            return self._contents()

        return None


class ImageDir(DataDir):
    """TODO: Put class docstring here.
    """

    def __init__(self, data_dir=None, image_file_type=None):
        if image_file_type not in IMAGE_TYPES:
            raise ValueError(
                'Image type not supported (\'{0}\')'.format(image_file_type)
                )

        super().__init__(data_dir, image_file_type)

    def _contents(self):
        """TODO: Put method docstring here.
        """

        if self.isDir:
            contents = list()

            for fp in sorted(self._data_path.glob('*')):
                # We skip the subdirectories.
                if not fp.is_dir():
                    contents.append(fp.resolve())

            if not contents:
                return None

            return tuple(contents)

        return None

    @property
    def isEmpty(self):
        """TODO: Put method docstring here.
        """

        if self.isDir:
            contents = self._contents()

            if contents is None:
                return True

            # Directory contain files. Lets check if the target type is set.
            if not self._data_file_type:
                # Directory contains files and target type is not set, so we
                # take any file type as target.
                return False

            # Directory contain files and target file type is set. Check if any
            # file belongs to the target file type.
            for fpath in contents:
                if what(fpath) == self._data_file_type:
                    # We have file of the target type, so directory is not
                    # empty.
                    return False

            # We traversed the entire contents and none of the files in the
            # directory belongs to the target file type, so we take that the
            # directory is empty.
            return True

        return True

    def listDataFiles(self):
        """TODO: Put method docstring here.
        """

        if self.isDir:
            contents = self._contents()

            if contents is None:
                return None

            # Directory contain files. Lets check if the target type is set.
            if not self._data_file_type:
                # Directory contains files and target type is not set, so we
                # take any file type as target.
                return contents

            # Directory contain files and target file type is set. Check if any
            # file belongs to the target file type.
            targets = list()
            for fpath in contents:
                if what(fpath) == self._data_file_type:
                    # We have file of the target type, so add id to the targets
                    # stack.
                    targets.append(fpath)

            # We traversed the entire contents of the directory if the targets
            # list is empty we return None.
            if not targets:
                return None

            # Targets list is not empty so ew return tuple of files that belong
            # to the target file type.
            return targets

        return None


class TiffConformityMatch():
    """TODO: Put class docstring here.
    """

    valid_units = ['dpi', 'dpcm']

    def __init__(
            self,
            target_size=None,
            target_units=None,
            target_resolution=None,
            ):

        self._target_size = target_size
        self._target_units = target_units
        self._target_resolution = target_resolution
        self._tiff_object = None

    @property
    def target_units(self):
        """Put method docstring HERE.
        """

        return self._target_units

    @property
    def target_size(self):
        """Put method docstring HERE.
        """

        return self._target_size

    @property
    def target_resolution(self):
        """Put method docstring HERE.
        """

        return self._target_resolution

    @property
    def tiff_object(self):
        """Put method docstring HERE.
        """

        return self._tiff_object

    @tiff_object.setter
    def tiff_object(self, tiff_object=None):
        """Put method docstring HERE.
        """

        if tiff_object is not None:
            self._tiff_object = tiff_object

    def resolutionMatch(self):
        """Put method docstring HERE.
        """

        if self._target_units is not None:
            if self._tiff_object is not None:
                res_x = self._tiff_object.pages[0].tags['XResolution'].value[0]
                res_y = self._tiff_object.pages[0].tags['YResolution'].value[0]
                if res_x == self._target_resolution \
                        and res_y == self._target_resolution:
                    return True

                return False

        return True

    def sizeMatch(self):
        """Put method docstring HERE.
        """

        if self._tiff_object is not None \
                and self._target_size is not None:
            height = self._tiff_object.pages[0].shape[0]
            width = self._tiff_object.pages[0].shape[1]
            if height == self._target_size[0]\
                    and width == self._target_size[1]:
                return True

        return False

    def unitsMatch(self):
        """Put method docstring HERE.
        """

        if self._target_units is not None:
            if self._tiff_object is not None:
                units = res_unit_string(
                    self._tiff_object.pages[0].tags['ResolutionUnit'].value
                    )
                if units == self._target_units:
                    return True

                return False

        return True

    def validUnits(self):
        """Put method docstring HERE.
        """

        if self._target_units is not None:
            if self._target_units in TiffConformityMatch.valid_units:
                return True

            return False

        return True


def res_unit_string(res_unit):
    """TODO: Put function docstring here.
    """

    if res_unit == 2:
        return 'dpi'

    if res_unit == 3:
        return 'dpcm'

    return 'none'


def res_unit_value(res_unit_str):
    """TODO: Put function docstring here.
    """

    if res_unit_str == 'dpi':
        return 2

    if res_unit_str == 'dpcm':
        return 3

    return 1
