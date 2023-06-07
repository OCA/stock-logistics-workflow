# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    @api.depends("quant_ids")
    def _compute_has_stock(self):
        for record in self:
            if record.quant_ids:
                record.has_stock = True
            else:
                record.has_stock = False

    active = fields.Boolean(default=True)
    has_stock = fields.Boolean(
        string="Has stock",
        compute="_compute_has_stock",
        store=True
    )

    @api.constrains("name", "product_id", "company_id")
    def _check_unique_lot(self):
        """Check that there is no other lot with the same name, company and product

        To avoid allowing duplicate lot/company/name combinations when there is
        another inactive entry we have to set the active_test flag to False.
        """
        return super(
            StockProductionLot, self.with_context(active_test=False)
        )._check_unique_lot()
