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
from imghdr import what
from tifffile import (
    imwrite,
    TiffFile
    )
import numpy as np
from models import (
    DataDir,
    Path,
    res_unit_string
    )


# =============================================================================
# Module level constants
# =============================================================================

DPI = 400


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

    @scans_path.setter
    def scans_path(self, resolution):
        """Put method docstring HERE.
        """

        self._resolution = resolution

    @property
    def resolution_units(self):
        """Put method docstring HERE.
        """

        return self._resolution_units

    @scans_path.setter
    def resolution_units(self, resolution_units):
        """Put method docstring HERE.
        """

        self._resolution_units = resolution_units

    def execute(self):
        """Put method docstring HERE.
        """

        # Do some sanity checks first.
        if not self._scans_path.exists:
            print(
                '{0}: Supplied path \'{1}\' does not exist.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            self._exit_app(1)

        if not self._scans_path.isDir:
            print(
                '{0}: Supplied path \'{1}\' is not a dir.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            self._exit_app(2)

        fl = self._scans_path.listDataFiles()

        if fl is None:
            # Supplied path does not exist.
            print(
                '{0}: Supplied path \'{1}\' contains no image files.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            self._exit_app(3)

        # Containter to hold opened image data.
        pixels_data = list()

        # Reference image size. Set from the first image in the dir.
        ref_width = ref_height = None

        # Reference resolution. Set from the first image in the dir.
        ref_res_unit = None

        for path in fl:
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

            else:
                print('Loading image: \'{0}\'.'.format(Path(path).name))
                tif_file = TiffFile(path)

                # We require that dpi persists along both axes and it must be
                # equal to the user set dpi.
                res_x = tif_file.pages[0].tags['XResolution'].value[0]
                res_y = tif_file.pages[0].tags['YResolution'].value[0]
                res_unit = tif_file.pages[0].tags['ResolutionUnit'].value

                if not ref_res_unit:
                    ref_res_unit = res_unit

                if res_x != DPI or res_y != DPI:
                    print(
                        '{0}: Image \'{1}\' does not conform to the required'
                        .format(self._program_name, Path(path).name)
                        + ' resolution: {0}.'.format(DPI),
                        file=stderr
                        )

                elif res_unit != ref_res_unit:
                    print(
                        '{0}: Image \'{1}\' does not conform to the required'
                        .format(self._program_name, Path(path).name)
                        + ' resolution units: {0}.'
                        .format(res_unit_string(ref_res_unit)),
                        file=stderr
                        )

                else:
                    # Read image data as array.
                    pixels = tif_file.asarray().astype(np.float)

                    # Check if image size have been set.
                    if not ref_width:
                        ref_height = pixels.shape[0]
                        ref_width = pixels.shape[1]
                        pixels_data.append(pixels)

                    # If image size is set compare size of the current image
                    # with a reference image size.
                    elif pixels.shape[0] == ref_height\
                            and pixels.shape[1] == ref_width:
                        # Image conforms to the refernce size so put it on the
                        # data stack.
                        pixels_data.append(pixels)

                    else:
                        # Image does not conform to the refernce size so we
                        # can't process it. We dicard the image and inform user
                        # about it.
                        print(
                            '{0}: Image \'{1}\' does not conform to the'
                            .format(self._program_name, Path(path).name)
                            + ' required image size (HxW: {0}x{1}).'
                            .format(ref_height, ref_width),
                            file=stderr
                            )

        if pixels_data:
            # Do some image manipulation just for demo purposes.
            pixels_data[0][:, :, 0] = pixels_data[0][:, :, 0] / 3.0
            pixels_data[0][:, :, 1] = pixels_data[0][:, :, 1] / 3.0
            pixels_data[0][:, :, 2] = pixels_data[0][:, :, 2] / 3.0

            imwrite(
                'demo_result.tif',
                pixels_data[0].astype(np.uint16),
                resolution=(DPI, DPI),
                metadata={'ResolutionUnit': ref_res_unit}
                )

        self._exit_app(0)
