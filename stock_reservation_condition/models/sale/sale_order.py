# -*- coding: utf-8 -*-
# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    reservation_date = fields.Date(
        help="Set if you don't want to reserve stock until that date.")
    reservation_po_ids = fields.Many2many(
        'purchase.order', 'sale_purchase_rel', 'sale_id', 'purchase_id',
        help="Set if you don't want to reserve stock until "
             "these Purchase Orders are received."
    )
