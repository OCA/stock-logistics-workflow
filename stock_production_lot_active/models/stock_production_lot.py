# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    active = fields.Boolean(default=True)

    @api.constrains("name", "product_id", "company_id")
    def _check_unique_lot(self):
        """Check that there is no other lot with the same name, company and product

        To avoid allowing duplicate lot/company/name combinations when there is
        another inactive entry we have to set the active_test flag to False.
        """
        return super(StockLot, self.with_context(active_test=False))._check_unique_lot()
