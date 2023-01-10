# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv.expression import AND


class StockMove(models.Model):

    _inherit = "stock.move"

    def _assign_picking_group_domain(self):
        """
        Group pickings per customer
        """
        domain = super()._assign_picking_group_domain()
        if self.picking_type_id.group_pickings_by_customer:
            domain = AND([domain, [("customer_id", "=", self.group_id.customer_id.id)]])
        return domain
