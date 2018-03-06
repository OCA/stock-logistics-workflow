# -*- coding: utf-8 -*-
# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.models import Model


class StockPicking(Model):
    _inherit = 'stock.picking'

    @api.model
    def check_assign_all(self):
        """ Try to assign confirmed pickings """
        type_obj = self.env['stock.picking.type']
        out_type_ids = type_obj.search([('code', '=', 'outgoing')]).ids
        domain = [('picking_type_id', 'in', out_type_ids),
                  ('state', '=', 'confirmed')]
        records = self.search(domain, order='min_date')
        records.action_assign()
