# Copyright 2021 Camptocamp SA
# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import models


class StockPackage(models.Model):
    _inherit = "stock.package"

    def _get_weight(self, picking_id=False):
        """Override standard method to use custom packaging weight logic.

        NOTE: code copied/pasted and adapted from `stock`, the product weight
        being replaced by the weight computed from the product packagings.
        """
        res = {}
        if picking_id:
            package_weights = defaultdict(float)
            children_by_dest_pack, all_pack_ids = (
                self._get_all_children_package_dest_ids()
            )
            base_weight_per_package = {
                package.id: package.package_type_id.base_weight
                for package in self.browse(list(all_pack_ids))
            }
            move_lines = self.env["stock.move.line"].search(
                [
                    ("result_package_id", "in", list(all_pack_ids)),
                    ("product_id", "!=", False),
                    ("picking_id", "=", picking_id),
                ]
            )
            for move_line in move_lines:
                package_weights[move_line.result_package_id.id] += (
                    move_line._get_weight_from_packaging()
                )
        for package in self:
            weight = package.package_type_id.base_weight or 0.0
            if picking_id:
                res[package] = weight + package_weights[package.id]
                for child_id in children_by_dest_pack.get(package, []):
                    res[package] += base_weight_per_package.get(
                        child_id, 0
                    ) + package_weights.get(child_id, 0)
            else:
                # Take the base_weight of every contained package, so we include
                # package only containing packages
                weight += sum(
                    package.all_children_package_ids.mapped(
                        lambda p: p.package_type_id.base_weight
                    )
                )
                for quant in package.contained_quant_ids:
                    weight += quant.product_id.get_total_weight_from_packaging(
                        quant.quantity
                    )
                res[package] = weight
        return res
