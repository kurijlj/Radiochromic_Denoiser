#!/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

#==============================================================================
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
#==============================================================================


#==============================================================================
#
# 2020-10-25 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * mda.py: created.
#
#==============================================================================


# ============================================================================
#
# TODO:
#   * Implement option switch for imputing required dpi.
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
from models import DataDir
from models import Path
from PIL import Image
from sys import stderr
import cv2
import numpy as np


# =============================================================================
# Module level constants
# =============================================================================

DPI = 400

#==============================================================================
# App action classes
#==============================================================================

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

    def __init__(self, prog, exitf, scans_dir=None):
        super().__init__(exitf)
        self._program_name = prog
        if scans_dir is not None:
            self._scans_path = DataDir(scans_dir, '.tif')
        else:
            # If no path is supplied set current dir as search path.
            self._scans_path = DataDir('.', '.tif')

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
        image_data = list()

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
                img = Image.open(path)

                # We require that dpi persists along both axes and it must be
                # equal to the user set dpi. We use pillow Image.open facility
                # to read the dpi tag, since 'open' does not actually read the
                # image until we access image pixels.
                img_dpi = img.info['dpi']
                img.close() # We don't need image anymore so close it.

                if img_dpi[0] != DPI or img_dpi[1] != DPI:
                    print(
                        '{0}: Image \'{1}\' does not conform to the required'.\
                        format(self._program_name, Path(path).name)
                        + ' dpi: {0}.'.format(DPI),
                        file=stderr
                        )

                else:
                    # Read image data as array.
                    pixel_data = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)\
                        .astype(np.float)
                    image_data.append(pixel_data)

        if image_data:
            # Do some image manipulation just for demo purposes.
            image_data[0][:, :, 0] = image_data[0][:, :, 0] / 3.0
            image_data[0][:, :, 1] = image_data[0][:, :, 1] / 3.0
            image_data[0][:, :, 2] = image_data[0][:, :, 2] / 3.0

            # Save just the red channel.
            cv2.imwrite('result.tif', image_data[0][:, :, 2].astype(np.uint16))

        self._exit_app(0)
