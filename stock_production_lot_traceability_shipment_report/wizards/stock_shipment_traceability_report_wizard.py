# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockTraceabilityDeliveryReportWizard(models.TransientModel):
    _name = "stock.shipment.traceability.report.wizard"
    _description = "Stock Traceability Delivery Report Wizard"

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain="[('type', '=', 'product')]",
    )
    lot_id = fields.Many2one(
        "stock.production.lot",
        string="Lot/Serial Number",
        domain="[('product_id', '=?', product_id)]",
        required=True,
    )

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        if self.lot_id and self.lot_id.product_id != self.product_id:
            self.product_id = self.lot_id.product_id

    def _get_affected_lots(self):
        """Get all the lots affected by ``self.lot_id``"""
        return self.lot_id | self.lot_id.produce_lot_ids

    def _get_affected_move_lines(self):
        lots = self._get_affected_lots()
        return self.env["stock.move.line"].search(
            [
                ("state", "=", "done"),
                ("lot_id", "in", lots.ids),
                "|",
                ("location_id.usage", "=", "customer"),
                ("location_dest_id.usage", "=", "customer"),
            ]
        )

    def confirm(self):
        self.ensure_one()
        lines = self._get_affected_move_lines()
        if not lines:  # pragma: no cover
            raise UserError(_("There isn't any shipment involving this lot."))
        module = "stock_production_lot_traceability_shipment_report"
        xml_id = "action_stock_shipment_traceability_report"
        action = self.env["ir.actions.act_window"]._for_xml_id(f"{module}.{xml_id}")
        action["display_name"] += f" ({self.lot_id.display_name})"
        action["domain"] = [("id", "in", lines.ids)]
        return action
