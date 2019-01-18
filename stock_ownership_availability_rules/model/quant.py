# -*- coding: utf-8 -*-
# Copyright 2014 ALeonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class Quant(models.Model):
    _inherit = 'stock.quant'

    owner_id = fields.Many2one('res.partner', 'Owner',
                               help="This is the owner of the quant",
                               readonly=True,
                               index=True,
                               required=True)

    @api.model
    def create(self, vals):
        """Set the owner based on the location.

        This is not a default method because we need to know the location.

        """
        if not vals.get('owner_id'):
            Company = self.env['res.company']
            location = self.env['stock.location'].browse(vals['location_id'])
            vals_company = Company.browse(vals.get('company_id', False))
            vals['owner_id'] = (
                location.partner_id.id or
                location.company_id.partner_id.id or
                vals_company.partner_id.id or  # Default value
                Company._company_default_get('stock.quant').partner_id.id)

        return super(Quant, self).create(vals)

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
                    move.location_id.company_id.partner_id.id or
                    move.company_id.partner_id.id)
                domain += [('owner_id', '=', restrict_partner_id)]
        return domain
