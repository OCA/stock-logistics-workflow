from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    can_be_estimated = fields.Boolean(
        "Can Be Estimated",
        compute="_compute_can_be_estimated",
    )

    demand_total_amount = fields.Float(
        "Demand Total Amount", compute="_compute_demand_total_amount"
    )
    reserved_total_amount = fields.Float(
        "Reserved Total Amount", compute="_compute_reserved_total_amount"
    )

    estimated_progress = fields.Float(
        "Estimated Progress", compute="_compute_estimated_progress"
    )

    # This is required because percentagepie and percentage use different
    # percentage representations
    estimated_progress_normalized = fields.Float(
        "Estimated Progress Normalized",
        compute="_compute_estimated_progress_normalized",
    )

    amount_currency_id = fields.Many2one(
        "res.currency",
        string="Amount Currency",
        compute="_compute_amount_currency_id",
    )

    def _compute_can_be_estimated(self):
        for picking in self:
            picking.can_be_estimated = (
                True if picking.sale_id or picking.purchase_id else False
            )

    def _compute_demand_total_amount(self):
        for picking in self:
            if picking.can_be_estimated:
                picking.demand_total_amount = sum(
                    picking.move_lines.mapped("product_price_demand_subtotal")
                )
            else:
                picking.demand_total_amount = False

    def _compute_reserved_total_amount(self):
        for picking in self:
            if picking.can_be_estimated:
                picking.reserved_total_amount = sum(
                    picking.move_lines.mapped("product_price_reserved_subtotal")
                )
            else:
                picking.reserved_total_amount = False

    def _compute_estimated_progress(self):
        for picking in self:
            if picking.can_be_estimated:
                picking.estimated_progress = (
                    picking.reserved_total_amount / picking.demand_total_amount * 100
                    if picking.demand_total_amount
                    else 0
                )
            else:
                picking.estimated_progress = False

    def _compute_estimated_progress_normalized(self):
        for picking in self:
            if picking.can_be_estimated:
                picking.estimated_progress_normalized = picking.estimated_progress / 100
            else:
                picking.estimated_progress_normalized = False

    def _compute_amount_currency_id(self):
        for picking in self:
            if picking.sale_id:
                picking.amount_currency_id = picking.sale_id.currency_id
            elif picking.purchase_id:
                picking.amount_currency_id = picking.purchase_id.currency_id
            else:
                picking.amount_currency_id = False


class StockMove(models.Model):
    _inherit = "stock.move"

    product_price = fields.Float("Product Price", compute="_compute_product_price")

    product_price_demand_subtotal = fields.Float(
        "Demand Subtotal",
        compute="_compute_product_price_demand_subtotal",
    )

    product_price_reserved_subtotal = fields.Float(
        "Reserved Subtotal",
        compute="_compute_product_price_reserved_subtotal",
    )

    amount_currency_id = fields.Many2one(related="picking_id.amount_currency_id")

    def _compute_product_price(self):
        for move in self:
            if move.picking_id.sale_id:
                move.product_price = move.product_id.lst_price
            elif move.picking_id.purchase_id:
                move.product_price = move.product_id.standard_price
            else:
                move.product_price = 0

    def _compute_product_price_demand_subtotal(self):
        for move in self:
            move.product_price_demand_subtotal = (
                move.product_price * move.product_uom_qty
            )

    def _compute_product_price_reserved_subtotal(self):
        for move in self:
            move.product_price_reserved_subtotal = (
                move.product_price * move.reserved_availability
            )
