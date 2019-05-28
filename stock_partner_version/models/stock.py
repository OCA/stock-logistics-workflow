# -*- coding: utf-8 -*-
# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_confirm(self):
        for picking in self.filtered('partner_id'):
            picking.partner_id = picking.partner_id.get_address_version()
        return super(StockPicking, self).action_confirm()
