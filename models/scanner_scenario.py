# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with
#    simple scenarios
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.syleam.fr/>)
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

from openerp import models, api, fields, exceptions
from openerp import _

import logging
logger = logging.getLogger('stock_scanner')


class ScannerScenario(models.Model):
    _name = 'scanner.scenario'
    _description = 'Scenario for scanner'

    _order = 'sequence'

    _parent_name = 'parent_id'

    @api.model
    def _type_get(self):
        return [
            ('scenario', 'Scenario'),
            ('menu', 'Menu'),
            ('shortcut', 'Shortcut'),
        ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        size=64,
        required=True,
        translate=True,
        help='Appear on barcode reader screen')
    sequence = fields.Integer(
        string='Sequence',
        default=0,
        required=False,
        help="Sequence order")
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If check, this object is always available')
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=False,
        ondelete='restrict',
        help='Model used for this scenario')
    step_ids = fields.One2many(
        comodel_name='scanner.scenario.step',
        inverse_name='scenario_id',
        string='Scenario',
        ondelete='cascade',
        help='Step of the current running scenario')
    warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        relation='scanner_scenario_warehouse_rel',
        column1='scenario_id',
        column2='warehouse_id',
        string='Warehouses',
        help='Warehouses for this scenario')
    notes = fields.Text(
        string='Notes',
        help='Store different notes, date and title for modification, etc...')
    shared_custom = fields.Boolean(
        string='Shared Custom',
        default=False,
        help='Allows to share the custom values with a shared scanner in the '
             'same warehouse')
    parent_id = fields.Many2one(
        comodel_name='scanner.scenario',
        string='Parent',
        required=False,
        ondelete='restrict',
        help='Parent scenario, used to create menus')
    type = fields.Selection(
        selection='_type_get',
        string='Type',
        required=True,
        default='scenario',
        help='Defines if this scenario is a menu or an executable scenario')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id.id,
        ondelete='restrict',
        help='Company to be used on this scenario')
    group_ids = fields.Many2many(
        comodel_name='res.groups',
        relation='scanner_scenario_res_groups_rel',
        column1='scenario_id',
        column2='group_id',
        string='Allowed Groups',
        default=lambda self: [self.env.ref('stock.group_stock_user').id])
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='scanner_scenario_res_users_rel',
        column1='scenario_id',
        column2='user_id',
        string='Allowed Users')

    @api.one
    @api.constrains('parent_id')
    def _check_recursion(self):
        if not super(ScannerScenario, self)._check_recursion():
            raise exceptions.Warning(
                _('Error ! You can not create recursive scenarios.'),
            )
