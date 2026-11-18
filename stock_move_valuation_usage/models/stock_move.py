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

    def _set_value(self, recompute_date=None, skip_check=False):
        if not recompute_date:
            # The FIFO valuation creates the usage records of these moves again
            self.filtered(
                lambda m: (
                    m.is_out
                    and m.product_id.with_company(m.company_id).cost_method == "fifo"
                )
            ).sudo().incoming_usage_ids.unlink()
        return super()._set_value(recompute_date=recompute_date, skip_check=skip_check)

    def _action_done(self, cancel_backorder=False):
        result = super()._action_done(cancel_backorder=cancel_backorder)
        dropship_fifo = result.filtered(
            lambda m: (
                m.is_dropship and m.product_id.cost_method == "fifo" and m.quantity > 0
            )
        )
        for move in dropship_fifo:
            move._create_usage_record(
                src_move=move,
                dest_move=move,
                quantity=move.quantity,
                value=move.quantity * move._get_unit_cost(),
            )
        return result

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
