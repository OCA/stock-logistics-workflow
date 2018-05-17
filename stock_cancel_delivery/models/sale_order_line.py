# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def unlink(self):
        if self.filtered(lambda s: s.is_delivery) and self.env.context.get(
                'reopen_picking'):
            return models.Model.unlink(self)
        else:
            return super(SaleOrderLine, self).unlink()
