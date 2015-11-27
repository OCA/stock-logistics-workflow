# -*- coding: utf-8 -*-
# © 2011 Christophe CHAUVET <christophe.chauvet@syleam.fr>
# © 2011 Jean-Sébastien SUZANNE <jean-sebastien.suzanne@syleam.fr>
# © 2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from oobjlib.connection import Connection
from oobjlib.component import Object
from oobjlib.common import GetParser
from optparse import OptionGroup
from lxml.etree import Element, SubElement
from lxml.etree import tostring
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
                 default=True,
                 help='Add XML and OpenObject Header')
group.add_option('', '--indent', dest='indent',
                 action='store_true',
                 default=True,
                 help='Indent the XML output')
group.add_option('', '--id', dest='scenario_id',
                 default=False,
                 help='id of the scenario to extract')
group.add_option('', '--name', dest='name',
                 default='',
                 help='Name of the scenario (default : last directory name)')
group.add_option('', '--directory', dest='directory',
                 default='.',
                 help='directory where the script will write the scenario '
                 'files')
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

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

try:
    logger.info('Open connection to "%s:%s" on "%s" with user "%s" ',
                opts.server, opts.port, opts.dbname, opts.user)
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


def normalize_name(name):
    """
    Replace all non alphanumeric characters by underscores
    """
    return re.sub(r'[^\w\d]', '_', name).lower()


resid = {}
opts.directory = os.path.expanduser(opts.directory)

# extract scenario
scenario_obj = Object(cnx, 'scanner.scenario')
model_obj = Object(cnx, 'ir.model')
warehouse_obj = Object(cnx, 'stock.warehouse')
user_obj = Object(cnx, 'res.users')
group_obj = Object(cnx, 'res.groups')
scen_read = scenario_obj.read(
    int(opts.scenario_id), [], {'active_test': False})
if not scen_read:
    logger.error('Scenario ID %s not found' % opts.scenario_id)
    sys.exit(1)
del scen_read['step_ids']

field_to_remove = ['create_uid', 'create_date',
                   'write_uid', 'write_date',
                   '__last_update', 'display_name']
for field in field_to_remove:
    del scen_read[field]

scenario_xml_id = scenario_obj.get_metadata(opts.scenario_id)[0]['xmlid']
if not scenario_xml_id:
    scenario_xml_id = 'scanner_scenario_%s' % (
        normalize_name(scen_read['name']),
    )
resid['scenario'] = scenario_xml_id

# create node and attributs
root = Element('scenario')
for field in scen_read:
    node = SubElement(root, field)
    if field == 'model_id':
        if scen_read[field]:
            node.text = model_obj.read(
                scen_read.get('model_id', [0])[0], ['model']).get('model')
    elif field == 'company_id':
        if scen_read[field]:
            node.text = scen_read.get('company_id', [0])[1]
    elif field == 'parent_id':
        if scen_read[field]:
            parent_id, parent_name = scen_read['parent_id']
            node.text = scenario_obj.get_metadata(parent_id)[0]['xmlid']
            if not node.text:
                node.text = 'scanner_scenario_%s' % normalize_name(
                    parent_name,
                )
    elif field in ['name', 'notes', 'title']:
        if scen_read[field]:
            node.text = unicode(scen_read[field])
    elif field == 'id':
        node.text = scenario_xml_id
    elif field == 'warehouse_ids':
        root.remove(node)
        for warehouse in warehouse_obj.read(scen_read[field], ['name']):
            node = SubElement(root, 'warehouse_ids')
            node.text = unicode(warehouse.get('name'))
    elif field == 'group_ids':
        root.remove(node)
        for group_id in scen_read[field]:
            group_xml_id = group_obj.get_metadata(group_id)[0]['xmlid']
            if group_xml_id:
                node = SubElement(root, 'group_ids')
                node.text = group_xml_id
    elif field == 'user_ids':
        root.remove(node)
        for user in user_obj.read(scen_read[field], ['login']):
            node = SubElement(root, 'user_ids')
            node.text = unicode(user.get('login'))
    else:
        node.text = unicode(scen_read[field])

# add step
step_obj = Object(cnx, 'scanner.scenario.step')
step_ids = step_obj.search([
    ('scenario_id', '=', int(opts.scenario_id)),
], 0, None, 'name')
for step_id in step_ids:
    step = step_obj.read(step_id, [])
    # delete unuse key
    del step['in_transition_ids']
    del step['out_transition_ids']
    del step['scenario_id']
    for field in field_to_remove:
        del step[field]

    # get res_id
    step_xml_id = step_obj.get_metadata(step_id)[0]['xmlid']
    if not step_xml_id:
        step_xml_id = 'scanner_scenario_step_%s_%s' % (
            normalize_name(scen_read['name']),
            normalize_name(step['name']),
        )
    step['id'] = step_xml_id

    resid[step_id] = step_xml_id

    # Do not add the scenario name on the python filename
    # if this step is defined in the same module as the scenario
    if '.' in scenario_xml_id and '.' in step_xml_id:
        scenario_module = scenario_xml_id.split('.')[0]
        step_module = step_xml_id.split('.')[0]
        if scenario_module == step_module:
            python_filename = step_xml_id.split('.')[1]

    # save code
    src_file = open('%s/%s.py' % (opts.directory, step_xml_id), 'w')
    src_file.write(step['python_code'].encode('utf-8'))
    src_file.close()
    del step['python_code']
    # use unicode
    for key, item in step.items():
        step[key] = unicode(item)
    node = SubElement(root, 'Step', attrib=step)

# add transition
transition_obj = Object(cnx, 'scanner.scenario.transition')
transition_ids = transition_obj.search([
    ('from_id.scenario_id', '=', int(opts.scenario_id)),
], 0, None, 'name')
for transition_id in transition_ids:
    transition = transition_obj.read(transition_id, [])
    del transition['scenario_id']
    for field in field_to_remove:
        del transition[field]

    # get res id
    transition_xml_id = transition_obj.get_metadata(transition_id)[0]['xmlid']
    transition['id'] = transition_xml_id
    if not transition_xml_id:
        transition['id'] = 'scanner_scenario_%s_%s' % (
            normalize_name(scen_read['name']),
            normalize_name(transition['name']),
        )

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

scenario_name = opts.name
if not scenario_name:
    scenario_name = os.path.split(opts.directory.strip('/'))[1]

xml_file = open('%s/%s.scenario' % (opts.directory, scenario_name), 'w')
scenario_xml = tostring(
    root, encoding='UTF-8', xml_declaration=opts.header,
    pretty_print=opts.indent)
xml_file.write(scenario_xml)
xml_file.close()
