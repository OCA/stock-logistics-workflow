# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    @api.constrains("product_qty", "qty_done")
    def _check_qty_done(self):
        for rec in self.filtered("picking_id.picking_type_id.qty_done_constraint"):
            if not rec.qty_done:
                continue
            if (
                float_compare(
                    rec.product_qty,
                    rec.qty_done,
                    precision_rounding=rec.product_uom_id.rounding,
                )
                < 0
            ):
                raise ValidationError(
                    _(
                        "You cannot fill in more in the 'Done'"
                        "column than in 'Reserved' one for line %s"
                        % rec.product_id.name
                    )
                )
