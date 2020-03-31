# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class DeliveryTimeWindow(models.Model):

    _name = "partner.delivery.time.window"
    _inherit = "time.window.mixin"
    _description = "Preferred delivery time windows"

    _overlap_check_field = 'partner_id'

    partner_id = fields.Many2one("res.partner")

    @api.constrains("partner_id")
    def check_window_no_overlaps(self):
        return super().check_window_no_overlaps()
