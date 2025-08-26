# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MakePickingBatch(models.TransientModel):
    _inherit = "make.picking.batch"

    def _get_picking_kit_quantity(self, picking):
        """Compute the kit quantity of the picking

        The kit quantity is the number of kits + number of regular products
        in the picking.
        """
        kit_moves = picking.move_ids.filtered(
            lambda m: m.bom_line_id.bom_id.type == "phantom"
        )
        kit_moves_by_bom = kit_moves.grouped(lambda m: m.bom_line_id.bom_id)
        kit_quantity = 0.0
        # Process kits
        for bom, moves in kit_moves_by_bom.items():
            kit_quantity += moves._compute_kit_quantities(
                bom.product_id,
                max(moves.mapped("product_qty")),
                bom,
                {
                    "incoming_moves": lambda m: True,
                    "outgoing_moves": lambda m: False,
                },
            )
        # Process regular products
        regular_moves = picking.move_ids - kit_moves
        kit_quantity += sum(regular_moves.mapped("product_uom_qty"))
        return kit_quantity

    def _is_picking_exceeding_limits(self, picking):
        # OVERRIDE to handle kit quantity mode
        last_device = self.stock_device_type_ids[-1]
        if last_device.split_mode == "kit_quantity":
            return self._get_picking_kit_quantity(picking) > last_device.nbr_bins
        return super()._is_picking_exceeding_limits(picking)

    def _split_first_picking_for_limit(self, picking):
        # OVERRIDE to handle kit quantity mode
        last_device = self.stock_device_type_ids[-1]
        if last_device.split_mode == "kit_quantity":
            return (
                self.env["stock.split.picking"]
                .with_context(active_ids=picking.ids)
                .create(
                    {
                        "mode": "kit_quantity",
                        "kit_split_quantity": last_device.nbr_bins,
                    }
                )
                ._action_apply()
            )
        return super()._split_first_picking_for_limit(picking)
