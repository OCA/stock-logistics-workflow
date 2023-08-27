# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def button_validate(self) -> bool or dict:
        """
        Check if the GRN is well set when validating picking
        """
        if not self.env.context.get("__no_pick_receive_note_check") and any(
            not picking.grn_id
            for picking in self.filtered(lambda p: p.picking_type_id.is_grn_mandatory)
        ):
            raise UserError(_("The picking must be linked to a Goods Received Note"))
        return super().button_validate()
