# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with
#       simple scenarios
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

from openerp import models, fields


class ScannerHardwareStepHistory(models.Model):
    _name = 'scanner.hardware.step.history'
    _description = 'Steps History of Scanner Hardware'
    _order = 'id'

    hardware_id = fields.Many2one(
        comodel_name='scanner.hardware', string='Hardware',
        required=True, help='Hardware linked to this history line')
    step_id = fields.Many2one(
        comodel_name='scanner.scenario.step', string='Step',
        help='Step executed during this history line')
    message = fields.Char(
        string='Message',
        help='Message sent during execution of the step')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
