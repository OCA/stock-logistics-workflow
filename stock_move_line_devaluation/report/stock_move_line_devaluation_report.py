from odoo import fields, models


class StockMoveLineDevaluationReport(models.TransientModel):
    _name = "stock.move.line.devaluation.report"
    _description = "Stock Withdrawal Valuation Report"
    _order = "date desc, id"
    _transient_max_hours = 4.0

    move_line_id = fields.Many2one(
        comodel_name="stock.move.line",
        string="Move Line",
        readonly=True,
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Transfer",
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot/Serial",
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        readonly=True,
    )
    responsible_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        readonly=True,
    )
    date = fields.Datetime(
        readonly=True,
    )
    qty_done = fields.Float(
        string="Original Qty",
        digits="Product Unit of Measure",
        readonly=True,
    )
    returned_qty = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
    )
    net_qty = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        readonly=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="From",
        readonly=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="To",
        readonly=True,
    )
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        readonly=True,
    )
    standard_price = fields.Float(
        string="Cost",
        digits="Product Price",
        readonly=True,
    )
    unit_price = fields.Float(
        digits="Product Price",
        readonly=True,
    )
    total_value = fields.Float(
        digits="Product Price",
        readonly=True,
    )
