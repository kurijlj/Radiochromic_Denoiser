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
# * actions.py: created.
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

from sys import (
    stderr,
    stdout
    )
from os.path import basename
from enum import Enum
from tifffile import (
    imwrite,
    TiffFile
    )
import numpy as np
from algorithms import (
    ColorChannelOption,
    gaussian_kernel,
    ImageDir,
    Path,
    res_unit_value,
    TiffConformityMatch,
    wiener_filter
    )


# =============================================================================
# Module level constants
# =============================================================================


# =============================================================================
# Module utility classes and functions
# =============================================================================

class AppError(Enum):
    """TODO: Put class docstring here.
    """

    noerror = 0
    wrongunits = 1
    nonexistentpath = 2
    notdir = 3
    emptydir = 4
    novalidimages = 5
    invalidcolorchannel = 6


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
        self._scans_path = ImageDir('.', 'tiff')
        self._img_validator = TiffConformityMatch()
        self._selchnl = ColorChannelOption()

    @property
    def color_channel(self):
        """Put method docstring HERE.
        """

        return self._selchnl.value

    @color_channel.setter
    def color_channel(self, chnl):
        """Put method docstring HERE.
        """

        if chnl is not None:
            self._selchnl = ColorChannelOption(chnl)

    @property
    def image_validator(self):
        """Put method docstring HERE.
        """

        return (
            self._img_validator.target_size,
            self._img_validator.target_units,
            self._img_validator.target_resolution
            )

    @property
    def scans_path(self):
        """Put method docstring HERE.
        """

        return self._scans_path.absolutePath

    @scans_path.setter
    def scans_path(self, scans_path):
        """Put method docstring HERE.
        """

        if scans_path is not None:
            self._scans_path = ImageDir(scans_path, 'tiff')

    def execute(self):
        """Put method docstring HERE.
        """

        # Do some sanity checks first. First we chack if all options arguments
        # passed are valid. So verify if correct resolution units are passed
        # as option.
        if not self._img_validator.validUnits():
            # Invalid units string passed as option argument.
            print(
                '{0}: Supplied resolution units \'{1}\' are not supported.'\
                        .format(
                    self._program_name,
                    self._img_validator.target_units
                    ),
                file=stderr
                )
            self._exit_app(AppError.wrongunits)

        # Then we check if supplied path to scans exists at all, is directory
        # and is not empty.
        if not self._scans_path.exists:
            print(
                '{0}: Supplied path \'{1}\' does not exist.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            self._exit_app(AppError.nonexistentpath)

        if not self._scans_path.isDir:
            print(
                '{0}: Supplied path \'{1}\' is not a dir.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            self._exit_app(AppError.notdir)

        if self._scans_path.isEmpty:
            # Supplied path contains no files.
            print(
                '{0}: Supplied path \'{1}\' contains no image files.'.format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            self._exit_app(AppError.emptydir)

        if not self._selchnl.isValid():
            # Color channel option value is not valid.
            print(
                '{0}: Supplied color channel value ({1}) is not supported.'\
                        .format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )
            self._exit_app(AppError.invalidcolorchannel)

        tifs = self._scans_path.listDataFiles()
        valid_tifs = list()

        # Check if contents of the user supplied directory confrom to the
        # specified conditions.
        for tif in tifs:
            print('Loading image: \'{0}\'.'.format(Path(tif).name))
            stdout.flush()
            tif_obj = TiffFile(tif)
            self._img_validator.tiff_object = tif_obj

            if not self._img_validator.unitsMatch():
                print(
                    '{0}: Image \'{1}\' does not conform to the required'
                    .format(self._program_name, basename(tif))
                    + ' resolution units: {0}.'
                    .format(self._img_validator.target_units),
                    file=stderr
                    )
                stdout.flush()

                # Image resolution units don't conform to a user set
                # resolution units so go to the next image in the list.
                continue

            if not self._img_validator.resolutionMatch():
                print(
                    '{0}: Image \'{1}\' does not conform to the required'
                    .format(self._program_name, basename(tif))
                    + ' resolution: {0}.'.format(
                        self._img_validator.target_resolution
                        ),
                    file=stderr
                    )
                stdout.flush()

                # Image resolution doesn't conform to a user set resolution
                # units so go to the next image in the list.
                continue

            # Check if reference image size have been set. If not set reference
            # size from the first image on the stack that confroms with target
            # resolution and units.
            height = tif_obj.pages[0].shape[0]
            width = tif_obj.pages[0].shape[1]
            if self._img_validator.target_size is None:
                self.newImageValidator(
                    (height, width),
                    self.image_validator[1],
                    self.image_validator[2]
                    )
                self._img_validator.tiff_object = tif_obj

            if not self._img_validator.sizeMatch():
                print(
                    '{0}: Image \'{1}\' size is not equal to the size of'
                    .format(self._program_name, basename(tif))
                    + ' first image in the list (HxW: {0}x{1}).'\
                    .format(
                        self._img_validator.target_size[0],
                        self._img_validator.target_size[1]
                        ),
                    file=stderr
                    )
                stdout.flush()

                # Image size is not equal to the image size of the first image
                # in the list so we skip this image and go to the next image
                # in the list.
                continue

            # Image conforms to all requirements so add its data to the stack.
            valid_tifs.append(tif_obj)


        if not valid_tifs:
            # Supplied path contains no valid image files.
            print(
                '{0}: Supplied path \'{1}\' contains no valid image files.'\
                        .format(
                    self._program_name,
                    self._scans_path.absolutePath
                    ),
                file=stderr
                )

            self._exit_app(AppError.novalidimages)

        # Do some image manipulation just for demo purposes.
        # Read image data as array.
        # pixels = tif_file.asarray().astype(np.float)

        # Allocate memory for storage of processed pixel data.
        # result = valid_tifs[0].asarray().astype(np.float)

        # result[:, :, 0] = result[:, :, 0] / 3.0
        # result[:, :, 1] = result[:, :, 1] / 3.0
        # result[:, :, 2] = result[:, :, 2] / 3.0

        print('Averaging images ...')
        stdout.flush()

        result = None
        if self._selchnl.isNone():
            height, width = self._img_validator.target_size
            result = np.zeros((height, width, 3), dtype=np.float)
        else:
            result = np.zeros(self._img_validator.target_size, dtype=np.float)

        weight = len(valid_tifs)

        for tif in valid_tifs:
            data = tif.asarray().astype(np.float)

            if self._selchnl.isNone():
                result[:, :, 0] += (data[:, :, 0] / weight)
                result[:, :, 1] += (data[:, :, 1] / weight)
                result[:, :, 2] += (data[:, :, 2] / weight)

            else:
                result += (data[:, :, self._selchnl.int] / weight)

        # Calculate signal to noise ratio of the averaged image.
        snr = None
        if self._selchnl.isNone():
            snr = (
                # result[:, :, 0].mean() / result[:, :, 0].var(),
                # result[:, :, 1].mean() / result[:, :, 1].var(),
                # result[:, :, 2].mean() / result[:, :, 2].var(),
                result[:, :, 0].mean() / result[:, :, 0].std(),
                result[:, :, 1].mean() / result[:, :, 1].std(),
                result[:, :, 2].mean() / result[:, :, 2].std(),
                )
        else:
            # snr = result.mean() / result.var()
            snr = result.mean() / result.std()

        # Denoise image using Wiener filter.
        print('Applying filter ...')
        stdout.flush()

        kernel = gaussian_kernel(3)
        if self._selchnl.isNone():
            result[:, :, 0] = wiener_filter(result[:, :, 0], kernel, snr[0])
            result[:, :, 1] = wiener_filter(result[:, :, 1], kernel, snr[1])
            result[:, :, 2] = wiener_filter(result[:, :, 2], kernel, snr[2])
        else:
            result = wiener_filter(result, kernel, snr)

        print('Saving result ...')
        stdout.flush()

        if self._img_validator.target_units:
            imwrite(
                'demo_result.tif',
                result.astype(np.uint16),
                resolution=(
                    self._img_validator.target_resolution,
                    self._img_validator.target_resolution
                    ),
                metadata={'ResolutionUnit':
                    res_unit_value(self._img_validator.target_units)}
                )

        else:
            imwrite(
                'demo_result.tif',
                result.astype(np.uint16),
                )

        self._exit_app(0)

    def newImageValidator(self, size=None, units=None, resolution=None):
        """Put method docstring HERE.
        """

        if size is not None or units is not None:
            self._img_validator = TiffConformityMatch(size, units, resolution)
