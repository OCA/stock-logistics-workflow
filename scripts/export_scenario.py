#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    wms_scanner module for OpenERP, Module for manage barcode reader
#    Copyright (C) 2011 SYLEAM (<http://www.syleam.fr/>)
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
#              Jean-Sébastien SUZANNE <jean-sebastien.suzanne@syleam.fr>
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

from oobjlib.connection import Connection
from oobjlib.component import Object
from oobjlib.common import GetParser
from optparse import OptionGroup
from lxml.etree import Element, SubElement
from lxml.etree import tostring
import uuid
import os

import logging
import sys

parser = GetParser('Export scenario', '0.1')
group = OptionGroup(parser, "Object arguments",
        "Application Options")
group.add_option('-v', '--verbose', dest='verbose',
                 action='store_true',
                 default=False,
                 help='Add verbose mode')
group.add_option('', '--header', dest='header',
                action='store_true',
                default=False,
                help='Add XML and OpenObkect Header')
group.add_option('', '--indent', dest='indent',
                action='store_true',
                default=False,
                help='Indent the XML output')
group.add_option('', '--id', dest='scenario_id',
                 default=False,
                 help='id of the scenario to extract')
group.add_option('', '--directory', dest='directory',
                 default='.',
                 help='directory where the script will write the scenario files')
parser.add_option_group(group)
opts, args = parser.parse_args()

logger = logging.getLogger("check_parent_store")
ch = logging.StreamHandler()
if opts.verbose:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

try:
    logger.info('Open connection to "%s:%s" on "%s" with user "%s" ' % (opts.server, opts.port, opts.dbname, opts.user))
    cnx = Connection(
        server=opts.server,
        dbname=opts.dbname,
        login=opts.user,
        password=opts.passwd,
        port=opts.port)
except Exception, e:
    logger.error('Fail to connect to the server')
    logger.error('%s' % str(e))
    sys.exit(1)


resid = {}
opts.directory = os.path.expanduser(opts.directory)

# extract scenario
scenario_obj = Object(cnx, 'scanner.scenario')
model_obj = Object(cnx, 'ir.model')
warehouse_obj = Object(cnx, 'stock.warehouse')
scen_read = scenario_obj.read(int(opts.scenario_id), [], {'active_test': False})
if not scen_read:
    logger.error('Scenario ID %s not found' % opts.scenario_id)
    sys.exit(1)
del scen_read['step_ids']
del scen_read['id']
# create node and attributs
root = Element('scenario')
for field in scen_read:
    node = SubElement(root, field)
    if field == 'model_id':
        if scen_read[field]:
            node.text = model_obj.read(scen_read.get('model_id', [0])[0], ['model']).get('model')
    elif field == 'parent_id':
        if scen_read[field]:
            node.text = scenario_obj.read(scen_read.get('parent_id', [0])[0], ['reference_res_id']).get('reference_res_id')
    elif field in ['name', 'notes', 'title']:
        if scen_read[field]:
            node.text = unicode(scen_read[field])
    elif field == 'resid':
        if scen_read[field]:
            node.text = unicode(scen_read[field])
            resid['scenario'] = unicode(scen_read[field])
        else:
            resid['scenario'] = unicode(uuid.uuid1())
            node.text = resid['scenario']
            scenario_obj.write([int(opts.scenario_id)], {'resid': resid['scenario']})
    elif field == 'warehouse_ids':
        root.remove(node)
        for warehouse in warehouse_obj.read(scen_read[field], ['name']):
            node = SubElement(root, 'warehouse_ids')
            node.text = unicode(warehouse.get('name'))
    else:
        node.text = unicode(scen_read[field])
# add step
step_obj = Object(cnx, 'scanner.scenario.step')
step_ids = step_obj.search([('scenario_id', '=', int(opts.scenario_id))], 0, None, 'reference_res_id')
for step_id in step_ids:
    step = step_obj.read(step_id, [])
    # delete unuse key
    del step['in_transition_ids']
    del step['out_transition_ids']
    del step['id']
    del step['scenario_id']
    # get res_id
    if not step['reference_res_id']:
        step['reference_res_id'] = unicode(uuid.uuid1())
        step_obj.write([step_id], {'reference_res_id': step['reference_res_id']})
    resid[step_id] = unicode(step['reference_res_id'])
    # save code
    src_file = open('%s/%s.py' % (opts.directory, step['reference_res_id']), 'w')
    src_file.write(step['python_code'].encode('utf-8'))
    src_file.close()
    del step['python_code']
    # use unicode
    for key, item in step.items():
        step[key] = unicode(item)
    node = SubElement(root, 'Step', attrib=step)
# add transition
transition_obj = Object(cnx, 'scanner.scenario.transition')
transition_ids = transition_obj.search([('from_id.scenario_id', '=', int(opts.scenario_id))], 0, None, 'reference_res_id')
for transition_id in transition_ids:
    transition = transition_obj.read(transition_id, [])
    del transition['id']
    # get res id
    if not transition['reference_res_id']:
        transition['reference_res_id'] = unicode(uuid.uuid1())
        transition_obj.write([transition_id], {'reference_res_id': transition['reference_res_id']})
    # not write False in attribute tracer
    if not transition['tracer']:
        transition['tracer'] = ''
    # get res id for step
    transition['to_id'] = resid[transition['to_id'][0]]
    transition['from_id'] = resid[transition['from_id'][0]]
    # use unicode
    for key, item in transition.items():
        transition[key] = unicode(item)
    node = SubElement(root, 'Transition', attrib=transition)

xml_file = open('%s/scenario.xml' % opts.directory, 'w')
scenario_xml = tostring(root, encoding='UTF-8', xml_declaration=opts.header, pretty_print=opts.indent)
xml_file.write(scenario_xml)
xml_file.close()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
