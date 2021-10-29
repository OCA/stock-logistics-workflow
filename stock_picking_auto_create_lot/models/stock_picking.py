# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _set_auto_lot(self):
        """
        Allows to be called either by button or through code
        """
        pickings = self.filtered(lambda p: p.picking_type_id.auto_create_lot)
        lines = pickings.mapped("move_line_ids").filtered(
            lambda x: (
                not x.lot_id
                and not x.lot_name
                and x.product_id.tracking != "none"
                and x.product_id.auto_create_lot
            )
        )
        lines.set_lot_auto()

    def _action_done(self):
        self._set_auto_lot()
        return super()._action_done()

    def button_validate(self):
        self._set_auto_lot()
        return super().button_validate()
