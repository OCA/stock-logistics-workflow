# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class StockValuationLayerRevaluation(models.TransientModel):
    _inherit = "stock.valuation.layer.revaluation"

    current_value_lot = fields.Float(
        "Current Value ", compute="_compute_current_value_lot"
    )
    current_quantity_lot = fields.Float(
        "Current Quantity", compute="_compute_current_value_lot"
    )
    lot_id = fields.Many2one("stock.lot", "Lot/Serial Number")
    display_lot_id = fields.Boolean(compute="_compute_display_lot_id")

    def _get_remaining_stock_move_lines(self, lot_id=None):
        self.ensure_one()
        domain = [
            ("product_id", "=", self.product_id.id),
            ("company_id", "=", self.company_id.id),
            ("qty_remaining", ">", 0.0),
        ]
        if lot_id:
            domain.append(("lot_id", "=", lot_id.id))
        return self.env["stock.move.line"].search(domain)

    @api.depends("lot_id")
    def _compute_current_value_lot(self):
        for rec in self:
            rec.current_quantity_lot = 0.0
            rec.current_value_lot = 0.0
            if not rec.lot_id:
                continue
            move_lines = rec._get_remaining_stock_move_lines(rec.lot_id)
            rec.current_quantity_lot = sum(move_lines.mapped("qty_remaining"))
            rec.current_value_lot = sum(move_lines.mapped("value_remaining"))

    @api.depends("product_id")
    def _compute_display_lot_id(self):
        for rec in self:
            rec.display_lot_id = False
            product = rec.product_id
            if product.tracking != "none" and product.cost_method == "fifo":
                rec.display_lot_id = True

    @api.depends(
        "current_value_svl",
        "current_quantity_svl",
        "added_value",
        "lot_id",
        "current_value_lot",
        "current_quantity_lot",
    )
    def _compute_new_value(self):
        revaluations = self.filtered(lambda l: l.lot_id)
        for reval in revaluations:
            reval.new_value = reval.current_value_lot + reval.added_value
            if (
                float_compare(
                    reval.new_value, 0.0, precision_rounding=self.currency_id.rounding
                )
                < 0
            ):
                raise UserError(_("The new value for the lot cannot be negative."))
            if not float_is_zero(
                reval.current_quantity_lot,
                precision_rounding=self.product_id.uom_id.rounding,
            ):
                reval.new_value_by_qty = reval.new_value / reval.current_quantity_lot
            else:
                reval.new_value_by_qty = 0.0
        return super(
            StockValuationLayerRevaluation, self - revaluations
        )._compute_new_value()

    @api.onchange("product_id")
    def _onchange_product_id_set_lot_domain(self):
        if not self.product_id:
            return
        remaining_lots = self._get_remaining_stock_move_lines().mapped("lot_id")
        return {"domain": {"lot_id": [("id", "in", remaining_lots.ids)]}}

    def action_validate_revaluation(self):
        self.ensure_one()
        if not self.lot_id:
            return super().action_validate_revaluation()
        if self.currency_id.is_zero(self.added_value):
            raise UserError(
                _("The added value doesn't have any impact on the stock valuation.")
            )
        product = self.product_id.with_company(self.company_id)
        reason_text = self.reason if self.reason else _("No Reason Given")
        description = _("Manual Lot Valuation: %s", reason_text)
        # We don't use self.new_value_by_qty (monetary) to avoid unwanted rounding
        new_value_per_qty = self.new_value / self.current_quantity_lot
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("lot_id", "=", self.lot_id.id),
                ("location_id.usage", "=", "internal"),
            ]
        )
        quants = quants.with_context(
            inventory_name=description,
            lot_revaluation_account=self.account_id,
            lot_revaluation_journal=self.account_journal_id,
        )
        # Keep the current quant quantities to restore them later
        quant_qty_dict = {quant: quant.quantity for quant in quants}
        # Remove the exsiting on-hand quantities first
        quants.inventory_quantity = 0
        quants.accounting_date = self.date
        quants.action_apply_inventory()
        # Restore the quantities to the quants
        product.standard_price = new_value_per_qty
        for quant in quants:
            quant.write({"inventory_quantity": quant_qty_dict[quant]})
        quants.accounting_date = self.date
        # Assign context so that the created stock is valued with product standard price
        quants = quants.with_context(lot_revaluation=True)
        quants.action_apply_inventory()
        return True
