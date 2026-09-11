# Copyright 2019-2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_avco_layer_to_restate(self, move):
        """Return the layer this line's quantity correction has to restate."""
        self.ensure_one()
        layers = move.stock_valuation_layer_ids.filtered(
            lambda x: not x.stock_valuation_layer_id
        )
        if move.product_id.lot_valuated:
            layers = layers.filtered(lambda x: x.lot_id == self.lot_id)
        return layers[:1]

    @api.model
    def _create_correction_svl(self, move, diff):
        """Restate the layer of the move instead of appending a correction one.

        Odoo books the correction of an already validated quantity as a new
        layer dated the day the correction is made. That is fine for its own
        bookkeeping, but it leaves two things wrong for the reason this module
        exists:

        - A stock valuation as of a date before the correction still shows the
          wrong figures, because the report only sums the layers created up to
          that date (`product._get_valuation_layer_group_domain`). Companies
          that post the stock valuation periodically rather than movement by
          movement need the past to come out corrected once the mistake is
          fixed.
        - The outgoing layers that were valued in between keep the cost they
          were given, so anything derived from them, such as the margin
          `sale_margin_sync` pushes to the sale order line, stays wrong.

        Restating the layer as if the move had always had the corrected
        quantity fixes both, and `stock.valuation.layer.write` replays the
        chain from there on. The remaining quantity Odoo needs for the negative
        stock vacuum and for the invoice price difference is kept in step, and
        the vacuum is run afterwards just like Odoo does.
        """
        if (
            move.product_id.cost_method != "average"
            or self.env.context.get("new_stock_move_create")
            or not diff
        ):
            return super()._create_correction_svl(move, diff)
        layer = self._get_avco_layer_to_restate(move)
        if not layer:
            return super()._create_correction_svl(move, diff)
        # An outgoing layer holds a negative quantity, so delivering more units
        # has to make it more negative.
        layer._restate_avco_quantity(-diff if move._is_out() else diff)
        move.product_id._run_fifo_vacuum(move.company_id)

    @api.model_create_multi
    def create(self, vals_list):
        """Flag the creation so a correction that comes from a brand new line
        is left to Odoo: there is no previous layer of its own to restate.
        """
        return super(
            StockMoveLine, self.with_context(new_stock_move_create=True)
        ).create(vals_list)
