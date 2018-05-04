# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOSC - Alfredo de la Fuente
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends('group_id', 'sale_id.client_order_ref')
    def _compute_client_order_ref(self):
        for picking in self:
            if picking.group_id:
                cond = [('procurement_group_id', '=', picking.group_id.id)]
                sale = self.env['sale.order'].search(cond, limit=1)
                if sale:
                    picking.client_order_ref = sale.client_order_ref

    client_order_ref = fields.Char(string="Sale Reference/Description",
                                   compute="_compute_client_order_ref",
                                   store=True)
