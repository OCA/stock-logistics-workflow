# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models
from odoo.tools import SQL


class StockMove(models.Model):
    _inherit = "stock.move"

    position = fields.Char(readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        # Number the new moves in their picking.
        moves = super().create(vals_list)
        # A move can be attached to an already-numbered picking directly at
        # create() (picking_id set in vals, e.g. purchase_stock's
        # _create_or_update_picking()), which never calls
        # stock.picking.write() and so never triggers its auto-renumbering.
        # Moves that already carry a position (e.g. a split, which inherits
        # it via _prepare_move_split_vals()) must be left untouched.
        moves.filtered(
            lambda m: not m.position
        ).picking_id._auto_renumber_lines_positions()
        return moves

    def write(self, vals):
        # Number the moves assigned to another picking.
        res = super().write(vals)
        if "picking_id" in vals:
            # Same as create(): a move can be assigned to an existing
            # picking after the fact (e.g. stock.move._assign_picking()),
            # bypassing stock.picking.write().
            self.filtered(
                lambda m: not m.position
            ).picking_id._auto_renumber_lines_positions()
        return res

    def _prepare_move_split_vals(self, qty):
        # Keep the position on the split move.
        res = super()._prepare_move_split_vals(qty)
        res["position"] = self.position
        return res

    def _order_field_to_sql(self, alias, field_name, direction, nulls, query):
        # Sort position as a number ("10" after "9"), to list the moves of a transfer
        # in their order in the views.
        if field_name == "position":
            sql_field = self._field_to_sql(alias, field_name, query)
            return SQL("LPAD(%s, 10, '0') %s %s", sql_field, direction, nulls)
        return super()._order_field_to_sql(alias, field_name, direction, nulls, query)
