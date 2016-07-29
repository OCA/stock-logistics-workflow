# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.model
    def _prepare_inventory_line(self, inventory_id, data):
        line_data = super(StockChangeProductQty,
                          self)._prepare_inventory_line(inventory_id, data)
        Company = self.env['res.company']
        location = data.location_id
        line_data['partner_id'] = (
            location.partner_id.id or
            location.company_id.partner_id.id or
            Company.browse(
                Company._company_default_get('stock.quant')
            ).partner_id.id
        )

        return line_data

