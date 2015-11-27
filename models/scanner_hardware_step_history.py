# -*- coding: utf-8 -*-
# © 2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ScannerHardwareStepHistory(models.Model):
    _name = 'scanner.hardware.step.history'
    _description = 'Steps History of Scanner Hardware'
    _order = 'id'

    hardware_id = fields.Many2one(
        comodel_name='scanner.hardware', string='Hardware',
        required=True, help='Hardware linked to this history line.')
    step_id = fields.Many2one(
        comodel_name='scanner.scenario.step', string='Step',
        help='Step executed during this history line.')
    transition_id = fields.Many2one(
        comodel_name='scanner.scenario.transition', string='Transition',
        help='Transition executed during this history line.')
    message = fields.Char(
        string='Message',
        help='Message sent during execution of the step.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
