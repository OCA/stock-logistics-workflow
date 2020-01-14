# Copyright 2020 Studio73 - Guillermo Llinares <guillermo@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def action_back_to_draft(self):
        picking_ids = self.mapped("picking_ids").filtered(lambda p: p.state == 'cancel')
        picking_ids.action_back_to_draft()
        return self.write({"state": "draft"})
