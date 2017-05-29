# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, api


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.model
    def create(self, vals):
        """Set the owner based on the location.

        This is not a default method because we need to know the location.

        """
        if not vals.get('partner_id'):
            Company = self.env['res.company']
            location = self.env['stock.location'].browse(vals['location_id'])

            vals['partner_id'] = (
                location.partner_id.id or
                location.company_id.partner_id.id or
                Company._company_default_get().partner_id.id)

        return super(StockInventoryLine, self).create(vals)
