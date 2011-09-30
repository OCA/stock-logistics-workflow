# -*- coding: utf-8 -*-
##############################################################################
#
#    wms_scanner module for OpenERP, Module for manage barcode reader
#    Copyright (C) 2010 NEOLOG (<http://syleam.fr/>)
#              Gabriel Colbeau <gabriel.colbeau@neolog.pro>
#    Copyright (C) 2010 SYLEAM (<http://syleam.fr/>)
#              Christophe Chauvet <christophe.chauvet@syleam.fr>
#
#    This file is a part of wms_scanner
#
#    wms_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wms_scanner is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
This class manage the protocole to establish connection to the scanner
"""

__name__ = "Powerscan"
__version__ = "1.0.0"


class Powerscan:
    """
    Manage Powerscan device
    """
    def __init__(self, scan):
        self._scan = scan
        self._buffer = ''

        self.CR = chr(13)
        self.ESC = chr(27)

    def __str__(self,):
        return '%s: %s\nVersion: %s' % (__name__, self._scan, __version__)

    def __repr__(self,):
        return '%s: %s\nVersion: %s' % (__name__, self._scan, __version__)

    #----------------------------------------------------------
    # Public method
    #----------------------------------------------------------
    def send(self, data=''):
        """
        send data to the serial port
        """
        if not self._buffer:
            self._buffer = self._scan
        if data:
            self._raw_write(data)
        #if self._buffer[-1] != self.CR:
        self._raw_write(self.CR)
        res = self._buffer
        self._buffer = ''
        return res

    #----------------------------------------------------------
    #- Private method -----------------------------------------
    #----------------------------------------------------------
    def _write(self, data):
        """
        Send data with ESC code at the begining
        """
        self._raw_write(data)

    def _raw_write(self, data):
        """ Send raw data """
        if not self._buffer:
            self._buffer = self._scan
        self._buffer += data

    def _command(self, data=''):
        self._raw_write(self.ESC + data)

    # CR char
    def cr(self):
        self._raw_write(self.CR)

    def wait(self):
        return True

    def menu(self, menus):
        return 1

    #----------------------------------------------------------
    # Cursor control
    #----------------------------------------------------------

    # Up n rows, no scroll
    def cursorup(self, row='1'):
        self._command("[" + row + "A")

    # Down n rows, no scroll
    def cursordown(self, row='1'):
        self._command("[" + row + "B")

    def cursorright(self, col):
        """Right n columns"""
        self._command("[" + col + "C")

    def cursorleft(self, col):
        """Left n columns"""
        self._command("[" + col + "D")

    def cursorcr(self):
        """CR"""
        self._command("[G")

    def cursormoveto(self, row, col):
        """Move to row and col"""
        self._command("[" + row + ";" + col + "H")

    def cursorscrolldown(self):
        """Down 1 row with scroll"""
        self._command("D")

    def cursorcrscrolldown(self):
        """CR and cursor down 1 row with scroll"""
        self._command("E")

    def cursorscrollup(self):
        """Up 1 row and scroll"""
        self._command("M")

    #----------------------------------------------------------
    # Font selection
    #----------------------------------------------------------

    def fontnormalmode(self):
        """Normal mode"""
        self._command("[0m")

    def fontreversemode(self):
        """Reverse mode"""
        self._command("[7m")

    def fontlarge(self):
        """Large font (12*16)"""
        self._command("#4")

    def fontnormal(self):
        """Normal font (6*8)"""
        self._command("#5")

    def fontmedium(self):
        """Medium font (8*8)"""
        self._command("#7")

    #----------------------------------------------------------
    # Clearing display
    #----------------------------------------------------------

    def clearlinefromcursor(self):
        """From cursor position to end of line inclusive"""
        self._command("[0K")

    def clearlinetocursor(self):
        """From beginning of line to cursor position (not inclusive)"""
        self._command("[1K")

    def clearline(self):
        """Entire line"""
        self._command("[2K")

    def cleardisplayfromcursor(self):
        """From cursor position to end of display inclusive"""
        self._command("[0J")

    def cleardisplaytocursor(self):
        """From beginning of display to cursor position (not inclusive)"""
        self._command("[1J")

    def cleardisplay(self):
        """Entire display; moves cursor to upper left corner on display"""
        self._command("[2J")

    #----------------------------------------------------------
    # LED and beeper control
    #----------------------------------------------------------
    def emitshorthigh(self):
        """ Emit short High tone + short delay """
        self._command("[0q")

    def emitshortlow(self):
        """ Emit short Low tone + short delay """
        self._command("[1q")

    def emitlonglow(self):
        """ Emit long Low tone + short delay """
        self._command("[2q")

    def emitgoodread(self):
        """ Emit good read tone """
        self._command("[3q")

    def emitbadread(self):
        """ Emit bad tx tone """
        self._command("[4q")

    def emitwait(self):
        """ Wait 100 ms """
        self._command("[5q")

    def greenledon(self):
        """ Turn on the green LED """
        self._command("[6q")

    def greenledoff(self):
        """ Turn off the green LED """
        self._command("[7q")

    def redledon(self):
        """ Turn on the red LED """
        self._command("[8q")

    def redledoff(self):
        """ Turn off the red LED """
        self._command("[9q")



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
