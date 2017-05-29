# -*- coding: utf-8 -*-
# Copyright 2014 ALeonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class Product(models.Model):
    _inherit = 'product.template'

    @api.multi
    def action_open_quants(self):
        result = super(Product, self).action_open_quants()
        result['context'] = (
            "{'search_default_locationgroup': 1, "
            "'search_default_ownergroup': 1, "
            "'search_default_internal_loc': 1, "
            "'search_default_without_reservation': 1}"
        )
        return result
