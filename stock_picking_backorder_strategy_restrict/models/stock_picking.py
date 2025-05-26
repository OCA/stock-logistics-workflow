from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_backorder(self):
        """Prevent backorder creation if picking type is set to restrict."""
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")

        # Filter pickings that explicitly restrict backorder creation
        restrict_bo_pickings = self.filtered(
            lambda p: p.picking_type_id.create_backorder == "restrict"
        )
        for picking in restrict_bo_pickings:
            if any(
                (move.product_uom_qty and not move.picked)
                or float_compare(
                    move._get_picked_quantity(),
                    move.product_uom_qty,
                    precision_digits=prec,
                )
                < 0
                for move in picking.move_ids
                if move.state != "cancel"
            ):
                # Raise an error if any required move is not completely picked
                raise ValidationError(
                    _("Creation of the backorder is not allowed for this picking type.")
                )
        return super()._check_backorder()
