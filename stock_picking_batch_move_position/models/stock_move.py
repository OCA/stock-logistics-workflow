# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models
from odoo.tools import SQL


class StockMove(models.Model):
    _inherit = "stock.move"

    batch_position = fields.Char(readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        # Number the new moves in their batch.
        moves = super().create(vals_list)
        # A move added to a picking that is already in a batch never goes
        # through stock.picking.batch.write(), and would be left without
        # batch_position. Split moves keep theirs.
        moves.filtered(
            lambda m: not m.batch_position
        ).picking_id.batch_id._auto_renumber_lines_positions()
        return moves

    def write(self, vals):
        # Number the moves assigned to a picking of a batch.
        res = super().write(vals)
        if "picking_id" in vals:
            # A move coming from another batch would keep a batch_position
            # that can collide with the new batch's: renumber it too.
            self.picking_id.batch_id._auto_renumber_lines_positions()
        return res

    def _prepare_move_split_vals(self, qty):
        # Keep the batch position on the split move.
        res = super()._prepare_move_split_vals(qty)
        res["batch_position"] = self.batch_position
        return res

    def _order_field_to_sql(self, alias, field_name, direction, nulls, query):
        # Sort batch_position as a number ("10" after "9"), to list the moves of a batch
        # in their order in the views.
        if field_name == "batch_position":
            sql_field = self._field_to_sql(alias, field_name, query)
            return SQL("LPAD(%s, 10, '0') %s %s", sql_field, direction, nulls)
        return super()._order_field_to_sql(alias, field_name, direction, nulls, query)
