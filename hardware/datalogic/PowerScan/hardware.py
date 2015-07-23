# flake8: noqa
# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with simple scenarios
#    Copyright (C) 2010 NEOLOG (<http://neolog.pro/>)
#              Gabriel Colbeau <gabriel.colbeau@neolog.pro>
#    Copyright (C) 2010 SYLEAM (<http://syleam.fr/>)
#              Christophe Chauvet <christophe.chauvet@syleam.fr>
#
#    This file is a part of stock_scanner
#
#    stock_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    stock_scanner is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
Manage the serial port for multiple device
"""

import serial
import threading
import sys
import logging
from powerscan import Powerscan
from oobjlib.connection import Connection
from oobjlib.component import Object

__appname__ = 'sentinel'
__version__ = "0.1.0"

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


class Hardware:
    """
    When detect a new hardware, we create a new instance
    """
    def __init__(self, device, connection=None, linewidth=None, debug=False, trace=False):
        ###
        ## Activate debugging with logging module
        self.debug = debug
        self.trace = trace
        level_name = 'info'

        if debug:
            level_name = 'debug'
        level = LEVELS.get(level_name, logging.NOTSET)
        self.log = logging.getLogger('sentinel')
        self.log.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

        self.log.info('OpenERP connection:')
        self.log.info('-   server: %s' % connection.server)
        self.log.info('-     port: %s' % str(connection.port))
        self.log.info('- database: %s' % connection.dbname)

        self.log.info('INIT of hardware')
        self.device = device or '/dev/ttyUSB0'
        self.log.info('Open %s serial port' % self.device)
        self.serial = serial.Serial(self.device)
        self.log.info('Serial port baudrate: 38400')
        self.serial.baudrate = 38400
        if self.serial.isOpen():
            self.log.info('Serial port is already opened, close it to reattribute baudrate')
            self.serial.close()
        self.log.info('Try to open serial port')
        self.serial.open()
        self.log.info('Serial port opened')
        self.alive = False

        ## store each scanner and instanciate Powerscan for each one
        self.scan = {}
        self.auto_answer = {}
        self.next_answer = {}
        self.action = {}
        self.line_width = linewidth or 16

        self.oerp_cnx = connection
        self.oerp_hwd = Object(self.oerp_cnx, 'scanner.hardware')

    #--------------------------------------------------------------------------
    #- Public method ----------------------------------------------------------
    #--------------------------------------------------------------------------
    def start(self):
        """
        Launch thread for reader function
        """
        self.log.debug('Start the thread')
        self.alive = True
        # start thread to check data arrival
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.start()
        self.log.debug('The thread has been started !')

    def stop(self):
        self.alive = False

    def join(self):
        """
        Control the thread
        """
        self.receiver_thread.join()

    def reader(self):
        """
        Loop the serial port and retrieve information
        """
        act = ''
        try:
            while self.alive:
                try:
                    (scan, message) = self.recv()
                    self.log.info('******[%s]**********************************' % scan)
                except KeyboardInterrupt:
                    self.alive = False
                    raise

                self.log_debug(scan, message)
                if message == 'STOP':
                    self.log.debug('==> STOP REQUIRED ! <==============================')
                    self.alive = False
                    self._end_sentinel(scan)
                    continue

                elif message == 'END':
                    self.log.debug('==> END REQUIRED ! <===============================')
                    mess = self.oerp_hwd.scanner_end(scan)
                    self._menu(scan, mess[1], indice=-1)
                    self.auto_answer[scan] = False
                    self.action[scan] = False
                    continue

                err = False
                c = 0

                # We must check the terminal, to see this affectation
                try:
                    scan_state = self.oerp_hwd.scanner_check(scan)
                except Exception:
                    act = 'M'
                    rec_oerp = [self._str_center('Terminal'), self._str_center(scan), self._str_center('not exists!')]
                    self.log_info(scan, 'This scanner is not declare on OpenERP')
                    self._choice(scan, act, rec_oerp, c)
                    continue

                if not scan_state and not self.auto_answer.get(scan, False):
                    # This scanner is not affect to a scenario
                    self.log_debug(scan, 'Scanner not affected to a scenario !')
                    act = 'M'
                    try:
                        (act, rec_oerp, t) = self.oerp_call(scan, 'menu', '')
                        self.log_debug(scan, repr(rec_oerp))
                    except Exception, e:
                        self.log_info(scan, repr(e))
                        rec_oerp = [self._str_center('Please contact'), self._str_center('your'), self._str_center('adminitrator')]
                        err = True

                    self._choice(scan, act, rec_oerp, c)
                    continue

                elif not scan_state and self.auto_answer.get(scan, False):
                    self.log_debug(scan, 'Scanner not affected to a scenario, but already in action')
                    self._analyse_result(scan, message)
                    continue
                elif self.auto_answer.get(scan, False):
                    self.log_debug(scan, 'Scanner in auto answer')
                    self._analyse_result(scan, message)
                    continue
                else:
                    self.log_debug(scan, 'Scanner in normal mode')
                    self._analyse_result(scan, message)
                    continue

        except serial.SerialException, e:
            self.alive = False
            raise

    def recv(self):
        """
        Read the serial and identify which scan send data

        :rtype: tuple
        :return: Scan number and message
        """
        res = self.serial.readline()
        (scan, message) = (res[0:4], res[4:])
        try:
            int(scan)
        except ValueError:
            raise Exception(res)
        message = message.replace(chr(13), '')
        message = message.replace(chr(10), '')
        if not self.scan.get(scan):
            self.scan[scan] = Powerscan(scan)
        return (scan, message)

    def send(self, scan, data=''):
        res = self.scan[scan].send(data)
        if self.trace:
            self.debug_send(res)
        self.serial.write(res)

    def _analyse_result(self, scan, message):
        """
        Analyse the return message
        """
        (act, rec_oerp, c) = self.action.get(scan, ('U', ['close the', 'scenario', 'before'], 0))
        self.log_debug(scan, '_ANALYSE: %s %s (%s)' % (act, rec_oerp, c))
        key = 'B'
        if message in ('<', '>', '='):
            key = 'K'

        if act == 'U':
            (act, rec_oerp, c) = self.oerp_call(scan, 'menu', '')
            self._menu(scan, rec_oerp, indice=0)
        elif act == 'R':
            #self.oerp_hwd.empty_scanner_values([scan])
            (act, rec_oerp, c) = self.oerp_call(scan, 'menu', '')
            self._menu(scan, rec_oerp, indice=0)
        elif act == 'M':
            if message == '<' and c > 0:
                c -= 1
                self._menu(scan, rec_oerp, indice=c)
            elif message == '<' and c == 0:
                # let the indice to zero because it is the first value
                self._menu(scan, rec_oerp, indice=c)
            elif message == '>' and c < len(rec_oerp) - 1:
                c += 1
                self._menu(scan, rec_oerp, indice=c)
            elif message == '>' and c == len(rec_oerp) - 1:
                # we are in the last line
                self._menu(scan, rec_oerp, indice=c)
            elif message == '=':
                # send choice to OpenERP
                # We must remenber the choice
                self.auto_answer[scan] = False
                (act, rec_oerp, t) = self.oerp_call(scan, 'action', rec_oerp[c])
                old_rec_oerp = list(rec_oerp)
                self.log_debug(scan, 'M + = | %s %s %s' % (act, rec_oerp, t))
                if act == 'U':
                    # we make a forbidden action
                    # So we will make nothig and recall menu
                    self._menu(scan, old_rec_oerp, indice=c)
                elif act == 'R':
                    (act, rec_oerp, t) = self.oerp_call(scan, 'menu', '')
                    self._menu(scan, rec_oerp, indice=0)
                else:
                    self._choice(scan, act, rec_oerp, t)
            else:
                self.auto_answer[scan] = False
                old_rec_oerp = list(rec_oerp)
                (act, rec_oerp, t) = self.oerp_call(scan, 'action', message, etype='scan')
                self.log_debug(scan, 'M + = | %s %s %s' % (act, rec_oerp, t))
                if act == 'U':
                    # we make a forbidden action
                    # So we will make nothig and recall menu
                    self._menu(scan, old_rec_oerp, indice=c)
                elif act == 'R':
                    self.oerp_hwd.empty_scanner_values([scan])
                    (act, rec_oerp, t) = self.oerp_call(scan, 'menu', '')
                    self._menu(scan, old_rec_oerp, indice=0)
                else:
                    self._choice(scan, act, rec_oerp, t)

        elif act == 'Q':
            (act, rec_oerp, qty) = self.action[scan]
            qty = int(qty)
            if message == '<':
                qty -= 1
                self._quantity(scan, rec_oerp, qty)
            elif message == '>':
                qty += 1
                self._quantity(scan, rec_oerp, qty)
            elif message == '=':
                self.auto_answer[scan] = False
                (act, rec_oerp, t) = self.oerp_call(scan, 'action', str(qty))
                self.log_debug(scan, 'Q + = | %s %s %s' % (act, rec_oerp, t))
                self._choice(scan, act, rec_oerp, t)
            #else:
            #    raise Exception('No authorized')

        elif act == 'C':
            (act, rec_oerp, c) = self.action[scan]
            if message == '<':
                self._confirmation(scan, rec_oerp)
            elif message == '=':
                self.auto_answer[scan] = False
                (act, rec_oerp, t) = self.oerp_call(scan, 'action', message)
                self.log_debug(scan, 'C + = | %s %s %s' % (act, rec_oerp, t))
                self._choice(scan, act, rec_oerp, t)

    def _choice(self, scan, action, message, plus, error=False):
        """
        Analyse the action to call the good menu
        """
        self.log_debug(scan, '_CHOICE: %s %s (%s)' % (action, message, plus))
        if action == 'M':
            self._menu(scan, message, indice=plus, error=error)
        elif action == 'Q':
            self._quantity(scan, message, plus)
        elif action == 'C':
            self._confirmation(scan, message)
        else:
            self._menu(scan, ['Please contact', 'your', 'administrator'], -1, error=True)

    def _menu(self, scan, menu, line=4, indice=0, current=0, error=False):
        """
        Display menu
        """
        psn = self.scan[scan]
        psn.cleardisplay()
        if len(menu) < line:
            line = len(menu)
        if indice >= line:
            current = int(indice) - int(line) + 1
        for i in range(current, current + line):
            self._add_line(psn, menu[i], i == indice)
        if error:
            psn.redledon()
        self.send(scan, psn.send())
        self.auto_answer[scan] = True
        self.action[scan] = ('M', menu, indice)

    def _quantity(self, scan, menu, qty=0):
        """
        display a quantity and
        """
        psn = self.scan[scan]
        psn.cleardisplay()
        if len(menu) > 2:
            raise Exception('Quantity menu must have only 2 lines')
        self._add_line(psn, menu[0])
        if len(menu) > 1:
            self._add_line(psn, menu[1])
        else:
            self._add_line(psn, ' ')

        # Write the quantity on the 3rd line
        q = str(qty)
        l = 'Qte: '.ljust(16)
        l = l[:self.line_width - len(q)] + q
        self._add_line(psn, l)

        # Write keyboard legend on the 4th line
        self._add_line(psn, '--     OK     ++')

        self.send(scan, psn.send())
        self.auto_answer[scan] = True
        self.action[scan] = ('Q', menu, str(qty))

    def _confirmation(self, scan, message):
        """
        Design screen and ask user to confirm, or retry the entry
        """
        if len(message) > 3:
            raise Exception('Confirmation message must have only 3 lines')

        psn = self.scan[scan]
        psn.cleardisplay()
        cpt = 0
        for m in message:
            cpt += 1
            if m.startswith('_'):
                self._add_line(psn, m[1:], True)
            else:
                self._add_line(psn, m, False)
        while cpt <= 3:
            cpt += 1
            self._add_line(psn, ' ', False)

        self._add_line(psn, 'Back   OK')
        self.send(scan, psn.send())

    def _yes_no(self, scan, message):
        """
        Send a message on a user screen and ask to choose yes or no
        """
        pass

    def _add_line(self, scan, message, reverse_mode=False):
        """
        """
        if reverse_mode:
            scan.fontreversemode()
        else:
            scan.fontnormalmode()
        scan._raw_write(message)
        scan.cursordown()
        scan.cursorcr()

    def _end_sentinel(self, scan):
        """
        This function is called when stop barcode is read
        """
        psn = self.scan[scan]
        psn.cleardisplay()
        self._add_line(psn, 'STOP Required')
        self.send(scan, psn.send())

    def _str_center(self, message):
        """
        Center the message on the user screen
        """
        return message.center(self.line_width)

    ###
    ## Define connection to OpenERP
    ##
    def oerp_call(self, scan, action, message, etype='K'):
        """
        send the datas to OpenERP
        :param etype: Indicate K for keyboard and S for Scan
        :type  etype: str
        """
        self.log_debug(scan, '(%s) %s ' % (action, message))
        return self.oerp_hwd.scanner_call(scan, action, message, etype)

    def debug_send(self, data):
        data = data.replace(chr(27), ' ESC ')
        data = data.replace(chr(13), ' CR')
        self.log_debug(data[:4], '%s' % data[5:])

    def log_info(self, scan, message):
        self.log.info('[%s] %s' % (scan, message))

    def log_debug(self, scan, message):
        self.log.debug('[%s] %s' % (scan, message))

    #--------------------------------------------------------------------------
    #- Private method ---------------------------------------------------------
    #--------------------------------------------------------------------------
    def __del__(self):
        if self.serial.isOpen():
            self.serial.close()
        if self.debug:
            print 'Close the serial port, and detroy this object'

    def __str__(self):
        return 'Connection open to %s (%s bauds)' % (self.device, self.serial.baudrate)

if __name__ == '__main__':
    from optparse import OptionParser, OptionGroup

    usage = "Usage: %prog [options]"
    parser = OptionParser(usage, prog=__appname__,
                          version=__version__)
    parser.add_option('-s', '--server', dest='server',
                      default='localhost',
                      help='Indicate the server name or IP (default: localhost)')
    parser.add_option('-p', '--port', dest='port',
                      default=8069,
                      help='Port (default: 8069)')
    parser.add_option('-d', '--dbname', dest='dbname',
                      default='demo',
                      help='Name of the database (default: demo)')
    parser.add_option('-u', '--user', dest='user',
                      default='admin',
                      help='Select an OpenERP User (default: admin)')
    parser.add_option('-w', '--password', dest='passwd',
                      default='admin',
                      help='Enter the user password (default: admin)')

    material = OptionGroup(parser, 'Material', 'arguments')
    material.add_option('', '--serial-port', dest='serial_port',
                        default='/dev/ttyUSB1',
                        help='Indicate the serial port where the material is connected (default: /dev/ttyUSB1)')
    material.add_option('', '--line-width', dest='line_width',
                       default=16,
                       help='Indicate the width of the screen (default: 16)')
    material.add_option('-v', '--debug', dest='debug',
                        action='store_true',
                        default=False,
                        help='')
    material.add_option('-t', '--serial-trace', dest='trace',
                        action='store_true',
                        default=False,
                        help='Print the code send to the serial port')
    parser.add_option_group(material)

    (opts, args) = parser.parse_args()

    try:
        cnx = Connection(
            server=opts.server,
            dbname=opts.dbname,
            login=opts.user,
            password=opts.passwd,
            port=opts.port)
    except Exception, e:
        print '%s' % str(e)
        sys.exit(2)

    try:
        hwd = Hardware(opts.serial_port, connection=cnx, linewidth=opts.line_width, debug=opts.debug, trace=opts.trace)
    except serial.SerialException, e:
        sys.stderr.write("could not open the serial port")
        sys.exit(1)

    try:
        hwd.start()
        hwd.join()
    except serial.SerialException, e:
        sys.stderr.write('Error on the serial port')
        sys.exit(0)

    sys.stderr.write('User ask to shutdown the program')
    sys.exit(0)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
