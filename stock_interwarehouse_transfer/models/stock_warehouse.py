# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    out_inter_wh_type_id = fields.Many2one(
        "stock.picking.type",
        string="Inter-WH Out Type",
        check_company=True,
        copy=False,
    )
    in_inter_wh_type_id = fields.Many2one(
        "stock.picking.type",
        string="Inter-WH In Type",
        check_company=True,
        copy=False,
    )

    def _ensure_inter_wh_op_types(self):
        for wh in self:
            transit_loc = wh.company_id.internal_transit_location_id
            if not wh.out_inter_wh_type_id:
                wh.out_inter_wh_type_id = self.env["stock.picking.type"].create(
                    {
                        "name": "Inter-Warehouse Transfers",
                        "code": "outgoing",
                        "sequence_code": "IW",
                        "warehouse_id": wh.id,
                        "company_id": wh.company_id.id,
                        "default_location_src_id": wh.lot_stock_id.id,
                        "default_location_dest_id": transit_loc.id,
                    }
                )
            if not wh.in_inter_wh_type_id:
                wh.in_inter_wh_type_id = self.env["stock.picking.type"].create(
                    {
                        "name": "Inter-Warehouse Receipts",
                        "code": "incoming",
                        "sequence_code": "IWR",
                        "warehouse_id": wh.id,
                        "company_id": wh.company_id.id,
                        "default_location_src_id": transit_loc.id,
                        "default_location_dest_id": wh.lot_stock_id.id,
                    }
                )
