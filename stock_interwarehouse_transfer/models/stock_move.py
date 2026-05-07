# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    interwh_transfer_line_id = fields.Many2one(
        "stock.interwarehouse.transfer.line",
        string="Inter-WH Transfer Line",
        index=True,
        ondelete="set null",
    )

    # === CONSTRAINT METHODS ===

    @api.constrains("location_id", "location_dest_id", "picking_type_id")
    def _check_inter_warehouse_move(self):
        for move in self:
            if move.picking_type_id.code != "internal":
                continue
            wh_from = move.location_id.warehouse_id
            wh_to = move.location_dest_id.warehouse_id
            if wh_from and wh_to and wh_from != wh_to:
                raise ValidationError(
                    _(
                        "Cannot create an internal move between locations of "
                        "different warehouses (%(wh_from)s → %(wh_to)s). "
                        "Use an Inter-Warehouse Transfer instead.",
                        wh_from=wh_from.name,
                        wh_to=wh_to.name,
                    )
                )

    # === CORE METHODS ===

    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("interwh_transfer_line_id")
        return distinct_fields

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        transfer = self.interwh_transfer_line_id.transfer_id
        if len(transfer) == 1:
            vals["interwarehouse_transfer_id"] = transfer.id
        return vals
