# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockPickingNoteType(models.Model):
    _name = "stock.picking.note.type"
    _description = "Picking Note Type"
    _order = "sequence,name"

    sequence = fields.Integer()
    name = fields.Char(required=True)
