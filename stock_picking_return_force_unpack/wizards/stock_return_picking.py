# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_return(self):
        new_picking = super()._create_return()
        self._force_unpack_if_needed(new_picking)
        return new_picking

    def _create_exchange(self, return_picking):
        exchange_picking = super()._create_exchange(return_picking)
        self._force_unpack_if_needed(exchange_picking)
        return exchange_picking

    def _force_unpack_if_needed(self, picking):
        """Strip the destination package assignment from a return/exchange
        picking's moves.

        `result_package_id` is what Odoo would put the returned quantity
        back into on arrival; clearing it lands the goods in their
        destination location unpackaged instead of recreating the original
        container there, which is what fails validation when the original
        package still holds the non-returned remainder at the customer.

        `package_id` (the source package) is deliberately left untouched: it
        is what lets Odoo resolve the move against the exact quant being
        returned (package + lot/serial). Clearing it too would leave that
        quant untouched inside the still-existing package at the customer
        location while depositing an unrelated, unpackaged quant at the
        destination -- for serial-tracked products this produces two quants
        for the same serial number instead of moving the one that exists.
        """
        if picking.picking_type_id.force_unpack_on_return:
            picking.move_line_ids.write({"result_package_id": False})
