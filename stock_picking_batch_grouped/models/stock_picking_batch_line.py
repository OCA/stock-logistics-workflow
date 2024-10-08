#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class StockPickingBatchLine(models.Model):
    _name = "stock.picking.batch.line"
    _description = "Line of a Batch Transfer"

    batch_id = fields.Many2one(
        comodel_name="stock.picking.batch",
        string="Batch Transfer",
        required=True,
        ondelete="cascade",
    )
    move_line_ids = fields.Many2many(
        comodel_name="stock.move.line",
        relation="stock_batch_grouped_move_line_rel",
        required=True,
        string="Move Lines",
    )
    company_id = fields.Many2one(
        related="batch_id.company_id",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        compute="_compute_from_move_lines",
        store=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        compute="_compute_from_move_lines",
        store=True,
        string="Lot/Serial",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="From",
        compute="_compute_from_move_lines",
        store=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="To",
        compute="_compute_from_move_lines",
        store=True,
    )
    reserved_qty = fields.Float(
        string="Reserved Quantity",
        compute="_compute_from_move_lines",
        store=True,
    )
    done_qty = fields.Float(
        string="Done Quantity",
        compute="_compute_from_move_lines",
        store=True,
        inverse="_inverse_done_qty",
    )

    @api.model
    def _get_groupby_move_line_fields(self):
        """Fields of stock.move.line to group by to compute grouped lines."""
        return [
            "product_id",
            "lot_id",
            "location_id",
            "location_dest_id",
        ]

    @api.model
    def _get_grouped_move_line_fields(self):
        """Fields of stock.move.line to group to compute grouped lines."""
        return [
            "reserved_qty",
            "qty_done",
        ]

    @api.model
    def _get_move_line_grouped_line_fields_map(self):
        """Map names of fields in stock.move.line to fields of grouped lines."""
        return {
            "product_id": "product_id",
            "lot_id": "lot_id",
            "location_id": "location_id",
            "location_dest_id": "location_dest_id",
            "reserved_qty": "reserved_qty",
            "qty_done": "done_qty",
        }

    @api.model
    def _prepare_batch_lines_values(self, grouped_move_lines_values):
        """Convert grouped values of move lines to values for grouped lines.

        :param grouped_move_lines_values: move lines values grouped
            as a result of `read_group`
        """
        fields_map = self._get_move_line_grouped_line_fields_map()
        fields_definitions = self.fields_get(
            allfields=set(fields_map.values()),
        )
        batch_lines_values = []
        for grouped_move_line_values in grouped_move_lines_values:
            batch_line_values = {}
            for move_line_field, move_line_value in grouped_move_line_values.items():
                grouped_line_field = fields_map.get(move_line_field)
                if grouped_line_field:
                    if move_line_value:
                        field_definition = fields_definitions.get(
                            grouped_line_field, dict()
                        )
                        # If the field is relational its value is (ID, name)
                        # but we only need its ID
                        if field_definition.get("relation"):
                            move_line_value = move_line_value[0]
                    batch_line_values[grouped_line_field] = move_line_value

            batch_lines_values.append(batch_line_values)
        return batch_lines_values

    @api.model
    def _depends_grouped_line(self):
        """List of fields that trigger the grouped line computation."""
        groupby_fields = self._get_groupby_move_line_fields()
        grouped_fields = self._get_grouped_move_line_fields()
        return ["move_line_ids." + f for f in set(groupby_fields + grouped_fields)]

    @api.depends(
        _depends_grouped_line,
    )
    def _compute_from_move_lines(self):
        groupby_fields = self._get_groupby_move_line_fields()
        grouped_fields = self._get_grouped_move_line_fields()
        for line in self:
            move_lines = line.move_line_ids
            grouped_move_lines_values = move_lines.read_group(
                [
                    ("id", "in", move_lines.ids),
                ],
                grouped_fields,
                groupby_fields,
                lazy=False,
            )
            batch_lines_values = self._prepare_batch_lines_values(
                grouped_move_lines_values
            )
            # Move lines in each batch line are already grouped,
            # that is why we only have values for one batch line
            batch_lines_values = batch_lines_values[0]
            line.update(batch_lines_values)

    def _inverse_done_qty(self):
        """Fill the grouped move lines from the oldest.

        If more quantity has been set than what had been reserved,
        set the remainder in the last line.
        """
        for line in self:
            done_qty = line.done_qty
            line_rounding = line.product_id.uom_id.rounding
            move_lines = line.move_line_ids.sorted("date")
            for move_line in move_lines:
                if (
                    float_compare(
                        done_qty,
                        0,
                        precision_rounding=line_rounding,
                    )
                    > 0
                ):
                    line_reserved_qty = move_line.reserved_uom_qty
                    if (
                        float_compare(
                            line_reserved_qty,
                            done_qty,
                            precision_rounding=line_rounding,
                        )
                        < 0
                    ):
                        line_qty = line_reserved_qty
                    else:
                        line_qty = done_qty

                    done_qty -= line_qty
                    move_line.qty_done = line_qty
                else:
                    move_line.qty_done = 0

            last_move_line = move_lines[-1]
            if (
                float_compare(
                    done_qty,
                    0,
                    precision_rounding=line_rounding,
                )
                > 0
            ) and last_move_line:
                last_move_line.qty_done += done_qty

    @api.model
    def _get_grouped_move_lines(self, move_lines):
        """Group `move_lines` based on `_get_groupby_move_line_fields`.

        :return: List of recordsets
        """
        groupby_fields = self._get_groupby_move_line_fields()
        grouped_move_lines_values = move_lines.read_group(
            [
                ("id", "in", move_lines.ids),
            ],
            ["id"],
            groupby_fields,
            lazy=False,
        )
        grouped_move_lines = []
        for grouped_move_line_values in grouped_move_lines_values:
            domain = grouped_move_line_values["__domain"]
            grouped_move_lines.append(self.env["stock.move.line"].search(domain))
        return grouped_move_lines

    @api.model
    def create_from_move_lines(self, move_lines):
        """Create grouped lines from `move_lines`."""
        grouped_move_lines = self._get_grouped_move_lines(move_lines)
        batch_lines_values = []
        for move_lines_group in grouped_move_lines:
            batch_lines_values.append(
                {
                    "move_line_ids": move_lines_group.ids,
                    "batch_id": move_lines_group.move_id.picking_id.batch_id.id,
                }
            )
        return self.create(batch_lines_values)
