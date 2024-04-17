# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WeighingWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    show_auto_lot_info = fields.Boolean(compute="_compute_show_auto_lot_info")

    @api.depends("lot_id")
    def _compute_show_auto_lot_info(self):
        self.show_auto_lot_info = False
        self.filtered(
            lambda x: (x.product_tracking != "none" and not self.lot_id)
            and x.wizard_state != "weight"
            and x.move_id.picking_type_id.auto_create_lot
            and x.product_id.auto_create_lot
        ).show_auto_lot_info = True

    def _lot_creation_constraints(self):
        """It will raise an exception only if no autlot is allowd"""
        conditions = super()._lot_creation_constraints()
        conditions += [
            not self.move_id.picking_type_id.auto_create_lot,
            not self.product_id.auto_create_lot,
        ]
        return conditions

    def _post_add_detailed_operation(self):
        """After creating a new detailed operation for lot auto-assigning"""
        self.selected_move_line_id.with_context(
            bypass_reservation_update=True
        ).set_lot_auto()
