#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with simple scenarios
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of stock_scanner
#
#    stock_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    stock_scanner is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import sys
import math
import traceback
import ConfigParser
import curses.ascii
import unicodedata
from datetime import datetime
from oobjlib.connection import Connection
from oobjlib.component import Object

# Default configuration
DEFAULT_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin',
    'port': '8069',
}

# Names of the ncurses colors
COLOR_NAMES = {
    'black': curses.COLOR_BLACK,
    'blue': curses.COLOR_BLUE,
    'cyan': curses.COLOR_CYAN,
    'green': curses.COLOR_GREEN,
    'magenta': curses.COLOR_MAGENTA,
    'red': curses.COLOR_RED,
    'white': curses.COLOR_WHITE,
    'yellow': curses.COLOR_YELLOW,
}

# Pre-defined color pairs
COLOR_PAIRS = {
    'base': (1, 'white', 'blue'),
    'info': (2, 'yellow', 'blue'),
    'error': (3, 'yellow', 'red'),
}


class Sentinel(object):
    """
    Sentinel class
    Manages scanner terminals
    """

    def __init__(self, stdscr):
        """
        Initialize the sentinel program
        """
        # Read user configuration
        config = ConfigParser.SafeConfigParser(DEFAULT_CONFIG)
        config.read('.oerp_sentinelrc')

        # No configfile found, exit
        if not 'openerp' in config.sections():
            raise Exception('Config Error', 'Config file not found !')

        # Connection to the OpenERP Server
        self.connection = Connection(
            server=config.get('openerp', 'host'),
            dbname=config.get('openerp', 'database'),
            login=config.get('openerp', 'user'),
            password=config.get('openerp', 'password'),
            port=config.get('openerp', 'port'),
        )

        # Initialize hardware
        self.hardware_obj = Object(self.connection, 'scanner.hardware')

        # Initialize window
        self.screen = stdscr
        self._set_screen_size()

        # Initialize curses colors
        for name, (id, front_color, back_color) in COLOR_PAIRS.items():
            curses.init_pair(id, COLOR_NAMES[front_color], COLOR_NAMES[back_color])
        self.screen.bkgd(0, self._get_color('base'))

        # Get the informations for this material from server (identified by IP)
        self.hardware_code = ''
        self.scenario_id = False
        try:
            ssh_data = os.environ['SSH_CONNECTION'].split(' ')
            self.hardware_code = ssh_data[0]
            self.scenario_id = self.hardware_obj.scanner_check(self.hardware_code)
        except:
            self.hardware_code = self._input_text('Autoconfigurationfailed !\nPlease enter\nterminal code')
            self.scenario_id = self.hardware_obj.scanner_check(self.hardware_code)

        # Resize window to terminal screen size
        self._resize()

        # Initialize mouse events capture
        curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED)

        # Load the sentinel
        self.main_loop()

    def _resize(self):
        """
        Resizes the window
        """
        # Asks for the hardware screen size
        (code, (width, height), value) = self.oerp_call('screen_size')
        self._set_screen_size(width, height)

    def _set_screen_size(self, width=17, height=6):
        self.window_width = width
        self.window_height = height
        self.screen.resize(height, width)

    def _get_color(self, name):
        """
        Get a curses color's code
        """
        return curses.color_pair(COLOR_PAIRS[name][0])

    def getkey(self):
        """
        Get a user input and avoid Ctrl+C
        """
        # Get the pushed character
        key = self.screen.getkey()
        if key == '':
            # Escape key : Return back to the previous step
            raise SentinelBackException('Back')
        return key

    def _read_input(self, echo=True, line=1, default='', size=None):
        """
        Read a line of text from the keyboard
        """
        # Initialize variables
        value = default
        self.screen.move(line, 0)
        key = ''

        # While we do not validate, store characters
        while key != '\n':
            # Printable character : store in value
            if len(key) == 1 and curses.ascii.isprint(key):
                value += key
            # Backspace or del, remove the last character
            elif key == 'KEY_BACKSPACE' or key == 'KEY_DC':
                value = value[:-1]

            # Display the current value if echoing is needed
            if echo:
                display_start = max(0, len(value) - self.window_width + 1)
                display_value = value[display_start:]
                self._display(' ' * (self.window_width - 1), 0, line)
                self._display(display_value, 0, line)

            # Move cursor at end of the displayed value
            if size is not None and len(value) >= size:
                key = '\n'
            else:
                self.screen.move(line, min(len(value), self.window_width - 1))
                key = self.getkey()

        return value

    def _display(self, text, x=0, y=0, clear=False, color='base', bgcolor=False, modifier=curses.A_NORMAL):
        """
        Display a line of text
        """
        # Clear the sceen if needed
        if clear:
            self.screen.clear()

        # No text to display, return
        if not text:
            return

        # Compute the display modifiers
        color = self._get_color(color) | modifier
        # Set background to 'error' colors
        if bgcolor:
            self.screen.bkgd(0, color)

        # Display the text
        self.screen.addstr(y, x, unicodedata.normalize('NFKD', unicode(text)).encode('ascii', 'ignore'), color)

    def main_loop(self):
        """
        Loops until the user asks for ending
        """
        code = False
        result = None
        value = None

        while True:
            try:
                try:
                    # No active scenario, select one
                    if not self.scenario_id:
                        (code, result, value) = self._select_scenario()
                    else:
                        if code == 'Q' or code == 'N':
                            # Quantity selection
                            quantity = self._select_quantity('\n'.join(result), '%g' % value, integer=(code == 'N'))
                            (code, result, value) = self.oerp_call('action', quantity)
                        elif code == 'C':
                            # Confirmation query
                            confirm = self._confirm('\n'.join(result))
                            (code, result, value) = self.oerp_call('action', confirm)
                        elif code == 'T':
                            # Select arguments from value
                            default = ''
                            size = None
                            if isinstance(value, dict):
                                default = value.get('default', '')
                                size = value.get('size', None)
                            elif isinstance(value, str):
                                default = value

                            # Text input
                            text = self._input_text('\n'.join(result), default=default, size=size)
                            (code, result, value) = self.oerp_call('action', text)
                        elif code == 'R':
                            # Error
                            self.scenario_id = False
                            self._display_error('\n'.join(result))
                        elif code == 'U':
                            # Unknown action : message with return back to the last state
                            self._display('\n'.join(result), clear=True)
                            self.getkey()
                            (code, result, value) = self.oerp_call('back')
                        elif code == 'E':
                            # Error message
                            self._display('\n'.join(result), color='error', bgcolor=True, clear=True)
                            self.getkey()
                            # Restore normal background colors
                            self.screen.bkgd(0, self._get_color('base'))
                            # Execute transition
                            (code, result, value) = self.oerp_call('action')
                        elif code == 'M':
                            # Simple message
                            self._display('\n'.join(result), clear=True)
                            self.getkey()
                            # Execute transition
                            (code, result, value) = self.oerp_call('action', value)
                        elif code == 'L':
                            if result:
                                # Select a value in the list
                                choice = self._menu_choice(result)
                                # Send the result to OpenERP
                                (code, result, value) = self.oerp_call('action', choice)
                            else:
                                # Empty list supplied, display an error
                                (code, result, value) = ('E', ['No value available'], False)
                        elif code == 'F':
                            # End of scenario
                            self.scenario_id = False
                            self._display('\n'.join(result), clear=True)
                            self.getkey()
                        else:
                            # Default call
                            (code, result, value) = self.oerp_call('restart')
                except SentinelBackException, e:
                    # Back to the previous step required
                    (code, result, value) = self.oerp_call('back')
                    self.screen.bkgd(0, self._get_color('base'))
                except Exception, e:
                    # Generates log contents
                    log_contents = '%s\n# %s\n# Hardware code : %s\n# Current scenario : %s\n# Current values :\n#\tcode : %s\n#\tresult : %s\n#\tvalue : %s\n%s\n%s\n' % (
                        '#' * 79,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        self.hardware_code,
                        str(self.scenario_id),
                        code,
                        repr(result),
                        repr(value),
                        '#' * 79,
                        reduce(lambda x, y: x + y, traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
                    )

                    # Writes traceback in log file
                    logfile = open('oerp_sentinel.log', 'a')
                    logfile.write(log_contents)
                    logfile.close()

                    # Display error message
                    (code, result, value) = ('E', ['An error occured', '', 'Please contact your', 'administrator'], False)
            except KeyboardInterrupt, e:
                # If Ctrl+C, exit
                (code, result, value) = self.oerp_call('end')

    def _display_error(self, error_message):
        """
        Displays an error messge, changing the background to red
        """
        # Reset scenario_id
        self.scenario_id = False
        self._display(error_message, color='error', bgcolor=True, clear=True)
        self.getkey()
        # Restore normal background colors
        self.screen.bkgd(0, self._get_color('base'))

    def oerp_call(self, action, message=False):
        """
        Calls a method from OpenERP Server
        """
        return self.hardware_obj.scanner_call(self.hardware_code, action, message, 'keyboard')

    def _select_scenario(self):
        """
        Selects a scenario from the server
        """
        # Get the scenarios list from server
        values = self.oerp_call('menu')[1]

        # If no scenario available : return an error
        if not values:
            return ('R', ['No scenario available !'], 0)

        # Select a scenario in the list
        choice = self._menu_choice(values)
        self.scenario_id = choice

        # Send the result to OpenERP
        return self.oerp_call('action', choice)

    def _confirm(self, message):
        """
        Allows the user to select  quantity
        """
        confirm = False

        while True:
            # Display the confirmation message
            self._display(message, clear=True)

            # Compute Yes/No positions
            yes_start = 0
            yes_padding = int(math.floor(self.window_width / 2))
            yes_text = 'Yes'.ljust(int(math.floor(yes_padding / 2)) + 2).rjust(yes_padding)
            no_start = yes_padding
            no_padding = self.window_width - no_start - 1
            no_text = 'No'.ljust(int(math.floor(no_padding / 2)) + 1).rjust(no_padding)

            if confirm:
                # Yes selected
                yes_modifier = curses.A_BOLD | curses.A_REVERSE
                no_modifier = curses.A_NORMAL
            else:
                # No selected
                yes_modifier = curses.A_NORMAL
                no_modifier = curses.A_BOLD | curses.A_REVERSE

            # Display Yes
            self._display(yes_text, x=yes_start, y=self.window_height - 1, color='info', modifier=yes_modifier)
            # Display No
            self._display(no_text, x=no_start, y=self.window_height - 1, color='info', modifier=no_modifier)

            # Get the pushed key
            key = self.getkey()

            if key == '\n':
                # Return key : Validate the choice
                return confirm
            elif key == 'KEY_DOWN' or key == 'KEY_LEFT' or key == 'KEY_UP' or key == 'KEY_RIGHT':
                # Arrow key : change value
                confirm = not confirm
            elif key == 'KEY_MOUSE':
                nb_lines = self.window_height - 1

                # Retrieve mouse event information
                mouse_info = curses.getmouse()

                # Set the selected entry
                confirm = mouse_info[1] < len(yes_text)

                # If we double clicked, auto-validate
                if mouse_info[4] & curses.BUTTON1_DOUBLE_CLICKED:
                    return confirm

    def _input_text(self, message, default='', size=None):
        """
        Allows the user to input random text
        """
        # Display the menu
        self._display(message, clear=True)

        # Input text from user
        return self._read_input(line=self.window_height - 1, default=default, size=size)

    def _select_quantity(self, message, quantity='0', integer=False):
        """
        Allows the user to select  quantity
        """
        while True:
            # Display the menu
            self._display(message, clear=True)
            # Diplays the selected quantity
            self._display('Selected : %s' % quantity, y=self.window_height - 1, color='info', modifier=curses.A_BOLD)

            # Get the pushed key
            key = self.getkey()

            if key == '\n':
                # Return key : Validate the choice
                return quantity
            elif key.isdigit():
                # Digit : Add at end
                if quantity == '0':
                    quantity = key
                else:
                    quantity += key
            elif not integer and not '.' in quantity and key == '.' or key == ',' or key == '*':
                # Decimal point
                quantity += '.'
            elif key == 'KEY_BACKSPACE' or key == 'KEY_DC':
                # Backspace : Remove last digit
                quantity = quantity[:-1]
            elif key == 'KEY_DOWN' or key == 'KEY_LEFT':
                # Down key : Decrease
                quantity = '%g' % (float(quantity) - 1)
            elif key == 'KEY_UP' or key == 'KEY_RIGHT':
                # Up key : Increase
                quantity = '%g' % (float(quantity) + 1)

            if not quantity:
                quantity = '0'

    def _menu_choice(self, entries):
        """
        Allows the user to choose a value in a list
        """
        # If a dict is passed, keep the keys
        keys = entries
        if isinstance(entries, dict):
            keys = entries.keys()
            entries = entries.values()

        # Highlighted entry
        highlighted = 0
        first_column = 0
        max_length = max([len(value) for value in entries])

        # Add line numbers before text
        display = []
        index = 0
        nb_char = int(math.floor(math.log10(len(entries))) + 1)
        decal = nb_char + 3
        for value in entries:
            display.append('%s: %s' % (str(index).rjust(nb_char), value[:self.window_width - decal]))
            index += 1

        while True:
            # Display the menu
            self._menu_display(display, highlighted)

            # Get the pushed key
            key = self.getkey()
            digit_key = False

            if key == '\n':
                # Return key : Validate the choice
                return keys[highlighted]
            elif key.isdigit():
                # Digit : Add at end of index
                highlighted = highlighted * 10 + int(key)
                digit_key = True
            elif key == 'KEY_BACKSPACE' or key == 'KEY_DC':
                # Backspace : Remove last digit from index
                highlighted = int(math.floor(highlighted / 10))
            elif key == 'KEY_DOWN':
                # Down key : Go down in the list
                highlighted = highlighted + 1
            elif key == 'KEY_RIGHT':
                # Move display
                first_column = max(0, min(first_column + 1, max_length - self.window_width + decal))
                display = []
                index = 0
                for value in entries:
                    display.append('%s: %s' % (str(index).rjust(nb_char), value[first_column:self.window_width - decal + first_column]))
                    index += 1
            elif key == 'KEY_UP':
                # Up key : Go up in the list
                highlighted = highlighted - 1
            elif key == 'KEY_LEFT':
                # Move display
                first_column = max(0, first_column - 1)
                display = []
                index = 0
                for value in entries:
                    display.append('%s: %s' % (str(index).rjust(nb_char), value[first_column:self.window_width - decal + first_column]))
                    index += 1
            elif key == 'KEY_MOUSE':
                # First line to be displayed
                first_line = 0
                nb_lines = self.window_height - 1
                middle = int(math.floor((nb_lines - 1) / 2))

                # Change the first line if there is too much lines for the screen
                if len(entries) > nb_lines and highlighted >= middle:
                    first_line = min(highlighted - middle, len(entries) - nb_lines)

                # Retrieve mouse event information
                mouse_info = curses.getmouse()

                # Set the selected entry
                highlighted = min(max(0, first_line + mouse_info[2]), len(entries) - 1)

                # If we double clicked, auto-validate
                if mouse_info[4] & curses.BUTTON1_DOUBLE_CLICKED:
                    return keys[highlighted]

            # Avoid going out of the list
            highlighted = min(max(0, highlighted), len(entries) - 1)

            # Auto validate if max number is reached
            current_nb_char = int(math.floor(math.log10(max(1, highlighted))) + 1)
            if highlighted and digit_key and current_nb_char >= nb_char:
                return keys[highlighted]

    def _menu_display(self, entries, highlighted):
        """
        Display a menu, highlighting the selected entry
        """
        # First line to be displayed
        first_line = 0
        nb_lines = self.window_height - 1
        middle = int(math.floor((nb_lines - 1) / 2))

        # Change the first line if there is too much lines for the screen
        if len(entries) > nb_lines and highlighted >= middle:
            first_line = min(highlighted - middle, len(entries) - nb_lines)

        # Display all entries, normal display
        self._display('\n'.join(entries[first_line:first_line + nb_lines]), clear=True)
        # Highlight selected entry
        self._display(entries[highlighted].ljust(self.window_width - 1), y=highlighted - first_line, modifier=curses.A_REVERSE | curses.A_BOLD)

        # Display arrows
        if first_line > 0:
            self.screen.addch(0, self.window_width - 1, curses.ACS_UARROW)
        if first_line + nb_lines < len(entries):
            self.screen.addch(nb_lines - 1, self.window_width - 1, curses.ACS_DARROW)

        # Diplays number of the selected entry
        self._display('Selected : %d' % highlighted, y=nb_lines, color='info', modifier=curses.A_BOLD)

        # Set the cursor position
        self.screen.move(highlighted - first_line, self.window_width - 1)


class SentinelException (Exception):
    pass


class SentinelBackException (SentinelException):
    pass

if __name__ == '__main__':
    curses.wrapper(Sentinel)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
