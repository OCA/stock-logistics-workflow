# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")

    def write(self, vals):
        if "owner_id" in vals:
            for pick in self:
                owner_restriction = pick.picking_type_id.owner_restriction
                if owner_restriction in ("unassigned_owner", "picking_partner"):
                    pick.move_line_ids.unlink()
        return super().write(vals)
