# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from .res_config_settings import CONFIG_PARAM_SKU_TRAILING


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _set_auto_lot(self):
        """Assign lot_name automatically for eligible move lines."""
        pickings = self.filtered(lambda p: p.picking_type_id.auto_create_lot)
        if not pickings:
            return

        lines = pickings.mapped("move_line_ids").filtered(
            lambda x: (
                not x.lot_id
                and not x.lot_name
                and x.product_id.tracking != "none"
                and bool(x.product_id.product_tmpl_id.auto_create_lot_option)
            )
        )
        if not lines:
            return

        trailing = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(CONFIG_PARAM_SKU_TRAILING, "0")
        )

        sku_products = lines.mapped("product_id").filtered(
            lambda p: p.product_tmpl_id.auto_create_lot_option == "sku_based"
            and bool(p.default_code)
        )
        if sku_products:
            sku_products._auto_lot_sequence_sync_if_needed(trailing=trailing)

        for line in lines:
            line.lot_name = line._get_lot_sequence()

    def _action_done(self):
        self._set_auto_lot()
        return super()._action_done()

    def button_validate(self):
        self._set_auto_lot()
        return super().button_validate()
