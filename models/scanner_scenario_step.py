# -*- coding: utf-8 -*-
# © 2011 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import sys
import compiler
import traceback
from openerp import models, api, fields, exceptions
from openerp import _

from .common import PYTHON_CODE_DEFAULT

import logging
logger = logging.getLogger('stock_scanner')


class ScannerScenarioStep(models.Model):
    _name = 'scanner.scenario.step'
    _description = 'Step for scenario'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        required=False,
        help='Name of the step.')
    scenario_id = fields.Many2one(
        comodel_name='scanner.scenario',
        string='Scenario',
        required=True,
        ondelete='cascade',
        help='Scenario for this step.')
    step_start = fields.Boolean(
        string='Step start',
        default=False,
        help='Check this if this is the first step of the scenario.')
    step_stop = fields.Boolean(
        string='Step stop',
        default=False,
        help='Check this if this is the  last step of the scenario.')
    step_back = fields.Boolean(
        string='Step back',
        default=False,
        help='Check this to stop at this step when returning back.')
    no_back = fields.Boolean(
        string='No back',
        default=False,
        help='Check this to prevent returning back this step.')
    out_transition_ids = fields.One2many(
        comodel_name='scanner.scenario.transition',
        inverse_name='from_id',
        string='Outgoing transitions',
        ondelete='cascade',
        help='Transitions which goes to this step.')
    in_transition_ids = fields.One2many(
        comodel_name='scanner.scenario.transition',
        inverse_name='to_id',
        string='Incoming transitions',
        ondelete='cascade',
        help='Transitions which goes to the next step.')
    python_code = fields.Text(
        string='Python code',
        default=PYTHON_CODE_DEFAULT,
        help='Python code to execute.')

    @api.multi
    @api.constrains('python_code')
    def _check_python_code_syntax(self):
        """
        Syntax check the python code of a step
        """
        for step in self:
            try:
                compiler.parse(step.python_code)
            except SyntaxError, exception:
                logger.error(''.join(traceback.format_exception(
                    sys.exc_type,
                    sys.exc_value,
                    sys.exc_traceback,
                )))
                raise exceptions.ValidationError(
                    _('Error in python code for step "%s"'
                      ' at line %d, offset %d:\n%s') % (
                          step.name,
                          exception.lineno,
                          exception.offset,
                          exception.msg,
                    ))

        return True
