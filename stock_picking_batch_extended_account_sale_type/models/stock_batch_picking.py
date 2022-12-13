# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockBatchPicking(models.Model):
    _inherit = "stock.picking.batch"

    def _get_domain_picking_to_invoice(self):
        domain = super()._get_domain_picking_to_invoice()
        return [
            "|",
            "&",
            ("partner_id.batch_picking_auto_invoice", "=", "sale_type"),
            ("sale_id.type_id.batch_picking_auto_invoice", "=", True),
        ] + domain
