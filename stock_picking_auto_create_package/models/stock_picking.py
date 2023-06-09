# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Raumschmiede Gmbh
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _auto_create_delivery_package(self) -> None:
        self.ensure_one()
        if self.picking_type_id.automatic_package_creation_mode == "single":
            self._auto_create_delivery_package_single()
        elif self.picking_type_id.automatic_package_creation_mode == "packaging":
            self._auto_create_delivery_package_per_smallest_packaging()

    @api.model
    def _auto_create_delivery_package_filter(self, move_lines):
        """
        Filter move lines that can be put in pack
        """
        return move_lines.filtered(
            lambda ml: not ml.result_package_id
            and ml.state not in ("cancel", "done")
            and ml.qty_done
        )

    def _auto_create_delivery_package_per_smallest_packaging(self) -> None:
        """
        Put each done smallest product packaging in a package
        """
        for picking in self:
            for move_line in picking.move_line_ids:
                move_line = self._auto_create_delivery_package_filter(move_line)
                if not move_line:
                    continue
                packagings = move_line.product_id.packaging_ids
                if not packagings:
                    raise UserError(
                        _(
                            "Cannot create a package for the product %s as "
                            "no product packaging is defined"
                        )
                        % move_line.product_id.display_name
                    )
                smallest_packaging = packagings.sorted("qty")[0]
                precision_digits = self.env["decimal.precision"].precision_get(
                    "Product Unit of Measure"
                )
                qty_done = move_line.qty_done
                qty = float_round(
                    qty_done / smallest_packaging.qty,
                    precision_digits=precision_digits,
                    rounding_method="HALF-UP",
                )
                if not qty.is_integer():
                    raise UserError(
                        _(
                            "The done quantity of the product %s is not "
                            "a multiple of product packaging"
                        )
                        % move_line.product_id.display_name
                    )
                for _i in range(int(qty)):
                    move_line.qty_done = smallest_packaging.qty
                    move_line.picking_id._put_in_pack(move_line)

    def _auto_create_delivery_package_single(self) -> None:
        """
        For every move that don't have a package, set a new one.
        """
        for picking in self:
            move_lines = self._auto_create_delivery_package_filter(
                picking.move_line_ids
            )
            if move_lines:
                picking._put_in_pack(move_lines)

    def _action_done(self):
        for rec in self:
            rec._auto_create_delivery_package()
        return super()._action_done()
