# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_draft(self):
        res = super().action_draft()
        self.procurement_group_id = False
        return res
