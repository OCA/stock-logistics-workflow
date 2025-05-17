# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.models import Model


class StockPicking(Model):
    _inherit = "stock.picking"

    @api.model
    def check_assign_all(self, domain=None):
        """Try to assign confirmed pickings"""
        search_domain = [("state", "=", "confirmed")]
        if domain:
            search_domain += domain
        else:
            search_domain += [("picking_type_code", "=", "outgoing")]
        records = self.search(search_domain, order="scheduled_date")
        records.action_assign()
