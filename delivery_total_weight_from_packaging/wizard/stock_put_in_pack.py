# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPutInPack(models.TransientModel):
    _inherit = "stock.put.in.pack"

    @api.depends("package_type_id", "result_package_id")
    def _compute_shipping_weight(self):
        # NOTE: code copied/pasted and adapted from `stock_delivery`, the
        # product weight being replaced by the weight computed from the
        # product packagings.
        for wizard in self:
            # Add package weights to shipping weight, package base weight is
            # defined in package.type
            total_weight = (
                wizard.package_type_id.base_weight
                or wizard.result_package_id.package_type_id.base_weight
                or 0.0
            )
            if wizard.result_package_id:
                # If we use an existing package, we need to factor in the
                # shipping weight already set on the package.
                total_weight += wizard.result_package_id.shipping_weight
            for move_line in wizard.move_line_ids:
                total_weight += move_line._get_weight_from_packaging()
            for package in wizard.package_ids:
                total_weight += package.shipping_weight
            wizard.shipping_weight = total_weight
