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
from lxml.etree import parse
from StringIO import StringIO

from glob import glob
import traceback
import compiler
import logging
import sys
import os

parser = GetParser('Export scenario', '0.1')
group = OptionGroup(parser, "Object arguments",
                    "Application Options")
group.add_option('', '--directory', dest='directory',
                 default='.',
                 help='directory where the script will search for the scenario files (default \'.\')')
group.add_option('-r', '--recursive', dest='recursive',
                 action='store_true',
                 default=False,
                 help='Recursively imports scenarios from the supplied directory')
group.add_option('-v', '--verbose', dest='verbose',
                 action='store_true',
                 default=False,
                 help='Add verbose mode')
parser.add_option_group(group)
opts, args = parser.parse_args()

logger = logging.getLogger("import_scenario")
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

directories = []
opts.directory = os.path.expanduser(opts.directory)
if glob(opts.directory + '/scenario.xml'):
    directories.append(opts.directory)
if opts.recursive:
    for root, dirs, files in os.walk(opts.directory):
        for directory in dirs:
            if glob('%s/%s/scenario.xml' % (root, directory)):
                directories.append('%s/%s' % (root, directory))

for directory in directories:
    logger.info('Importing from : %s' % directory)

    # extract scenario
    scenario_obj = Object(cnx, 'scanner.scenario')
    model_obj = Object(cnx, 'ir.model')
    company_obj = Object(cnx, 'res.company')
    warehouse_obj = Object(cnx, 'stock.warehouse')
    step_obj = Object(cnx, 'scanner.scenario.step')
    trans_obj = Object(cnx, 'scanner.scenario.transition')
    xml_file = open('%s/scenario.xml' % directory, 'r')
    logger.info('Scenario file found, process reading!')
    scenario_xml = xml_file.read()
    xml_file.close()
    xml_doc = StringIO(scenario_xml)
    root = parse(xml_doc).getroot()

    step = []
    transition = []
    scen_vals = {}

    # parse of the scenario
    steps_number = 0
    transitions_number = 0
    for node in root.getchildren():
        # the node of the Step and Transition are put in other list
        if node.tag == 'Step':
            steps_number += 1
            step.append(node)
        elif node.tag == 'Transition':
            transitions_number += 1
            transition.append(node)
        elif node.tag == 'warehouse_ids':
            if 'warehouse_ids' not in scen_vals:
                scen_vals['warehouse_ids'] = []
            warehouse_ids = warehouse_obj.search([('name', '=', node.text)], 0, None, None, {'active_test': False})
            if warehouse_ids:
                scen_vals['warehouse_ids'].append((4, warehouse_ids[0]))
        elif node.tag in ('active', 'shared_custom'):
            scen_vals[node.tag] = eval(node.text) or False
        else:
            scen_vals[node.tag] = node.text or False
    logger.info('%d steps found' % steps_number)
    logger.info('%d transitions found' % transitions_number)

    if scen_vals['model_id']:
        logger.info('Search model: %s' % scen_vals['model_id'])
        scen_vals['model_id'] = model_obj.search([('model', '=', scen_vals['model_id'])], 0, None, None, {'active_test': False}) or False
        if scen_vals['model_id']:
            logger.info('Model found')
            scen_vals['model_id'] = scen_vals['model_id'][0]
        else:
            logger.error('Model not found')
            sys.exit(1)

    if scen_vals.get('company_id'):
        logger.info('Search company: %s' % scen_vals['company_id'])
        scen_vals['company_id'] = company_obj.search([('name', '=', scen_vals['company_id'])], 0, None, None, {'active_test': False}) or False
        if scen_vals['company_id']:
            logger.info('Company found')
            scen_vals['company_id'] = scen_vals['company_id'][0]
        else:
            logger.error('Company not found')
            sys.exit(1)

    if 'parent_id' in scen_vals and scen_vals['parent_id']:
        logger.info('Search parent: %s' % scen_vals['parent_id'])
        scen_vals['parent_id'] = scenario_obj.search([('reference_res_id', '=', scen_vals['parent_id'])], 0, None, None, {'active_test': False}) or False
        if scen_vals['parent_id']:
            logger.info('Parent found')
            scen_vals['parent_id'] = scen_vals['parent_id'][0]
        else:
            logger.error('Parent not found')
            sys.exit(1)

    # create or update
    scenario_ids = scenario_obj.search([('reference_res_id', '=', scen_vals['reference_res_id'])], 0, None, None, {'active_test': False})
    if scenario_ids:
        logger.info('Scenario exists, update it')
        del scen_vals['reference_res_id']
        scenario_obj.write(scenario_ids, scen_vals)
        scenario_id = scenario_ids[0]
    else:
        logger.info('Scenario not exists, create it')
        scenario_id = scenario_obj.create(scen_vals)

    # List scenario steps and transitions, to be able to remove deleted data
    scenario_data = scenario_obj.read(scenario_id, ['step_ids'])
    all_step_ids = set(scenario_data['step_ids'])
    step_data = step_obj.read(list(all_step_ids), ['in_transition_ids', 'out_transition_ids'])
    all_transition_ids = set(sum([data['in_transition_ids'] + data['out_transition_ids'] for data in step_data], []))

    # parse step
    logger.info('Update steps')
    resid = {}
    for node in step:
        step_vals = {}
        for key, item in node.items():
            if item == 'False':
                item = False
            step_vals[key] = item
        # get scenario id
        step_vals['scenario_id'] = scenario_id
        # get python src
        filename = '%s/%s.py' % (directory, step_vals['reference_res_id'])
        try:
            compiler.compileFile(filename)
        except Exception, e:
            print 'Compile error in file %s :' % filename
            print ''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        python_code = open(filename, 'r')
        step_vals['python_code'] = python_code.read()
        python_code.close()
        # create or update
        step_ids = step_obj.search([('reference_res_id', '=', step_vals['reference_res_id'])], 0, None, None, {'active_test': False})
        if step_ids:
            resid[step_vals['reference_res_id']] = step_ids[0]
            all_step_ids -= set(step_ids)
            del step_vals['reference_res_id']
            step_obj.write(step_ids, step_vals)
        else:
            resid[step_vals['reference_res_id']] = step_obj.create(step_vals)

    # parse transition
    logger.info('Update transitions')
    for node in transition:
        trans_vals = {}
        for key, item in node.items():
            if key in ['to_id', 'from_id']:
                item = resid[item]
            trans_vals[key] = item
        # create or update
        trans_ids = trans_obj.search([('reference_res_id', '=', trans_vals['reference_res_id'])], 0, None, None, {'active_test': False})
        if trans_ids:
            all_transition_ids -= set(trans_ids)
            del trans_vals['reference_res_id']
            trans_obj.write(trans_ids, trans_vals)
        else:
            trans_obj.create(trans_vals)

    # Remove deleted steps and transitions
    logger.info('Delete old steps and transitions')
    step_obj.unlink(list(all_step_ids))
    trans_obj.unlink(list(all_transition_ids))

logger.info('Import scenario done!')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
