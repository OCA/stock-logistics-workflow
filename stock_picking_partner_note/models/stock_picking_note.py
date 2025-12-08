# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPickingNote(models.Model):
    _name = "stock.picking.note"
    _description = "Picking Note"
    _order = "sequence,name"

    name = fields.Text(required=True)
    active = fields.Boolean(default=True)
    note_type_id = fields.Many2one("stock.picking.note.type", required=True)
    sequence = fields.Integer(related="note_type_id.sequence", store=True)

    def write(self, vals):
        if "active" not in vals:
            self.check_note_already_in_use()
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def check_note_already_in_use(self):
        if not self.env.user.company_id.check_note_already_in_use:
            return True
        for note in self:
            partners = self.env["res.partner"].search(
                [("stock_picking_note_ids", "in", note.ids)]
            )
            if len(partners) > 1:
                raise UserError(
                    self.env._(
                        "You cannot update or delete a note that is linked to multiple"
                        " contacts: %(partner_ids)s",
                        partner_ids=", ".join(partners.mapped("name")),
                    )
                )
        return True
