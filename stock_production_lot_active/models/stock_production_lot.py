# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    def write(self, vals):
        error = ""
        for record in self:
            if record.active and record.product_qty and not vals.get("active"):
                error += _("This product has stock: %s \n", record.product_id.name)
            else:
                return super(StockProductionLot, self).write(vals)
        if error:
            raise UserError(error)

    active = fields.Boolean(default=True)

    @api.constrains("name", "product_id", "company_id")
    def _check_unique_lot(self):
        """Check that there is no other lot with the same name, company and product

        To avoid allowing duplicate lot/company/name combinations when there is
        another inactive entry we have to set the active_test flag to False.
        """
        return super(
            StockProductionLot, self.with_context(active_test=False)
        )._check_unique_lot()
