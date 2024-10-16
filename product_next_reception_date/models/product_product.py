# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    date_next_reception = fields.Date(compute="_compute_date_next_reception", compute_sudo=True)
    
    def _compute_date_next_reception(self):
        for record in self:
            picking_model = self.env["stock.picking"]
            picking_id = picking_model.search(
                [
                    ("product_id", "=", record.id),
                    ("picking_type_id.code", "=", "incoming"),
                    ("state", "in", ["ready", "waiting", "assigned"]),
                ],
                limit=1,
            )
            record.date_next_reception = picking_id.scheduled_date if picking_id else False