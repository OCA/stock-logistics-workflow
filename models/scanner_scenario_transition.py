# -*- coding: utf-8 -*-
# © 2011 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys
import compiler
import traceback
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
        help='Name of the transition.')
    sequence = fields.Integer(
        string='Sequence',
        default=0,
        required=False,
        help='Sequence order.')
    from_id = fields.Many2one(
        comodel_name='scanner.scenario.step',
        string='From',
        required=True,
        ondelete='cascade',
        help='Step which launches this transition.')
    to_id = fields.Many2one(
        comodel_name='scanner.scenario.step',
        string='To',
        required=True,
        ondelete='cascade',
        help='Step which is reached by this transition.')
    condition = fields.Char(
        string='Condition',
        required=True,
        default='True',
        help='The transition is followed only if this condition is evaluated '
             'as True.')
    transition_type = fields.Selection(
        selection='_transition_type_get',
        string='Transition Type',
        default="keyboard",
        help='Type of transition.')
    tracer = fields.Char(
        string='Tracer',
        required=False,
        default=False,
        help='Used to determine fron which transition we arrive to the '
             'destination step.')
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

    @api.multi
    @api.constrains('condition')
    def _check_condition_syntax(self):
        """
        Syntax check the python condition of a transition
        """
        for transition in self:
            try:
                compiler.parse(transition.condition)
            except SyntaxError, exception:
                logger.error(''.join(traceback.format_exception(
                    sys.exc_type,
                    sys.exc_value,
                    sys.exc_traceback,
                )))
                raise exceptions.ValidationError(
                    _('Error in condition for transition "%s"'
                      ' at line %d, offset %d:\n%s') % (
                        transition.name,
                        exception.lineno,
                        exception.offset,
                        exception.msg,
                    ))

        return True
