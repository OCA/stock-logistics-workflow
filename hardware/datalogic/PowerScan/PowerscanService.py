# -*- coding: utf-8 -*-
##################################################
#
#           POWER SCAN SERVICE
#
##################################################

#----------------------------------------------------------
# Python imports
#----------------------------------------------------------
import sys
import os
import time
import signal

#----------------------------------------------------------
# Specifics imports
#----------------------------------------------------------
import serial
import xmlrpclib
import Powerscan


# Opening XMLRPC
def openxmlrpc():
    global server
    global uid
    server = xmlrpclib.ServerProxy('http://%s:%d/xmlrpc/common' % (HOST, PORT))
    uid = server.login(DB, LOGIN, PASS)
    server = xmlrpclib.ServerProxy('http://%s:%d/xmlrpc/object' % (HOST, PORT))


def displaymenu(PS, menu, indicemenu, deb):
    x.write(PS)
    x.cleardisplay()
    lignes = 4
    if (len(menu) < 4):
        lignes = len(menu)
    for i in range(deb, deb + lignes):
        if i == indicemenu:
            x.fontreversemode()
        else:
            x.fontnormalmode()
        x.write(menu[i])
        x.cursordown("1")
        x.cursorcr()
    x.cr()
    m = x.read()
    if m == PS + ">" + chr(13) + chr(10) and indicemenu < len(menu) - 1:
        if indicemenu == deb + 3:
            deb += 1
        indicemenu += 1
        displaymenu(PS, menu, indicemenu, deb)
    elif m == PS + "<" + chr(13) + chr(10) and indicemenu > 0:
        if indicemenu == deb:
            deb -= 1
        indicemenu -= 1
        displaymenu(PS, menu, indicemenu, deb)
    elif m == PS + "=" + chr(13) + chr(10):
        if menu[indicemenu] == "":
            displaymenu(PS, menu, indicemenu, deb)
        print menu[indicemenu]
    else:
        displaymenu(PS, menu, indicemenu, deb)


def checkquantity(quantity, q):
    x.cleardisplay()
    for i in range(0, 3):
        x.write(quantity[i])
        x.cursordown("1")
        x.cursorcr()
    x.write(q)
    x.cr()
    m = x.read()
    if m == ">" + chr(13) + chr(10):
        q += 1
        checkquantity(quantity, q)
    elif m == "<" + chr(13) + chr(10) and q > 0:
        q -= 1
        checkquantity(quantity, q)
    elif m == "=" + chr(13) + chr(10):
        print q
    else:
        checkquantity(quantity, q)


def flasher(flashage):
    x.cleardisplay()
    for i in range(0, 4):
        x.write(flashage[i])
        x.cursordown("1")
        x.cursorcr()
    x.cr()
    m = x.read()
    if m == "=" + chr(13) + chr(10):
        print "Terminer"
    elif m == ">" + chr(13) + chr(10):
        x.emitshortlow()
        flasher(flashage)
    elif m == "<" + chr(13) + chr(10):
        x.emitshortlow()
        flasher(flashage)
    else:
        print m


def yesnochoice(yesno):
    x.cleardisplay()
    for i in range(0, 3):
        x.write(yesno[i])
        x.cursordown("1")
        x.cursorcr()
    x.write("Non          Oui")
    x.cr()
    m = x.read()
    if m == "=" + chr(13) + chr(10):
        yesnochoice(yesno)
    elif m == ">" + chr(13) + chr(10):
        print "Oui"
    elif m == "<" + chr(13) + chr(10):
        print "Non"
    else:
        yesnochoice(yesno)


def action(message, action):
    x.cleardisplay()
    for i in range(0, 4):
        x.write(message[i])
        x.cursordown("1")
        x.cursorcr()
    x.cr()
    m = m.read()
    # if m == "


def openerp(type, msg):
    return server.execute(DB, uid, PASS, 'scanner.hardware', 'scanner_call', '0000', type, msg)

# tests
LOGIN = 'admin'
PASS = 'admin'
HOST = '127.0.0.1'
PORT = 8069
DB = 'neo7'

global PS
PS = "0001"

indicemenu = 0
pws = Powerscan.Powerscan('/dev/ttyUSB0')
print 'Welcome to PowerScan Sentinel\n\n  '

while True:
    (hwd, msg) = pws.read()
    print '%s -> %s' % (hwd, msg)
    pws.cleardisplay(hwd)
    pws.write("-> %s" % msg)
    pws.cr()
    menu = ['Inventaire', 'Reception', 'Preparation', 'Controle', 'Terminer']
    #displaymenu(PS,menu,0,0)
    pws.cr()
#
#
#
#########################
##
## OLD CODE
##
##########################
## code, val = openerp('menu','')
#
## code = [('<','OK'), ('>','ANN')]
## print code[0][0]
## if code == 'M':
#    # displaymenu(val,0,0)
## elif code == 'Q':
#    # checkquantity(val['label'],val['value'])
## elif code == 'A':
#    # action(val['label'],val['action'])
#
## menu = ['Inventaire','Reception','Preparation','Controle','Terminer']
## displaymenu(menu,0,0)
## flashage = ['Flashez palette','','','Terminer']
## flasher(flashage)
## quantity = ['Nombre de carton','','',20]
## checkquantity(quantity,quantity[3])
## yesno = ['Confirmez','','','']
## yesnochoice(yesno)
##
## x.cr()
##closeserial()
##exit()
##x.greenledon()
##x.cursorcr()


# Signals
def handler(signum, _):
    sys.exit(0)

# Gestion des signaux
LST_SIGNALS = ['SIGINT', 'SIGTERM']
if os.name == 'posix':
    LST_SIGNALS.extend(['SIGUSR1', 'SIGQUIT'])

SIGNALS = dict(
    [(getattr(signal, sign), sign) for sign in LST_SIGNALS],
)

for signum in SIGNALS:
    signal.signal(signum, handler)

while True:
    time.sleep(1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
