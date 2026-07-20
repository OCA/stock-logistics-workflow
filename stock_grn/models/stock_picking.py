# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import api, fields, models


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
    dock_ids = fields.Many2many(
        comodel_name="stock.dock",
        string="Docks",
        compute="_compute_dock_ids",
        store=True,
    )

    @api.depends("grn_id", "grn_id.dock_ids")
    def _compute_dock_ids(self):
        for rec in self:
            rec.dock_ids = rec.grn_id.dock_ids
