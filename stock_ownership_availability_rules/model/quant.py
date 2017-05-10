# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from odoo import models, api, fields


class Quant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self, vals):
        """Set the owner based on the location.

        This is not a default method because we need to know the location.

        """
        if not vals.get('owner_id'):
            Company = self.env['res.company']
            location = self.env['stock.location'].browse(vals['location_id'])

            vals['owner_id'] = (
                location.partner_id.id or
                location.company_id.partner_id.id or
                Company._company_default_get('stock.quant').partner_id.id)

        return super(Quant, self).create(vals)

    owner_id = fields.Many2one('res.partner', 'Owner',
                               help="This is the owner of the quant",
                               readonly=True,
                               index=True,
                               required=True)

    @api.model
    def _quants_get_reservation_domain(self, move, pack_operation_id=False,
                                       lot_id=False, company_id=False,
                                       initial_domain=None):
        domain = super(Quant, self)._quants_get_reservation_domain(
            move, pack_operation_id=pack_operation_id, lot_id=lot_id,
            company_id=company_id, initial_domain=initial_domain)
        pack_operation = self.env['stock.pack.operation'].browse(
            pack_operation_id)
        if not pack_operation or not pack_operation.owner_id:
            if not move.restrict_partner_id:
                restrict_partner_id = (
                    move.location_id.partner_id.id or
                    move.location_id.company_id.partner_id.id)
                domain += [('owner_id', '=', restrict_partner_id)]
        return domain
