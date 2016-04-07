# -*- coding: utf-8 -*-
# © 2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from lxml.etree import parse
from StringIO import StringIO

import openerp
from openerp import exceptions
from openerp.tools import misc
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
from openerp.tools.convert import convert_file
import logging
logger = logging.getLogger('init:stock_scanner')


def get_xml_id(element, module, values):
    """
    Returns the XML ID of an element from its values
    """
    xml_id = values.get('id')
    if not xml_id:
        xml_id = values.get('reference_res_id')
    if not xml_id:
        raise exceptions.Warning(
            _('The id of a %s cannot be empty!') % element
        )

    if '.' not in xml_id:
        xml_id = '%s.%s' % (
            module,
            xml_id,
        )

    return xml_id


def import_scenario(env, module, scenario_xml, mode, directory, filename):
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
    noupdate = root.get('noupdate', False)

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
            else:
                scenario_values['group_ids'].append(
                    (4, env.ref(node.text).id),
                )
        elif node.tag == 'user_ids':
            if 'user_ids' not in scenario_values:
                scenario_values['user_ids'] = []
                user_ids = user_obj.search([
                    ('login', '=', node.text),
                ])
                if user_ids:
                    scenario_values['user_ids'].append((4, user_ids[0].id))
        elif node.tag in ('active', 'shared_custom'):
            scenario_values[node.tag] = safe_eval(node.text) or False
        else:
            scenario_values[node.tag] = node.text or False

    # Transition from old format to new format
    scenario_xml_id = get_xml_id(_('scenario'), module, scenario_values)

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

    if scenario_values.get('parent_id'):
        if '.' not in scenario_values['parent_id']:
            scenario_values['parent_id'] = '%s.%s' % (
                module,
                scenario_values['parent_id']
            )
        scenario_values['parent_id'] = env.ref(scenario_values['parent_id']).id
        if not scenario_values['parent_id']:
            logger.error('Parent not found')
            return

    # Create or update the scenario
    ir_model_data_obj._update(
        'scanner.scenario',
        module,
        scenario_values,
        xml_id=scenario_xml_id,
        mode=mode,
        noupdate=noupdate,
    )
    scenario = env.ref(scenario_xml_id)

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

        # Transition from old to new format
        step_xml_id = get_xml_id(_('step'), module, step_values)

        # Get python source
        python_filename = '%s/%s.py' % (
            directory,
            step_xml_id,
        )
        # Alow to use the id without module name for the current module
        try:
            python_file = misc.file_open(python_filename)
        except IOError:
            if module == step_xml_id.split('.')[0]:
                python_filename = '%s/%s.py' % (
                    directory,
                    step_xml_id.split('.')[1],
                )
                python_file = misc.file_open(python_filename)

        # Load python code and check syntax
        try:
            step_values['python_code'] = python_file.read()

        finally:
            python_file.close()

        # Create or update
        ir_model_data_obj._update(
            'scanner.scenario.step',
            module,
            step_values,
            xml_id=step_xml_id,
            mode=mode,
            noupdate=noupdate,
        )
        step = env.ref(step_xml_id)
        resid[step_xml_id] = step.id

    # Create or update transitions
    for node in transitions:
        transition_values = {}
        for key, item in node.items():
            if key in ['to_id', 'from_id']:
                item = resid[get_xml_id(_('step'), module, {'id': item})]

            transition_values[key] = item

        # Create or update
        ir_model_data_obj._update(
            'scanner.scenario.transition',
            module,
            transition_values,
            xml_id=get_xml_id(_('transition'), module, transition_values),
            mode=mode,
            noupdate=noupdate,
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
