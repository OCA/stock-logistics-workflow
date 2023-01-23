# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    grn_id = fields.Many2one(
        comodel_name="stock.grn",
        string="Goods Received Note",
        copy=False,
        readonly=True,
    )
    grn_date = fields.Datetime(
        related="grn_id.date", string="GRN Date", store=True, index=True, readonly=True
    )
    delivery_note_supplier_number = fields.Char(
        related="grn_id.delivery_note_supplier_number",
        string="Supplier delivery note number",
        store=True,
        readonly=True,
    )
