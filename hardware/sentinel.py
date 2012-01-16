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
import math
import ConfigParser
import curses.ascii
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


class Sentinel:
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
            raise Exception('Back')
        return key

    def _read_input(self, echo=True, line=1):
        """
        Read a line of text from the keyboard
        """
        # Echo typed characters if needed
        if echo:
            curses.echo()

        # Get the string from stdin
        value = self.screen.getstr(line, 0)

        # Disable characters echoing
        curses.noecho()

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
        # self.screen.addstr(y, x, unicode(text).encode('utf-8', 'replace'), color)
        self.screen.addstr(y, x, text.encode('ascii', 'replace'), color)

    def main_loop(self):
        """
        Loops until the user asks for ending
        """
        code = False

        while True:
            try:
                # No active scenario, select one
                if not self.scenario_id:
                    (code, result, value) = self._select_scenario()
                    self.scenario_id = result
                else:
                    if code == 'Q':
                        # Quantity selection
                        quantity = self._select_quantity('\n'.join(result), value)
                        (code, result, value) = self.oerp_call('action', quantity)
                    elif code == 'C':
                        # Confirmation query
                        confirm = self._confirm('\n'.join(result))
                        (code, result, value) = self.oerp_call('action', confirm)
                    elif code == 'T':
                        # Text input
                        text = self._input_text('\n'.join(result))
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
                        (code, result, value) = self.oerp_call('action')
                    elif code == 'L':
                        if not isinstance(result, list) or not result:
                            return ('E', ['No value available !'], 0)

                        # Select a value in the list
                        choice = self._menu_choice(result)
                        # Send the result to OpenERP
                        (code, result, value) = self.oerp_call('action', result[choice])
                    elif code == 'F':
                        # End of scenario
                        self.scenario_id = False
                        self._display('\n'.join(result), clear=True)
                        self.getkey()
                    else:
                        # Default call
                        (code, result, value) = self.oerp_call('restart')
            except KeyboardInterrupt, e:
                # If Ctrl+C, exit
                exit(0)
            except:
                (code, result, value) = self.oerp_call('back')
                self.screen.bkgd(0, self._get_color('base'))

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

        # Send the result to OpenERP
        return self.oerp_call('action', values[choice])

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

    def _input_text(self, message):
        """
        Allows the user to input random text
        """
        # Display the menu
        self._display(message, clear=True)

        # Input text from user
        return self._read_input(line=self.window_height - 1)

    def _select_quantity(self, message, quantity):
        """
        Allows the user to select  quantity
        """
        while True:
            # Display the menu
            self._display(message, clear=True)
            # Diplays the selected quantity
            self._display('Selected : %5d' % quantity, y=self.window_height - 1, color='info', modifier=curses.A_BOLD)

            # Get the pushed key
            key = self.getkey()

            if key == '\n':
                # Return key : Validate the choice
                return quantity
            elif key.isdigit():
                # Digit : Add at end of index
                quantity = quantity * 10 + int(key)
            elif key == 'KEY_BACKSPACE' or key == 'KEY_DC':
                # Backspace : Remove last digit from index
                quantity = int(math.floor(quantity / 10))
            elif key == 'KEY_DOWN' or key == 'KEY_LEFT':
                # Down key : Go down in the list
                quantity = quantity - 1
            elif key == 'KEY_UP' or key == 'KEY_RIGHT':
                # Up key : Go up in the list
                quantity = quantity + 1

            quantity = max(0, quantity)

    def _menu_choice(self, entries):
        """
        Allows the user to choose a value in a list
        """
        # Highlighted entry
        highlighted = 0

        # Add line numbers before text
        display = ['%2d: %s' % (entries.index(value), value) for value in entries]

        while True:
            # Display the menu
            self._menu_display(display, highlighted)

            # Get the pushed key
            key = self.getkey()

            if key == '\n':
                # Return key : Validate the choice
                return highlighted
            elif key.isdigit():
                # Digit : Add at end of index
                highlighted = highlighted * 10 + int(key)
            elif key == 'KEY_BACKSPACE' or key == 'KEY_DC':
                # Backspace : Remove last digit from index
                highlighted = int(math.floor(highlighted / 10))
            elif key == 'KEY_DOWN' or key == 'KEY_RIGHT':
                # Down key : Go down in the list
                highlighted = highlighted + 1
            elif key == 'KEY_UP' or key == 'KEY_LEFT':
                # Up key : Go up in the list
                highlighted = highlighted - 1
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
                    return highlighted

            # Avoid going out of the list
            highlighted = min(max(0, highlighted), len(entries) - 1)

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

if __name__ == '__main__':
    try:
        curses.wrapper(Sentinel)
    except KeyboardInterrupt, e:
        exit(0)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
