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
# 2020-10-25 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * mda.py: created.
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

from sys import stderr
from enum import Enum
from imghdr import what
from tifffile import (
    imwrite,
    TiffFile
    )
import numpy as np
from algorithms import (
    DataDir,
    Path,
    res_unit_string,
    res_unit_value
    )


# =============================================================================
# Module level constants
# =============================================================================

DPI = 400


# =============================================================================
# Module utility classes and functions
# =============================================================================

class OptionError(Enum):
    """TODO: Put class docstring here.
    """

    noerror = 0
    wrongunits = 1

class PathError(Enum):
    """TODO: Put class docstring here.
    """

    noerror = 0
    nonexistent = 2
    notdir = 3
    emptydir = 4
    novalidimages = 5


# =============================================================================
# App action classes
# =============================================================================

class ProgramAction():
    """Abstract base class for all program actions, that provides execute.

    The execute method contains code that will actually be executed after
    arguments parsing is finished. The method is called from within method
    run of the CommandLineApp instance.
    """

    def __init__(self, exitf):
        self._exit_app = exitf

    def execute(self):
        """Put method docstring HERE.
        """


class ProgramUsageAction(ProgramAction):
    """Program action that formats and displays usage message to the stdout.
    """

    def __init__(self, parser, exitf):
        super().__init__(exitf)
        self._usg_msg = \
            '{usage}Try \'{prog} --help\' for more information.'\
            .format(usage=parser.format_usage(), prog=parser.prog)

    def execute(self):
        """Put method docstring HERE.
        """

        print(self._usg_msg)
        self._exit_app()


class ShowVersionAction(ProgramAction):
    """Program action that formats and displays program version information
    to the stdout.
    """

    def __init__(self, prog, ver, year, author, license, exitf):
        super().__init__(exitf)
        self._ver_msg = \
            '{0} {1} Copyright (C) {2} {3}\n{4}'\
            .format(prog, ver, year, author, license)

    def execute(self):
        """Put method docstring HERE.
        """

        print(self._ver_msg)
        self._exit_app()


class DefaultAction(ProgramAction):
    """Program action that wraps some specific code to be executed based on
    command line input. In this particular case it prints simple message
    to the stdout.
    """

    def __init__(self, prog, exitf):
        super().__init__(exitf)
        self._program_name = prog
        # Set default path for seraching for film scans.
        self._scans_path = DataDir('.', '.tif')
        self._resolution_units = None
        self._resolution = None
        self._size = {'height': None, 'width': None}
        self._dir_contents = None
        self._for_processing = list()
        self._pixels_data = None

    def _validate_contents(self):
        """Put method docstring HERE.
        """

        for path in self._dir_contents:
            # Traverse file list and check if files in the dir are 'tiff'
            # images and if are of required dpi.
            if what(path) != 'tiff':
                print(
                    '{0}: File \'{1}\' is not an \'.tiff\''.format(
                        self._program_name,
                        Path(path).name
                        ),
                    file=stderr
                    )

                # Not a tiff file so got to next file in the list.
                continue

            print('Loading image: \'{0}\'.'.format(Path(path).name))
            tif_file = TiffFile(path)

            # Are target resolution and resolution units set by the user.
            if self._res_units_set():
                # Resolution and resolution units are set so we have to check
                # if images from the list conform to user set requirements.

                units = res_unit_string(
                    tif_file.pages[0].tags['ResolutionUnit'].value
                    )
                res_x = tif_file.pages[0].tags['XResolution'].value[0]
                res_y = tif_file.pages[0].tags['YResolution'].value[0]

                if units != self._resolution_units:
                    print(
                        '{0}: Image \'{1}\' does not conform to the required'
                        .format(self._program_name, Path(path).name)
                        + ' resolution units: {0}.'
                        .format(self._resolution_units),
                        file=stderr
                        )

                    # Image resolution units don't conform to a user set
                    # resolution units so go to the next image in the list.
                    continue

                if res_x != self._resolution or res_y != self._resolution:
                    print(
                        '{0}: Image \'{1}\' does not conform to the required'
                        .format(self._program_name, Path(path).name)
                        + ' resolution: {0}.'.format(self._resolution),
                        file=stderr
                        )

                    # Image resolution doesn't conform to a user set resolution
                    # units so go to the next image in the list.
                    continue

            # Check if reference image size have been set.
            height = tif_file.pages[0].shape[0]
            width = tif_file.pages[0].shape[1]
            if not self._size['height']:
                self._size['height'] = height
                self._size['width'] = width

            # Compare size of the current image with a reference image size.
            if height != self._size['height']\
                    or width != self._size['width']:
                # Image does not conform to the refernce size so we
                # can't process it. We dicard the image and inform user
                # about it.
                print(
                    '{0}: Image \'{1}\' size is not equal to the size of'
                    .format(self._program_name, Path(path).name)
                    + ' first image in the list (HxW: {0}x{1}).'\
                    .format(self._size['height'], self._size['width']),
                    file=stderr
                    )

                # Image size is not equal to the image size of the first image
                # in the list so we skip this image and go to the next image
                # in the list.
                continue

            # Image size is equal to the refernce image size so put it on the
            # data stack.
            self._for_processing.append(tif_file)

    def _empty_dir(self):
        """Put method docstring HERE.
        """

        fl = self._scans_path.listDataFiles()

        if fl is None:
            # Supplied path contains no files.
            print(
                '{0}: Supplied path \'{1}\' contains no files.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )

            return PathError.emptydir

        return PathError.noerror

    def _res_units_set(self):
        """Put method docstring HERE.
        """

        if self._resolution_units is not None:
            return True

        return False

    def _validate_res_units(self):
        """Put method docstring HERE.
        """

        valid = ['dpi', 'dpcm']

        if self._res_units_set():
            if self._resolution_units in valid:
                return OptionError.noerror

            # Invalid units string passed as option argument.
            print(
                '{0}: Supplied rsolution units \'{1}\' are not supported.'\
                        .format(
                    self._program_name,
                    self._resolution_units
                    ),
                file=stderr
                )
            return OptionError.wrongunits

        # If no units are set we also evaluate that to True.
        return OptionError.noerror

    def _validate_scans_path(self):
        """Put method docstring HERE.
        """

        if not self._scans_path.exists:
            print(
                '{0}: Supplied path \'{1}\' does not exist.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            return PathError.nonexistent

        if not self._scans_path.isDir:
            print(
                '{0}: Supplied path \'{1}\' is not a dir.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            return PathError.notdir

        return PathError.noerror

    @property
    def scans_path(self):
        """Put method docstring HERE.
        """

        return self._scans_path

    @scans_path.setter
    def scans_path(self, scans_path):
        """Put method docstring HERE.
        """

        if scans_path is not None:
            self._scans_path = DataDir(scans_path, '.tif')

    @property
    def resolution(self):
        """Put method docstring HERE.
        """

        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """Put method docstring HERE.
        """

        self._resolution = resolution

    @property
    def resolution_units(self):
        """Put method docstring HERE.
        """

        return self._resolution_units

    @resolution_units.setter
    def resolution_units(self, resolution_units):
        """Put method docstring HERE.
        """

        self._resolution_units = resolution_units

    def execute(self):
        """Put method docstring HERE.
        """

        # Do some sanity checks first. First we chack if all options arguments
        # passed are valid. So verify if correct resolution units are passed
        # as option.
        error = self._validate_res_units()
        if error != OptionError.noerror:
            self._exit_app(error)

        # Then we check if supplied path to scans exists at all, is directory
        # and is not empty.
        error = self._validate_scans_path()
        if error != PathError.noerror:
            self._exit_app(error)

        error = self._empty_dir()
        if error != PathError.noerror:
            self._exit_app(error)

        self._dir_contents = self._scans_path.listDataFiles()

        # Check if contents of the user supplied directory confrom to the
        # specified conditions.
        self._validate_contents()

        if not self._for_processing:
            # Supplied path contains no valid image files.
            print(
                '{0}: Supplied path \'{1}\' contains no valid image files.'\
                        .format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )

            self._exit_app(PathError.novalidimages)

        # Do some image manipulation just for demo purposes.
        # Read image data as array.
        # pixels = tif_file.asarray().astype(np.float)

        # Allocate memory for storage of processed pixel data.
        result = self._for_processing[0].asarray().astype(np.float)

        result[:, :, 0] = result[:, :, 0] / 3.0
        result[:, :, 1] = result[:, :, 1] / 3.0
        result[:, :, 2] = result[:, :, 2] / 3.0

        if self._res_units_set():
            imwrite(
                'demo_result.tif',
                result.astype(np.uint16),
                resolution=(self._resolution, self._resolution),
                metadata={'ResolutionUnit':
                    res_unit_value(self._resolution_units)}
                )

        else:
            imwrite(
                'demo_result.tif',
                result.astype(np.uint16),
                )

        self._exit_app(0)
