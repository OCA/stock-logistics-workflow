# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    note = fields.Html(compute="_compute_note", store=True)

    @api.depends("partner_id")
    def _compute_note(self):
        for picking in self:
            picking_type_note_type_ids = picking.picking_type_id.partner_note_type_ids
            picking_notes = picking.partner_id.stock_picking_note_ids.filtered(
                lambda n: n.note_type_id in picking_type_note_type_ids
            )
            picking_notes = [
                note.name.strip()
                for note in picking_notes
                if note.name and note.name.strip()
            ]
            picking.note = "<br />".join(picking_notes)
