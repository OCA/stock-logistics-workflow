# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockPickingNote(models.Model):
    _name = "stock.picking.note"
    _description = "Picking Note"
    _order = "sequence,name"

    name = fields.Text(required=True)
    active = fields.Boolean(default=True)
    note_type_id = fields.Many2one("stock.picking.note.type", required=True)
    sequence = sequence = fields.Integer(related="note_type_id.sequence", store=True)
