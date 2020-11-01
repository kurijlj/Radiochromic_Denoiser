
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
# 2020-11-01 Ljubomir Kurij <kurijlj@gmail.com>
#
# * wtiff_scan_conformity_tsests.py: created.
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

import unittest
from tifffile import TiffFile
from algorithms import (
    res_unit_string,
    TiffConformityMatch
    )


# =============================================================================
# Test cases
# =============================================================================

TEST_TIFFS = [
    TiffFile('./data/QA20200727016.tif'),
    ]


# =============================================================================
# Unit testing classes
# =============================================================================

class TestWithDefaultValues(unittest.TestCase):
    """TODO: Put class docstring HERE.
    """

    def setUp(self):
        """TODO: Put method docstring HERE.
        """

        self._tiff_object = TEST_TIFFS[0]
        self._tiff_validator = TiffConformityMatch()

    def testPropertyTargetUnits(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.target_units, None)

    def testPropertyTargetSize(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.target_size, None)

    def testPropertyTargetResolution(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.target_resolution, None)

    def testPropertyTiffObject(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.tiff_object, None)

    def testForResolutionMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.resolutionMatch(), True)

    def testForSizeMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.sizeMatch(), False)

    def testForUnitsMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.unitsMatch(), True)

    def testSetPropertyTiffObject(self):
        """TODO: Put method docstring HERE.
        """

        self._tiff_validator.tiff_object = self._tiff_object
        self.assertEqual(self._tiff_validator.tiff_object, self._tiff_object)


class TestWithDefaultValuesAndTiffSet(unittest.TestCase):
    """TODO: Put class docstring HERE.
    """

    def setUp(self):
        """TODO: Put method docstring HERE.
        """

        self._tiff_object = TEST_TIFFS[0]
        self._tiff_validator = TiffConformityMatch()
        self._tiff_validator.tiff_object = self._tiff_object

    def testPropertyTargetUnits(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.target_units, None)

    def testPropertyTargetSize(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.target_size, None)

    def testPropertyTargetResolution(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.target_resolution, None)

    def testPropertyTiffObject(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.tiff_object, self._tiff_object)

    def testForResolutionMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.resolutionMatch(), True)

    def testForSizeMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.sizeMatch(), False)

    def testForUnitsMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.unitsMatch(), True)


class TestWithSizeMismatch(unittest.TestCase):
    """TODO: Put class docstring HERE.
    """

    def setUp(self):
        """TODO: Put method docstring HERE.
        """

        self._tiff_object = TEST_TIFFS[0]
        self._tiff_validator = TiffConformityMatch((400, 400))
        self._tiff_validator.tiff_object = self._tiff_object

    def testForSizeMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.sizeMatch(), False)

    def testForUnitsMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.unitsMatch(), True)

    def testForResolutionMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.resolutionMatch(), True)


class TestWithUnitsMismatch(unittest.TestCase):
    """TODO: Put class docstring HERE.
    """

    def setUp(self):
        """TODO: Put method docstring HERE.
        """

        self._tiff_object = TEST_TIFFS[0]
        self._height = self._tiff_object.pages[0].shape[0]
        self._width = self._tiff_object.pages[0].shape[1]
        self._tiff_validator = TiffConformityMatch(
            (self._height, self._width),
            'dpcm'
            )
        self._tiff_validator.tiff_object = self._tiff_object

    def testPropertyTargetSize(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(
            self._tiff_validator.target_size,
            (self._height, self._width)
            )

    def testForSizeMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.sizeMatch(), True)

    def testForUnitsMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.unitsMatch(), False)

    def testForResolutionMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.resolutionMatch(), False)


class TestWithResolutionMismatch(unittest.TestCase):
    """TODO: Put class docstring HERE.
    """

    def setUp(self):
        """TODO: Put method docstring HERE.
        """

        self._tiff_object = TEST_TIFFS[0]
        self._height = self._tiff_object.pages[0].shape[0]
        self._width = self._tiff_object.pages[0].shape[1]
        self._units = self._tiff_object.pages[0].tags['ResolutionUnit'].value
        self._tiff_validator = TiffConformityMatch(
            (self._height, self._width),
            res_unit_string(self._units),
            700
            )
        self._tiff_validator.tiff_object = self._tiff_object

    def testPropertyTargetSize(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(
            self._tiff_validator.target_size,
            (self._height, self._width)
            )

    def testForSizeMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.sizeMatch(), True)

    def testForUnitsMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.unitsMatch(), True)

    def testForResolutionMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.resolutionMatch(), False)


class TestWithFullMatch(unittest.TestCase):
    """TODO: Put class docstring HERE.
    """

    def setUp(self):
        """TODO: Put method docstring HERE.
        """

        self._tiff_object = TEST_TIFFS[0]
        self._height = self._tiff_object.pages[0].shape[0]
        self._width = self._tiff_object.pages[0].shape[1]
        self._units = self._tiff_object.pages[0].tags['ResolutionUnit'].value
        self._resolution = self._tiff_object.pages[0].tags['XResolution']\
                .value[0]
        self._tiff_validator = TiffConformityMatch(
            (self._height, self._width),
            res_unit_string(self._units),
            self._resolution
            )
        self._tiff_validator.tiff_object = self._tiff_object

    def testPropertyTargetSize(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(
            self._tiff_validator.target_size,
            (self._height, self._width)
            )

    def testForSizeMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.sizeMatch(), True)

    def testForUnitsMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.unitsMatch(), True)

    def testForResolutionMatch(self):
        """TODO: Put method docstring HERE.
        """

        self.assertEqual(self._tiff_validator.resolutionMatch(), True)


# =============================================================================
# Script main body
# =============================================================================

if __name__ == '__main__':
    unittest.main()
