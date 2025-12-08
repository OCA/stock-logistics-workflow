# 2026 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    usage_ids = fields.One2many(
        comodel_name="stock.move.valuation.usage",
        inverse_name="src_stock_move_id",
        string="Valuation Usage",
        help="Trace in what stock moves has this move's valuation been used, "
        "including the quantities and values taken.",
    )
    incoming_usage_ids = fields.One2many(
        comodel_name="stock.move.valuation.usage",
        inverse_name="dest_stock_move_id",
        string="Incoming Valuation Usage",
        help="Trace in what stock moves has this move's valuation been used, "
        "including the quantities and values taken.",
    )
    incoming_usage_quantity = fields.Float(
        string="Incoming Usage quantity",
        compute="_compute_incoming_usages",
        store=True,
    )
    incoming_usage_value = fields.Float(
        string="Incoming Usage value",
        compute="_compute_incoming_usages",
        store=True,
    )
    usage_quantity = fields.Float(
        compute="_compute_usage_values",
        store=True,
    )
    usage_value = fields.Float(
        compute="_compute_usage_values",
        store=True,
    )

    @api.depends("incoming_usage_ids.quantity", "incoming_usage_ids.value")
    def _compute_incoming_usages(self):
        for rec in self:
            rec.incoming_usage_quantity = sum(rec.incoming_usage_ids.mapped("quantity"))
            rec.incoming_usage_value = sum(rec.incoming_usage_ids.mapped("value"))

    @api.depends("usage_ids.quantity", "usage_ids.value")
    def _compute_usage_values(self):
        for rec in self:
            rec.usage_quantity = sum(rec.usage_ids.mapped("quantity"))
            rec.usage_value = sum(rec.usage_ids.mapped("value"))

    def _set_value(self, correction_quantity=None):
        fifo_moves = self.filtered(
            lambda m: m._is_out() and m.product_id.cost_method == "fifo"
        )
        if fifo_moves:
            # Process FIFO moves with context
            for move in fifo_moves:
                super(StockMove, move.with_context(valued_move=move))._set_value(
                    correction_quantity=correction_quantity
                )
            # Process non-FIFO moves normally
            return (self - fifo_moves)._set_value(
                correction_quantity=correction_quantity
            )
        else:
            return super()._set_value(correction_quantity=correction_quantity)

    def _action_done(self, cancel_backorder=False):
        result = super()._action_done(cancel_backorder=cancel_backorder)
        dropship_fifo = result.filtered(
            lambda m: m.is_dropship
            and m.product_id.cost_method == "fifo"
            and m.quantity > 0
        )
        for move in dropship_fifo:
            move._create_usage_record(
                src_move=move,
                dest_move=move,
                quantity=move.quantity,
                value=move.quantity * move._get_unit_cost(),
            )
        # Backfill usage links for earlier outgoing moves
        # that had no stock (negative FIFO scenario)
        result._handle_negative_fifo_revaluation()
        return result

    def _handle_negative_fifo_revaluation(self):
        incoming_fifo = self.filtered(
            lambda m: m.location_id.usage in ("supplier", "production")
            and m.location_dest_id.usage == "internal"
            and m.product_id.cost_method == "fifo"
        )

        for move in incoming_fifo:
            # Find negative outgoing moves for this product
            negative_moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("state", "=", "done"),
                    ("location_id.usage", "=", "internal"),
                    ("location_dest_id.usage", "=", "customer"),
                    ("company_id", "=", move.company_id.id),
                    ("date", "<=", move.date),
                    ("incoming_usage_ids", "=", False),
                ]
            )
            for out_move in negative_moves:
                out_move._create_usage_record(
                    src_move=move,
                    dest_move=out_move,
                    quantity=out_move.quantity,
                    value=out_move.quantity * move._get_unit_cost(),
                )

    def _get_unit_cost(self):
        self.ensure_one()
        return (
            abs(self.price_unit) if self.price_unit else self.product_id.standard_price
        )

    @api.model
    def _create_usage_record(self, src_move, dest_move, quantity, value):
        self.env["stock.move.valuation.usage"].sudo().create(
            {
                "src_stock_move_id": src_move.id,
                "dest_stock_move_id": dest_move.id,
                "quantity": quantity,
                "value": value,
                "company_id": dest_move.company_id.id,
            }
        )
