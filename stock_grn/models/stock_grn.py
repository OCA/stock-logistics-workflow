# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import api, fields, models


class StockGrn(models.Model):
    """Goods Received Note"""

    _name = "stock.grn"
    _description = "Goods Received Note"
    _order = "id desc"

    name = fields.Char(copy=False, index=True, required=True, default="/")
    carrier_id = fields.Many2one("res.partner", string="Carrier", required=True)
    carrier_ref = fields.Char(string="Carrier Id")

    from_info = fields.Char(string="From")
    ref = fields.Char(string="Reference")

    date = fields.Datetime(required=True, default=lambda self: fields.Datetime.now())
    description = fields.Text()
    type_id = fields.Many2one("stock.grn.type", string="Grn Type")
    qty_pallet = fields.Integer(string="Qty Pallets")
    qty_box = fields.Integer(string="Qty Boxes")
    delivery_note_supplier_number = fields.Char(
        string="Supplier delivery note number", required=True
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        change_default=True,
        default=lambda self: self.env["res.company"]._company_default_get("stock.grn"),
        required=True,
        readonly=True,
    )

    picking_ids = fields.One2many(
        "stock.picking",
        "grn_id",
        string="Incoming Shipments",
        domain=[("picking_type_code", "=", "incoming")],
    )

    supplier_id = fields.Many2one(
        "res.partner", string="Supplier", related="picking_ids.partner_id", store=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("stock.grn") or "/"
        return super().create(vals_list)
