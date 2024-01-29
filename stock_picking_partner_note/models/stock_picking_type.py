# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    partner_note_type_ids = fields.Many2many(
        "stock.picking.note.type",
        help="Type of note with customer preferences on how his products are prepared "
        "for delivery.",
    )
