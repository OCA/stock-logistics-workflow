# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    use_manual_lots = fields.Boolean(
        related="picking_id.use_manual_lots",
    )

    manual_production_lot_id = fields.Many2one(
        "stock.production.lot",
        "Lot/Serial Number (manual)",
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]",
        check_company=True,
        copy=False,
        help="This field is used to manually select a production lot.",
    )

    @api.onchange("manual_production_lot_id")
    def onchange_manual_production_lot_id(self):
        if self.manual_production_lot_id:
            self.lot_id = self.manual_production_lot_id

    def _action_done(self):
        lines_to_block = self.filtered(
            lambda line: line.use_manual_lots
            and not line.manual_production_lot_id
            and line.product_id.tracking != "none"
            and line.qty_done > 0
        )
        if lines_to_block:
            raise UserError(
                _("You need to manually supply a Lot/Serial Number for product: \n - ")
                + "\n - ".join(lines_to_block.mapped("product_id.display_name"))
            )
        return super()._action_done()
