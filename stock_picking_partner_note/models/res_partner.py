# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    stock_picking_note_ids = fields.Many2many(
        comodel_name="stock.picking.note",
        string="Picking Notes",
    )

    def write(self, vals):
        # Update notes on open pickings
        res = super().write(vals)
        if "stock_picking_note_ids" in vals:
            self.env["stock.picking"].search(
                [
                    ("partner_id", "child_of", self.ids),
                    ("state", "in", ("draft", "waiting", "confirmed", "assigned")),
                ]
            )._compute_note()
        return res
