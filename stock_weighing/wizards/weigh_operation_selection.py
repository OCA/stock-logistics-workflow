# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models


class WeightOperationSelection(models.TransientModel):
    _name = "weigh.operation.selection"
    _description = "weigh operation selection screen"

    @api.model
    def _get_weighing_start_screen_actions(self):
        """Extend to add more options to the start screen"""
        return [
            {
                "title": _("Incoming"),
                "description": _("Incoming weighing operations"),
                "icon": "fa-arrow-down",
                "method": "action_incoming_weighing_operations",
            },
            {
                "title": _("Outgoing"),
                "description": _("Outgoing weighing operations"),
                "icon": "fa-arrow-right",
                "method": "action_outgoing_weighing_operations",
            },
        ]
