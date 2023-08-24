from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("qty_done")
    def check_negative_qty(self):
        if self.env.company.prevent_negative_quantity_on != "move_line":
            return

        precision = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for move_line in self:
            quant = self.env['stock.quant']._gather(
                move_line.product_id,
                move_line.location_id,
                lot_id=move_line.lot_id,
                package_id=move_line.package_id,
                owner_id=move_line.owner_id,
                strict=True
            )

            if (
                float_compare(quant.quantity - move_line.qty_done, 0, precision_digits=precision) == -1
                and move_line.product_id.type == "product"
                and move_line.location_id.usage in ["internal", "transit"]
                and not (
                    move_line.product_id.allow_negative_stock
                    or move_line.product_id.categ_id.allow_negative_stock
                ) and not move_line.location_id.allow_negative_stock
            ):
                msg_add = ""
                if quant.lot_id:
                    msg_add = _(" lot '%s'") % quant.lot_id.name_get()[0][1]
                raise ValidationError(_(
                    "You cannot validate this stock operation because the "
                    "stock level of the product '%(name)s'%(name_lot)s would "
                    "become negative "
                    "(%(q_quantity)s) on the stock location '%(complete_name)s' "
                    "and negative stock is "
                    "not allowed for this product and/or location."
                ) % {
                    "name": move_line.product_id.display_name,
                    "name_lot": msg_add,
                    "q_quantity": float_round(quant.quantity - move_line.qty_done, precision_digits=precision),
                    "complete_name": move_line.location_id.complete_name,
                })
