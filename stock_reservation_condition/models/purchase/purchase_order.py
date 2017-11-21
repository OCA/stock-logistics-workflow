# -*- coding: utf-8 -*-
# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    reservation_date = fields.Date(
        compute='_compute_reservation_date',
        help='Date of the last reception in status "Done".'
    )

    @api.model
    def _compute_reservation_date(self):
        for rec in self:
            if rec.picking_ids:
                picking_ids = rec.picking_ids.sorted(lambda p: p.min_date)
                if picking_ids:
                    rec.reservation_date = fields.Datetime.from_string(
                        picking_ids[0].min_date).date()
