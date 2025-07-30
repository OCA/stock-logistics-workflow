# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MakePickingBatch(models.TransientModel):
    _name = "make.picking.batch.profile"
    _description = "Choose a batch profile wizard"

    profile_id = fields.Many2one(
        comodel_name="stock.picking.batch.creation.profile",
        ondelete="cascade",
    )

    def choose_profile(self):
        self.ensure_one()
        if self.profile_id:
            action = self.profile_id.action_launch_wizard()
        else:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "stock_picking_batch_creation.make_picking_batch_act_window"
            )
        return action
