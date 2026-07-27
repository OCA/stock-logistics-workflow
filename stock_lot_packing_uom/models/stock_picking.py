# Copyright 2026 Abubakarafghan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        packing_by_line = self._collect_packing_info()
        res = super().button_validate()
        self._apply_packing_info(packing_by_line)
        return res

    def _action_done(self):
        packing_by_line = self._collect_packing_info()
        res = super()._action_done()
        self._apply_packing_info(packing_by_line)
        return res

    def _collect_packing_info(self):
        """Store packing UoM/qty before validation creates/links lots."""
        packing_by_line = {}
        for picking in self.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        ):
            for move in picking.move_ids.filtered(
                lambda m: m.product_id.tracking != "none"
            ):
                for line in move.move_line_ids:
                    packing_by_line[line.id] = self._get_line_packing_info(
                        move, line
                    )
        return packing_by_line

    def _apply_packing_info(self, packing_by_line):
        """Write packing fields onto lots created or selected on receipt."""
        for line_id, (packing_uom, packing_qty) in packing_by_line.items():
            line = self.env["stock.move.line"].browse(line_id).exists()
            if not line or not line.lot_id:
                continue
            line.lot_id.write(
                {
                    "packing_uom_id": packing_uom.id,
                    "received_qty": packing_qty,
                }
            )

    def _get_line_packing_info(self, move, line):
        """Resolve packing UoM and qty from PO line, move, or move line."""
        base_uom = line.product_id.uom_id
        if (
            move.purchase_line_id
            and move.purchase_line_id.product_uom != base_uom
        ):
            packing_uom = move.purchase_line_id.product_uom
        elif move.product_uom != base_uom:
            packing_uom = move.product_uom
        elif line.product_uom_id != base_uom:
            packing_uom = line.product_uom_id
        else:
            packing_uom = base_uom
        packing_qty = line.product_uom_id._compute_quantity(
            line.quantity, packing_uom
        )
        return packing_uom, packing_qty
