# Copyright (C) 2023 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    kit_product_id = fields.Many2one(
        "product.product",
        compute="_compute_kit_product_id",
        store=True,
        index=True,
    )
    kit_sequence = fields.Integer(readonly=True)
    kit_first_in_box = fields.Boolean()

    @api.depends("move_id.bom_line_id")
    def _compute_kit_product_id(self):
        """Identify the kit product this move line belongs to.

        Uses the bom_line_id on the stock.move, which is set when
        a phantom BOM (kit) is exploded into component moves.
        """
        for line in self:
            bom_line = line.move_id.bom_line_id
            if bom_line and bom_line.bom_id.type == "phantom":
                bom = bom_line.bom_id
                line.kit_product_id = (
                    bom.product_id or bom.product_tmpl_id.product_variant_ids[:1]
                )
            else:
                line.kit_product_id = False

    def action_pack_all_kits(self):
        """Pack all kit lines on the picking. Called from list view header."""
        self.picking_id.action_pack_all_kits()

    def _get_kit_box_groups(self):
        """Return kit lines grouped per box (kit unit) as a list of recordsets.

        For each component (bom_line), lines are in creation order.
        The Nth line of each component belongs to the same kit unit.
        Returns: list of recordsets, one per box.
        """
        component_lines = defaultdict(list)
        for line in self.sorted(
            key=lambda ml: (ml.move_id.bom_line_id.sequence or 0, ml.id)
        ):
            component_lines[line.move_id.bom_line_id.id].append(line)

        max_units = max((len(lines) for lines in component_lines.values()), default=0)
        MoveLines = self.env["stock.move.line"]
        boxes = []
        for unit_idx in range(max_units):
            box = MoveLines
            for lines in component_lines.values():
                if unit_idx < len(lines):
                    box |= lines[unit_idx]
            boxes.append(box)
        return boxes

    def _assign_kit_sequence(self):
        """Assign kit_sequence and kit_first_in_box for per-box view ordering."""
        for box_idx, box_lines in enumerate(self._get_kit_box_groups()):
            for line in box_lines:
                bom_seq = line.move_id.bom_line_id.sequence or 0
                new_seq = box_idx * 1000 + bom_seq
                is_first = line == box_lines[0]
                if line.kit_sequence != new_seq:
                    line.kit_sequence = new_seq
                if line.kit_first_in_box != is_first:
                    line.kit_first_in_box = is_first
