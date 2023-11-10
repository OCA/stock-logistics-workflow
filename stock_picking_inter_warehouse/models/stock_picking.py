# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    type_inter_warehouse_transfer = fields.Boolean(
        related="picking_type_id.inter_warehouse_transfer"
    )
    inter_warehouse_contact_domain_ids = fields.One2many(
        "res.partner", compute="_compute_inter_warehouse_contact_domain_ids"
    )

    @api.depends("picking_type_id.warehouse_id", "type_inter_warehouse_transfer")
    def _compute_inter_warehouse_contact_domain_ids(self):
        all_partner_ids = self.env["res.partner"].search([])
        for picking in self:
            if picking.type_inter_warehouse_transfer:
                picking.inter_warehouse_contact_domain_ids = (
                    self.env["stock.warehouse"]
                    .search([("id", "!=", picking.picking_type_id.warehouse_id.id)])
                    .mapped("receipt_picking_partner_id")
                )
            else:
                picking.inter_warehouse_contact_domain_ids = all_partner_ids

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if hasattr(super(), "_onchange_partner_id"):
            super()._onchange_partner_id()
        if (
            self.type_inter_warehouse_transfer
            and self.partner_id.default_stock_location_src_id
        ):
            self.picking_type_id.default_location_dest_id = (
                self.partner_id.default_stock_location_src_id
            )
