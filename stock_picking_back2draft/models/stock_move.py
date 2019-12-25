# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_back_to_draft(self):
        if self.filtered(lambda m: m.state != "cancel"):
            raise UserError(_("You can set to draft cancelled moves only"))
        self.write({"state": "draft"})
