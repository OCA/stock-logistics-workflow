# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS
from odoo.tools import float_compare, float_is_zero


class StockPicking(models.Model):

    _inherit = "stock.picking"

    is_completed = fields.Boolean(
        compute="_compute_is_completed",
        search="_search_is_completed",
        help="This field means if all picking operations have been done (each quantity is > 0)",
    )

    @api.depends(
        "state",
        "move_ids_without_package.quantity_done",
        "move_line_ids.qty_done",
        "move_ids.quantity_done",
    )
    def _compute_is_completed(self):
        """
        We must implement several fields value retrieval to allow a good behaviour on
        form side as several fields can be filled in:
          - move_line_ids.qty_done
          - move_ids_without_package
        """
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        # We must use recordset (and not ids) as web interface can trigger this
        # and record arrives here with NewId
        ready_pickings = self.browse()
        for picking in self.filtered(lambda picking: picking.state == "assigned"):
            if all(
                not float_is_zero(move_line.qty_done, precision_digits=precision_digits)
                and float_compare(
                    move_line.qty_done,
                    move_line.reserved_uom_qty,
                    precision_digits=precision_digits,
                )
                >= 0
                for move_line in picking.move_line_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                )
            ):
                ready_pickings |= picking
            elif all(
                not float_is_zero(
                    move_id.quantity_done, precision_digits=precision_digits
                )
                and float_compare(
                    move_id.quantity_done,
                    move_id.product_uom_qty,
                    precision_digits=precision_digits,
                )
                >= 0
                for move_id in picking.move_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                )
            ):
                ready_pickings |= picking
        ready_pickings.update({"is_completed": True})
        (self - ready_pickings).update({"is_completed": False})

    def _get_is_completed_domain(self):
        return [
            ("move_ids.quantity_done", ">", 0),
            ("state", "not in", ["done", "cancel"]),
        ]

    def _get_is_not_completed_domain(self):
        return [
            "|",
            ("move_ids.quantity_done", "=", 0),
            ("state", "in", ["done", "cancel"]),
        ]

    def _search_is_completed(self, operator, value):
        negative = operator in NEGATIVE_TERM_OPERATORS

        if (value and negative) or (not value and not negative):
            pickings = self.search(self._get_is_not_completed_domain())
            returned_pickings = pickings.filtered_domain([("is_completed", "=", False)])
        else:
            pickings = self.search(self._get_is_completed_domain())
            returned_pickings = pickings.filtered_domain([("is_completed", "=", True)])

        return [("id", "in", returned_pickings.ids)]
