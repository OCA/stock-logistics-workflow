# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _get_new_picking_values(self):
        """
        Inherit to fill the delivery_note on the new picking if this field
        is defined on the related sale order.
        :return: dict
        """
        values = super(StockMove, self)._get_new_picking_values()
        if self.procurement_id.sale_line_id:
            sale = self.procurement_id.sale_line_id.order_id
            values.update({"delivery_note": sale.delivery_note})
        return values
