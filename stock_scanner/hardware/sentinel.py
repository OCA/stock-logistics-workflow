#!/usr/bin/env python
# -*- coding: utf-8 -*-
# © 2011-2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import sys
import math
import types
import gettext
import textwrap
import traceback
import ConfigParser
import curses.ascii
import unicodedata
from datetime import datetime
from oobjlib.connection import Connection
from oobjlib.component import Object
from functools import reduce

# Translation configuration
I18N_DIR = '%s/i18n/' % os.path.dirname(os.path.realpath(__file__))
I18N_DOMAIN = 'sentinel'
I18N_DEFAULT = 'en_US'


# _ will be initialized by gettext.install but declared to prevent pep8 issues
_ = None

# Default configuration
DEFAULT_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin',
    'port': '8069',
    'test_file': None,
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
        self.datadir = os.path.expanduser("~/")
        config.read([
            '.oerp_sentinelrc',
            '.openerp_sentinelrc',
            '.odoo_sentinelrc',
            os.path.join(self.datadir, '.oerp_sentinelrc'),
            os.path.join(self.datadir, '.openerp_sentinelrc'),
            os.path.join(self.datadir, '.odoo_sentinelrc'),
        ])

        # No configfile found, exit
        if 'openerp' not in config.sections():
            raise Exception('Config Error', 'Config file not found !')

        # Connection to the OpenERP Server
        self.connection = Connection(
            server=config.get('openerp', 'host'),
            dbname=config.get('openerp', 'database'),
            login=config.get('openerp', 'user'),
            password=config.get('openerp', 'password'),
            port=config.get('openerp', 'port'),
        )

        # Open the test file, if any
        test_file_name = config.get('openerp', 'test_file')
        self.test_file = None
        if test_file_name:
            self.test_file = open(test_file_name, 'r')

        # Initialize translations
        self.context = Object(self.connection, 'res.users').context_get()
        lang = self.context.get('lang', I18N_DEFAULT)
        gettext.install(I18N_DOMAIN)
        try:
            language = gettext.translation(
                I18N_DOMAIN, I18N_DIR, languages=[lang])
        except:
            language = gettext.translation(
                I18N_DOMAIN, I18N_DIR, languages=[I18N_DEFAULT])

        # Replace global dummy lambda by the translations gettext method
        # The install method of gettext doesn't replace the function if exists
        global _
        _ = language.gettext

        # Initialize hardware
        self.hardware_obj = Object(self.connection, 'scanner.hardware')
        self.scenario_obj = Object(self.connection, 'scanner.scenario')

        # Initialize window
        self.screen = stdscr
        self._set_screen_size()

        self._init_colors()

        # Get the informations for this material from server (identified by IP)
        self.hardware_code = ''
        self.scenario_id = False
        self.scenario_name = False
        try:
            ssh_data = os.environ['SSH_CONNECTION'].split(' ')
            self.hardware_code = ssh_data[0]
            self.scanner_check()
        except:
            self.hardware_code = self._input_text(
                _('Autoconfiguration failed !\nPlease enter terminal code'))
            self.scanner_check()

        # Resize window to terminal screen size
        self._resize()

        # Reinit colors with values configured in OpenERP
        self._reinit_colors()

        # Initialize mouse events capture
        curses.mousemask(
            curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED)

        # Reinitialize to the main menu when using a test file (useful when
        # the last run has crashed before end)
        if test_file_name:
            self.oerp_call('end')

        # Load the sentinel
        self.main_loop()

    def scanner_check(self):
        self.scenario_id = self.hardware_obj.scanner_check(
            self.hardware_code, self.context)
        if isinstance(self.scenario_id, list):
            self.scenario_id, self.scenario_name = self.scenario_id

    def _resize(self):
        """
        Resizes the window
        """
        # Asks for the hardware screen size
        (width, height) = self.oerp_call('screen_size')[1]
        self._set_screen_size(width, height)

    def _init_colors(self):
        """
        Initialize curses colors
        """
        # Declare all configured color pairs for curses
        for (the_id, front_color, back_color) in COLOR_PAIRS.values():
            curses.init_pair(
                the_id, COLOR_NAMES[front_color], COLOR_NAMES[back_color])

        # Set the default background color
        self.screen.bkgd(0, self._get_color('base'))

    def _reinit_colors(self):
        """
        Initializes the colors from Odoo configuration
        """
        # Asks for the hardware screen size
        colors = self.oerp_call('screen_colors')[1]
        COLOR_PAIRS['base'] = (1, colors['base'][0], colors['base'][1])
        COLOR_PAIRS['info'] = (2, colors['info'][0], colors['info'][1])
        COLOR_PAIRS['error'] = (3, colors['error'][0], colors['error'][1])
        self._init_colors()

    def _set_screen_size(self, width=18, height=6):
        self.window_width = width
        self.window_height = height
        self.screen.resize(height, width)

    def _get_color(self, name):
        """
        Get a curses color's code
        """
        return curses.color_pair(COLOR_PAIRS[name][0])

    def _read_from_file(self):
        """
        Emulates the getkey method of curses, reading from the supplied test
        file
        """
        key = self.test_file.read(1)
        if key == ':':
            # Truncate the trailing "new line" character
            key = self.test_file.readline()[:-1]

        # End of file reached, terminate the sentinel
        if not key:
            self.test_file.close()
            exit(0)

        return key

    def ungetch(self, value):
        """
        Put a value in the keyboard buffer
        """
        curses.ungetch(value)

    def getkey(self):
        """
        Get a user input and avoid Ctrl+C
        """
        if self.test_file:
            # Test file supplied, read from it
            key = self._read_from_file()
        else:
            # Get the pushed character
            key = self.screen.getkey()
        if key == '':
            # Escape key : Return back to the previous step
            raise SentinelBackException('Back')
        return key

    def _display(self, text='', x=0, y=0, clear=False, color='base',
                 bgcolor=False, modifier=curses.A_NORMAL, cursor=None,
                 height=None, scroll=False, title=None):
        """
        Display a line of text
        """
        # Clear the sceen if needed
        if clear:
            self.screen.clear()

        # Display the title, if any
        if title is not None:
            y += 1
            title = title.center(self.window_width)
            self._display(
                title, color='info',
                modifier=curses.A_REVERSE | curses.A_BOLD)

        # Compute the display modifiers
        color = self._get_color(color) | modifier
        # Set background to 'error' colors
        if bgcolor:
            self.screen.bkgd(0, color)

        # Normalize the text, because ncurses doesn't know UTF-8 with
        # python 2.x
        if isinstance(text, str):
            text = text.decode('utf-8')
        text = unicodedata.normalize(
            'NFKD', unicode(text)).encode('ascii', 'ignore')
        text = ''.join(
            [char not in ('\r', '\n') and
             curses.ascii.unctrl(char) or char for char in text])

        # Display the text
        if not scroll:
            self.screen.addstr(y, x, text, color)
        else:
            # Wrap the text to avoid splitting words
            text_lines = []
            for line in text.splitlines():
                text_lines.extend(
                    textwrap.wrap(line, self.window_width - x - 1) or [''])

            # Initialize variables
            first_line = 0
            if height is None:
                height = self.window_height

            (cursor_y, cursor_x) = cursor or (
                self.window_height - 1, self.window_width - 1)

            while True:
                # Display the menu
                self.screen.addstr(height - 1, x,
                                   (self.window_width - x - 1) * ' ', color)
                self.screen.addstr(
                    y, x, '\n'.join(
                        text_lines[first_line:first_line + height - y]),
                    color)

                # Display arrows
                if first_line > 0:
                    self.screen.addch(
                        y, self.window_width - 1, curses.ACS_UARROW)
                if first_line + height < len(text_lines):
                    self.screen.addch(
                        min(height + y - 1, self.window_height - 2),
                        self.window_width - 1, curses.ACS_DARROW)
                else:
                    self.screen.addch(
                        min(height + y - 1, self.window_height - 2),
                        self.window_width - 1, ' ')

                # Set the cursor position
                if height < len(text_lines):
                    scroll_height = len(text_lines) - height
                    position_percent = float(first_line) / scroll_height
                    position = y + min(
                        int(round((height - 1) * position_percent)),
                        self.window_height - 2)
                    self._display(
                        ' ', x=self.window_width - 1, y=position - 1,
                        color='info', modifier=curses.A_REVERSE)
                self.screen.move(cursor_y, cursor_x)

                # Get the pushed key
                key = self.getkey()

                if key == 'KEY_DOWN':
                    # Down key : Go down in the list
                    first_line += 1
                elif key == 'KEY_UP':
                    # Up key : Go up in the list
                    first_line -= 1
                else:
                    # Return the pressed key value
                    return key

                # Avoid going out of the list
                first_line = min(
                    max(0, first_line), max(0, len(text_lines) - height + 1))

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
                        # Search for a step title
                        title = None
                        title_key = '|'
                        if isinstance(result, (types.NoneType, bool)):
                            pass
                        elif (isinstance(result, dict) and
                              result.get(title_key, None)):
                            title = result[title_key]
                            del result[title_key]
                        elif (isinstance(result[0], (tuple, list)) and
                              result[0][0] == title_key):
                            title = result.pop(0)[1]
                        elif (isinstance(result[0], basestring) and
                              result[0].startswith(title_key)):
                            title = result.pop(0)[len(title_key):]

                        if title is None and self.scenario_name:
                            # If no title is defined, display the scenario name
                            title = self.scenario_name

                        if code == 'Q' or code == 'N':
                            # Quantity selection
                            quantity = self._select_quantity(
                                '\n'.join(result), '%g' % value,
                                integer=(code == 'N'), title=title)
                            (code, result, value) = self.oerp_call('action',
                                                                   quantity)
                        elif code == 'C':
                            # Confirmation query
                            confirm = self._confirm(
                                '\n'.join(result), title=title)
                            (code, result, value) = self.oerp_call('action',
                                                                   confirm)
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
                            text = self._input_text(
                                '\n'.join(result), default=default,
                                size=size, title=title)
                            (code, result, value) = self.oerp_call('action',
                                                                   text)
                        elif code == 'R':
                            # Critical error
                            self.scenario_id = False
                            self.scenario_name = False
                            self._display_error('\n'.join(result), title=title)
                        elif code == 'U':
                            # Unknown action : message with return back to the
                            # last state
                            self._display(
                                '\n'.join(result), clear=True, scroll=True,
                                title=title)
                            (code, result, value) = self.oerp_call('back')
                        elif code == 'E':
                            # Error message
                            self._display_error(
                                '\n'.join(result), title=title)
                            # Execute transition
                            if not value:
                                (code, result, value) = self.oerp_call(
                                    'action')
                            else:
                                # Back to the previous step required
                                (code, result, value) = self.oerp_call(
                                    'back')
                        elif code == 'M':
                            # Simple message
                            self._display(
                                '\n'.join(result), clear=True, scroll=True,
                                title=title)
                            # Execute transition
                            (code, result, value) = self.oerp_call('action',
                                                                   value)
                        elif code == 'L':
                            if result:
                                # Select a value in the list
                                choice = self._menu_choice(result, title=title)
                                # Send the result to Odoo
                                (code, result, value) = self.oerp_call(
                                    'action', choice)
                            else:
                                # Empty list supplied, display an error
                                (code, result, value) = (
                                    'E', [_('No value available')], True)

                            # Check if we are in a scenario (to retrieve the
                            # scenario name from a submenu)
                            self.scanner_check()
                            if not self.scenario_id:
                                self.scenario_id = True
                                self.scenario_name = False
                        elif code == 'F':
                            # End of scenario
                            self.scenario_id = False
                            self.scenario_name = False
                            self._display('\n'.join(result), clear=True,
                                          scroll=True, title=title)
                        else:
                            # Default call
                            (code, result, value) = self.oerp_call('restart')
                except SentinelBackException:
                    # Back to the previous step required
                    (code, result, value) = self.oerp_call('back')
                    # Do not display the termination message
                    if code == 'F':
                        self.ungetch(ord('\n'))
                    self.screen.bkgd(0, self._get_color('base'))
                except Exception:
                    # Generates log contents
                    log_contents = """%s
# %s
# Hardware code : %s
# ''Current scenario : %s (%s)
# Current values :
#\tcode : %s
#\tresult : %s
#\tvalue : %s
%s
%s
"""
                    log_contents = log_contents % (
                        '#' * 79, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        self.hardware_code, str(self.scenario_id),
                        self.scenario_name, code, repr(result), repr(value),
                        '#' * 79, reduce(
                            lambda x, y: x + y, traceback.format_exception(
                                sys.exc_info()[0],
                                sys.exc_info()[1],
                                sys.exc_info()[2])))

                    # Writes traceback in log file
                    logfile = open(self.datadir + 'oerp_sentinel.log', 'a')
                    logfile.write(log_contents)
                    logfile.close()

                    # Display error message
                    (code, result, value) = (
                        'E', [_('An error occured\n\nPlease contact your '
                                'administrator')], False)
            except KeyboardInterrupt:
                # If Ctrl+C, exit
                (code, result, value) = self.oerp_call('end')
                # Restore normal background colors
                self.screen.bkgd(0, self._get_color('base'))

    def _display_error(self, error_message, title=None):
        """
        Displays an error message, changing the background to red
        """
        # Display error message
        self._display(error_message, color='error', bgcolor=True, clear=True,
                      scroll=True, title=title)
        # Restore normal background colors
        self.screen.bkgd(0, self._get_color('base'))

    def oerp_call(self, action, message=False):
        """
        Calls a method from Odoo Server
        """
        return self.hardware_obj.scanner_call(
            self.hardware_code, action, message, 'keyboard', self.context)

    def _select_scenario(self):
        """
        Selects a scenario from the server
        """
        # Get the scenarios list from server
        values = self.oerp_call('menu')[1]

        # If no scenario available : return an error
        if not values:
            return ('R', [_('No scenario available !')], 0)

        # Select a scenario in the list
        choice = self._menu_choice(values, title=_('Scenarios'))
        ret = self.oerp_call('action', choice)

        # Store the scenario id and name
        self.scanner_check()
        if not self.scenario_id:
            self.scenario_id = True
            self.scenario_name = False

        # Send the result to OpenERP
        return ret

    def _confirm(self, message, title=None):
        """
        Allows the user to select quantity
        """
        confirm = False

        while True:
            # Clear the screen
            self._display(clear=True)

            # Compute Yes/No positions
            yes_start = 0
            yes_padding = int(math.floor(self.window_width / 2))
            yes_text = _('Yes').center(yes_padding)
            no_start = yes_padding
            no_padding = self.window_width - no_start - 1
            no_text = _('No').center(no_padding)

            if confirm:
                # Yes selected
                yes_modifier = curses.A_BOLD | curses.A_REVERSE
                no_modifier = curses.A_NORMAL
            else:
                # No selected
                yes_modifier = curses.A_NORMAL
                no_modifier = curses.A_BOLD | curses.A_REVERSE

            # Display Yes
            self._display(yes_text, x=yes_start, y=self.window_height - 1,
                          color='info', modifier=yes_modifier)
            # Display No
            self._display(no_text, x=no_start, y=self.window_height - 1,
                          color='info', modifier=no_modifier)

            # Display the confirmation message
            key = self._display(message, scroll=True,
                                height=self.window_height - 1, title=title)

            if key == '\n':
                # Return key : Validate the choice
                return confirm
            elif (key == 'KEY_DOWN' or
                  key == 'KEY_LEFT' or
                  key == 'KEY_UP' or
                  key == 'KEY_RIGHT'):
                # Arrow key : change value
                confirm = not confirm
            elif key.upper() == 'O' or key.upper() == 'Y':
                # O (oui) or Y (yes)
                confirm = True
            elif key.upper() == 'N':
                # N (No)
                confirm = False
            elif key == 'KEY_MOUSE':
                # Retrieve mouse event information
                mouse_info = curses.getmouse()

                # Set the selected entry
                confirm = mouse_info[1] < len(yes_text)

                # If we double clicked, auto-validate
                if mouse_info[4] & curses.BUTTON1_DOUBLE_CLICKED:
                    return confirm

    def _input_text(self, message, default='', size=None, title=None):
        """
        Allows the user to input random text
        """
        # Initialize variables
        value = default
        line = self.window_height - 1
        self.screen.move(line, 0)
        # Flush the input
        curses.flushinp()

        # While we do not validate, store characters
        while True:
            # Clear the screen
            self._display(clear=True)

            # Display the current value if echoing is needed
            display_value = ''.join(
                [curses.ascii.unctrl(char) for char in value])
            display_start = max(0, len(display_value) - self.window_width + 1)
            display_value = display_value[display_start:]
            self._display(' ' * (self.window_width - 1), 0, line)
            self._display(
                display_value, 0, line, color='info', modifier=curses.A_BOLD)
            key = self._display(
                message, scroll=True, height=self.window_height - 1,
                cursor=(line, min(len(value), self.window_width - 1)),
                title=title)

            # Printable character : store in value
            if len(key) == 1 and (curses.ascii.isprint(key) or ord(key) < 32):
                value += key
            # Backspace or del, remove the last character
            elif key == 'KEY_BACKSPACE' or key == 'KEY_DC':
                value = value[:-1]

            # Move cursor at end of the displayed value
            if key == '\n' or (size is not None and len(value) >= size):
                # Flush the input
                curses.flushinp()
                return value.strip()

    def _select_quantity(self, message, quantity='0', integer=False,
                         title=None):
        """
        Allows the user to select  quantity
        """
        # Erase the selected quantity on the first digit key press
        digit_key_pressed = False

        while True:
            # Clear the screen
            self._display(clear=True)
            # Diplays the selected quantity
            self._display(
                _('Selected : %s') % quantity, y=self.window_height - 1,
                color='info', modifier=curses.A_BOLD)

            # Display the message and get the key
            key = self._display(
                message, scroll=True, height=self.window_height - 1,
                title=title)

            if key == '\n':
                # Return key : Validate the choice
                return float(quantity)
            elif key.isdigit():
                if not digit_key_pressed:
                    quantity = '0'
                    digit_key_pressed = True

                # Digit : Add at end
                if quantity == '0':
                    quantity = key
                else:
                    quantity += key
            elif (not integer and
                  '.' not in quantity and
                  (key == '.' or key == ',' or key == '*')):
                # Decimal point
                quantity += '.'
            elif key == 'KEY_BACKSPACE' or key == 'KEY_DC':
                # Backspace : Remove last digit
                quantity = quantity[:-1]
                digit_key_pressed = True
            elif key == 'KEY_DOWN' or key == 'KEY_LEFT':
                # Down key : Decrease
                quantity = '%g' % (float(quantity) - 1)
            elif key == 'KEY_UP' or key == 'KEY_RIGHT':
                # Up key : Increase
                quantity = '%g' % (float(quantity) + 1)

            if not quantity:
                quantity = '0'

    def _menu_choice(self, entries, title=None):
        """
        Allows the user to choose a value in a list
        """
        # If a dict is passed, keep the keys
        keys = entries
        if isinstance(entries, dict):
            keys, entries = entries.items()
        elif isinstance(entries[0], (tuple, list)):
            keys, entries = map(list, zip(*entries))[:2]

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
            display.append(
                '%s: %s' % (str(index).rjust(nb_char),
                            value[:self.window_width - decal]))
            index += 1

        while True:
            # Display the menu
            self._menu_display(display, highlighted, title=title)

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
                first_column = max(
                    0, min(first_column + 1,
                           max_length - self.window_width + decal))
                display = []
                index = 0
                for value in entries:
                    display.append(
                        '%s: %s' % (
                            str(index).rjust(nb_char),
                            value[first_column:
                                  self.window_width - decal + first_column]))
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
                    display.append(
                        '%s: %s' % (
                            str(index).rjust(nb_char),
                            value[first_column:
                                  self.window_width - decal + first_column]))
                    index += 1
            elif key == 'KEY_MOUSE':
                # First line to be displayed
                first_line = 0
                nb_lines = self.window_height - 1
                middle = int(math.floor(nb_lines / 2))

                # Change the first line if there is too much lines for the
                # screen
                if len(entries) > nb_lines and highlighted >= middle:
                    first_line = min(highlighted - middle,
                                     len(entries) - nb_lines)

                # Retrieve mouse event information
                mouse_info = curses.getmouse()

                # Set the selected entry
                highlighted = min(max(0, first_line + mouse_info[2]),
                                  len(entries) - 1)

                # If we double clicked, auto-validate
                if mouse_info[4] & curses.BUTTON1_DOUBLE_CLICKED:
                    return keys[highlighted]

            # Avoid going out of the list
            highlighted %= len(entries)

            # Auto validate if max number is reached
            current_nb_char = int(
                math.floor(math.log10(max(1, highlighted))) + 1)
            if highlighted and digit_key and current_nb_char >= nb_char:
                return keys[highlighted]

    def _menu_display(self, entries, highlighted, title=None):
        """
        Display a menu, highlighting the selected entry
        """
        # First line to be displayed
        first_line = 0
        nb_lines = self.window_height - 1
        if len(entries) > nb_lines:
            nb_lines -= 1
        middle = int(math.floor((nb_lines - 1) / 2))
        # Change the first line if there is too much lines for the screen
        if len(entries) > nb_lines and highlighted >= middle:
            first_line = min(highlighted - middle, len(entries) - nb_lines)

        # Display all entries, normal display
        self._display('\n'.join(entries[first_line:first_line + nb_lines]),
                      clear=True, title=title)
        # Highlight selected entry
        self._display(
            entries[highlighted].ljust(self.window_width - 1),
            y=highlighted - first_line,
            modifier=curses.A_REVERSE | curses.A_BOLD, title=title)

        # Display arrows
        if first_line > 0:
            self.screen.addch(0, self.window_width - 1, curses.ACS_UARROW)
        if first_line + nb_lines < len(entries):
            self.screen.addch(
                nb_lines, self.window_width - 1, curses.ACS_DARROW)

        # Diplays number of the selected entry
        self._display(_('Selected : %d') % highlighted, y=self.window_height-1,
                      color='info', modifier=curses.A_BOLD)

        # Set the cursor position
        if nb_lines < len(entries):
            position_percent = float(highlighted) / len(entries)
            position = int(round(nb_lines * position_percent))
            self._display(
                ' ', x=self.window_width - 1, y=position, color='info',
                modifier=curses.A_REVERSE)
        self.screen.move(self.window_height - 1, self.window_width - 1)


class SentinelException (Exception):
    pass


class SentinelBackException (SentinelException):
    pass


if __name__ == '__main__':
    curses.wrapper(Sentinel)
