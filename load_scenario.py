# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with
#    simple scenarios
#    Copyright (C) 2015 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of stock_scanner
#
#    stock_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

import compiler
import os
import sys
import traceback
from lxml.etree import parse
from StringIO import StringIO

import openerp
from openerp.tools import misc
from openerp.tools.convert import convert_file
import logging
logger = logging.getLogger('init:stock_scanner')


def import_scenario(env, module, scenario_xml, mode, directory, filename):
    scenario_obj = env['scanner.scenario']
    model_obj = env['ir.model']
    company_obj = env['res.company']
    warehouse_obj = env['stock.warehouse']
    user_obj = env['res.users']
    group_obj = env['res.groups']
    ir_model_data_obj = env['ir.model.data']

    xml_doc = StringIO(scenario_xml)
    root = parse(xml_doc).getroot()

    steps = []
    transitions = []
    scenario_values = {}

    # parse of the scenario
    for node in root.getchildren():
        # the node of the Step and Transition are put in other list
        if node.tag == 'Step':
            steps.append(node)
        elif node.tag == 'Transition':
            transitions.append(node)
        elif node.tag == 'warehouse_ids':
            if 'warehouse_ids' not in scenario_values:
                scenario_values['warehouse_ids'] = []
            warehouse_ids = warehouse_obj.search([('name', '=', node.text)])
            if warehouse_ids:
                scenario_values['warehouse_ids'].append(
                    (4, warehouse_ids[0].id))
        elif node.tag == 'group_ids':
            if 'group_ids' not in scenario_values:
                scenario_values['group_ids'] = []
                group_ids = group_obj.search([
                    ('full_name', '=', node.text),
                ])
                if group_ids:
                    scenario_values['group_ids'].append((4, group_ids[0].id))
        elif node.tag == 'user_ids':
            if 'user_ids' not in scenario_values:
                scenario_values['user_ids'] = []
                user_ids = user_obj.search([
                    ('login', '=', node.text),
                ])
                if user_ids:
                    scenario_values['user_ids'].append((4, user_ids[0].id))
        elif node.tag in ('active', 'shared_custom'):
            scenario_values[node.tag] = eval(node.text) or False
        else:
            scenario_values[node.tag] = node.text or False

    if scenario_values['model_id']:
        scenario_values['model_id'] = model_obj.search([
            ('model', '=', scenario_values['model_id']),
        ]).id or False
        if not scenario_values['model_id']:
            logger.error('Model not found')
            return

    if scenario_values.get('company_id'):
        scenario_values['company_id'] = company_obj.search([
            ('name', '=', scenario_values['company_id']),
        ]).id or False
        if not scenario_values['company_id']:
            logger.error('Company not found')
            return

    if 'parent_id' in scenario_values and scenario_values['parent_id']:
        scenario_values['parent_id'] = scenario_obj.search([
            ('reference_res_id', '=', scenario_values['parent_id']),
        ]).id or False
        if not scenario_values['parent_id']:
            logger.error('Parent not found')
            return

    # Create or update the scenario
    ir_model_data_obj._update(
        'scanner.scenario',
        module,
        scenario_values,
        xml_id=scenario_values['reference_res_id'],
        mode=mode,
    )
    scenario = env.ref('%s.%s' % (module, scenario_values['reference_res_id']))

    # Create or update steps
    resid = {}
    for node in steps:
        step_values = {}
        for key, item in node.items():
            if item == 'False':
                item = False
            step_values[key] = item

        # Get scenario id
        step_values['scenario_id'] = scenario.id

        # Get python source
        python_filename = '%s/%s.py' % (
            directory,
            step_values['reference_res_id'],
        )
        python_file = misc.file_open(python_filename)
        try:
            step_values['python_code'] = python_file.read()

            # Syntax check the python code
            try:
                compiler.parse(step_values['python_code'])
            except Exception:
                logger.error('Compile error in file %s :' % python_filename)
                logger.error(''.join(traceback.format_exception(
                    sys.exc_type,
                    sys.exc_value,
                    sys.exc_traceback,
                )))

        finally:
            python_file.close()

        # Create or update
        ir_model_data_obj._update(
            'scanner.scenario.step',
            module,
            step_values,
            xml_id=step_values['reference_res_id'],
            mode=mode,
        )
        step = env.ref('%s.%s' % (module, step_values['reference_res_id']))
        resid[step_values['reference_res_id']] = step.id

    # Create or update transitions
    for node in transitions:
        transition_values = {}
        for key, item in node.items():
            if key in ['to_id', 'from_id']:
                item = resid[item]

            transition_values[key] = item

        # Create or update
        ir_model_data_obj._update(
            'scanner.scenario.transition',
            module,
            transition_values,
            xml_id=transition_values['reference_res_id'],
            mode=mode,
        )


def scenario_convert_file(cr, module, filename, idref,
                          mode='update', noupdate=False,
                          kind=None, report=None, pathname=None):
    if pathname is None:
        pathname = os.path.join(module, filename)

    directory, filename = os.path.split(pathname)
    extension = os.path.splitext(filename)[1].lower()
    if extension == '.scenario':
        fp = misc.file_open(pathname)
        try:
            with openerp.api.Environment.manage():
                uid = openerp.SUPERUSER_ID
                env = openerp.api.Environment(cr, uid, {'active_test': False})

                import_scenario(env, module, fp.read(),
                                mode, directory, filename)
        finally:
            fp.close()
    else:
        convert_file(cr, module, filename, idref,
                     mode=mode, noupdate=noupdate,
                     kind=kind, report=report, pathname=pathname)

# Monkey patch Odoo's module file loading
# To be able to load scenarios from manifest file
openerp.tools.convert_file = scenario_convert_file
openerp.tools.convert.convert_file = scenario_convert_file

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
