# Copyright (C) 2025 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    lock_location_id = fields.Boolean(related="picking_type_id.lock_location_id")
    lock_location_dest_id = fields.Boolean(
        related="picking_type_id.lock_location_dest_id"
    )
