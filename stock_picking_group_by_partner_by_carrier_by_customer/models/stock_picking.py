# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.model
    def _get_index_for_grouping_fields(self):
        """
        This tuple is intended to be overriden in order to add fields
        used in groupings
        """
        res = super()._get_index_for_grouping_fields()
        if "customer_id" not in res:
            res.append("customer_id")
        return res

    def init(self):
        """
        This has to be called in every overriding module
        """
        self._create_index_for_grouping()
