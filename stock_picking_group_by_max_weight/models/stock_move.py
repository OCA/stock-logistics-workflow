# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv.expression import AND


class StockMove(models.Model):

    _inherit = "stock.move"

    def _search_picking_for_assignation_domain(self):
        """
        Group pickings per customer
        """
        domain = super()._search_picking_for_assignation_domain()
        if self.picking_type_id.group_pickings_maxweight:
            domain = AND(
                [
                    domain,
                    [("assignation_max_weight", ">=", self.weight)],
                ]
            )
        return domain
