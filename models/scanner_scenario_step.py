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
        help='Name of the step')
    scenario_id = fields.Many2one(
        comodel_name='scanner.scenario',
        string='Scenario',
        required=True,
        ondelete='cascade',
        help='Scenario for this step')
    step_start = fields.Boolean(
        string='Step start',
        default=False,
        help='Check this if this is the first step of the scenario')
    step_stop = fields.Boolean(
        string='Step stop',
        default=False,
        help='Check this if this is the  last step of the scenario')
    step_back = fields.Boolean(
        string='Step back',
        default=False,
        help='Check this to stop at this step when returning back')
    no_back = fields.Boolean(
        string='No back',
        default=False,
        help='Check this to prevent returning back this step')
    out_transition_ids = fields.One2many(
        comodel_name='scanner.scenario.transition',
        inverse_name='from_id',
        string='Outgoing transitions',
        ondelete='cascade',
        help='Transitions which goes to this step')
    in_transition_ids = fields.One2many(
        comodel_name='scanner.scenario.transition',
        inverse_name='to_id',
        string='Incoming transitions',
        ondelete='cascade',
        help='Transitions which goes to the next step')
    python_code = fields.Text(
        string='Python code',
        default=PYTHON_CODE_DEFAULT,
        help='Python code to execute')

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
