# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    picking_warn_option = fields.Many2one(
        comodel_name="warn.option",
    )

    @api.onchange("picking_warn_option")
    def _onchange_picking_warn_option(self):
        if self.picking_warn != "no-message" and self.picking_warn_option:
            self.picking_warn_msg = self.picking_warn_option.name
