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


class ScannerScenarioTransition(models.Model):
    _name = 'scanner.scenario.transition'
    _description = 'Transition for scenario'

    _order = 'sequence'

    @api.model
    def _transition_type_get(self):
        return [
            ('scanner', 'Scanner'),
            ('keyboard', 'Keyboard'),
        ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the transition')
    sequence = fields.Integer(
        string='Sequence',
        default=0,
        required=False,
        help='Sequence order')
    from_id = fields.Many2one(
        comodel_name='scanner.scenario.step',
        string='From',
        required=True,
        ondelete='cascade',
        help='Step which launches this transition')
    to_id = fields.Many2one(
        comodel_name='scanner.scenario.step',
        string='To',
        required=True,
        ondelete='cascade',
        help='Step which is reached by this transition')
    condition = fields.Char(
        string='Condition',
        required=True,
        default='True',
        help='The transition is followed only if this condition is evaluated '
             'as True')
    transition_type = fields.Selection(
        selection='_transition_type_get',
        string='Transition Type',
        default="scanner",
        help='Type of transition')
    tracer = fields.Char(
        string='Tracer',
        required=False,
        default=False,
        help='Used to determine fron which transition we arrive to the '
             'destination step')
    scenario_id = fields.Many2one(
        comodel_name='scanner.scenario',
        string='Scenario',
        required=False,
        related="from_id.scenario_id",
        store=True,
        ondelete='cascade',
        readonly=True)

    @api.one
    @api.constrains('from_id', 'to_id')
    def _check_scenario(self):
        if self.from_id.scenario_id.id != self.to_id.scenario_id.id:
            raise exceptions.Warning(
                _('Error ! You can not create recursive scenarios.'),
            )

        return True
