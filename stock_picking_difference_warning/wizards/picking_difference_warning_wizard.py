# Copyright 2023, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PickingDifferenceWarningWizard(models.TransientModel):
    _name = "picking.difference.warning.wizard"
    _description = "Picking Difference Warning Wizard"

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        required=True,
        readonly=True,
    )
    picking_difference_warning_line_ids = fields.One2many(
        comodel_name="picking.difference.warning.line.wizard",
        inverse_name="picking_difference_warning_id",
        readonly=True,
    )

    def action_validate(self):
        self.ensure_one()
        return self.picking_ids.with_context(
            skip_difference_check=True
        ).button_validate()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "picking_ids" in fields_list and not res.get("picking_ids"):
            res["picking_ids"] = [(6, 0, self._context.get("default_picking_ids", []))]
        if "picking_difference_warning_line_ids" in fields_list and not res.get(
            "picking_difference_warning_line_ids"
        ):
            pickings = self.env["stock.picking"].browse(res["picking_ids"][0][2])
            res["picking_difference_warning_line_ids"] = [
                (
                    0,
                    0,
                    {
                        "move_id": move.id,
                    },
                )
                for move in pickings.mapped("move_ids_without_package")
                .filtered(
                    lambda m: m.state not in ["cancel", "done"]
                    and m.original_qty != m.quantity_done
                )
                .sorted(key=lambda m: m.quantity_done - m.original_qty)
            ]
        return res


class PickingDifferenceWarningLineWizard(models.TransientModel):
    _name = "picking.difference.warning.line.wizard"
    _description = "Picking Difference Warning Line Wizard"

    picking_difference_warning_id = fields.Many2one(
        comodel_name="picking.difference.warning.wizard",
        required=True,
        readonly=True,
    )
    picking_id = fields.Many2one(
        related="move_id.picking_id",
        readonly=True,
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
        required=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        related="move_id.product_id",
        readonly=True,
    )
    quantity_done = fields.Float(
        related="move_id.quantity_done",
        readonly=True,
    )
    original_qty = fields.Float(
        related="move_id.original_qty",
        readonly=True,
    )
    difference = fields.Float(
        compute="_compute_difference",
    )

    @api.depends("quantity_done", "original_qty")
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.quantity_done - rec.original_qty
