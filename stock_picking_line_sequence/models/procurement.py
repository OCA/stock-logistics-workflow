# -*- coding: utf-8 -*-
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    # Needed to propagate the sequence to the picking
    def _get_stock_move_values(self):
        vals = super(ProcurementOrder, self)._get_stock_move_values()
        if self.sale_line_id:
            vals.update({'sequence': self.sale_line_id.sequence})
        return vals
