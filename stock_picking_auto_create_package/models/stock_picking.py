# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Raumschmiede Gmbh
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


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
            and ml.quantity
            and (not ml.move_id.picked or ml.picked)
            and (
                ml.product_id.packaging_ids
                or not ml.picking_type_id.auto_pack_requires_packaging
            )
        )

    def _auto_create_delivery_package_per_smallest_packaging(self) -> None:
        """
        Put each done smallest product packaging in a package
        """
        for picking in self:
            for move in picking.move_ids:
                move_lines = self._auto_create_delivery_package_filter(
                    move.move_line_ids
                )
                if not move_lines:
                    continue
                max_pack_qty = 1
                package_type = False
                packagings = move_lines[0].product_id.packaging_ids.filtered(
                    lambda pack: pack.qty > 0
                )
                if packagings:
                    smallest_packaging = packagings.sorted("qty")[0]
                    max_pack_qty = smallest_packaging.qty
                    package_type = smallest_packaging.package_type_id
                current_pack_lines = self.env["stock.move.line"]
                current_pack_qty = 0
                remaining_lines = list(move_lines)
                while remaining_lines:
                    current_line = remaining_lines.pop(0)
                    line_qty = current_line.quantity
                    space_in_pack = max_pack_qty - current_pack_qty
                    if line_qty <= space_in_pack:
                        current_pack_lines |= current_line
                        current_pack_qty += line_qty
                        if current_pack_qty >= max_pack_qty:
                            package = picking._put_in_pack(current_pack_lines)
                            if package_type:
                                package.package_type_id = package_type
                            current_pack_lines = self.env["stock.move.line"]
                            current_pack_qty = 0
                    else:
                        new_line = current_line._split_move_line_package_qty(
                            space_in_pack
                        )
                        current_line.quantity = space_in_pack
                        remaining_lines.insert(0, new_line)
                        current_pack_lines |= current_line
                        package = picking._put_in_pack(current_pack_lines)
                        if package_type:
                            package.package_type_id = package_type
                        current_pack_lines = self.env["stock.move.line"]
                        current_pack_qty = 0
                if current_pack_lines:
                    package = picking._put_in_pack(current_pack_lines)
                    if package_type:
                        package.package_type_id = package_type

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

    def button_auto_create_delivery_package(self):
        """
        Button to trigger the automatic package creation.
        """
        self.ensure_one()
        if self.state == "assigned":
            self._auto_create_delivery_package()
        return True

    def _action_done(self):
        for rec in self:
            rec._auto_create_delivery_package()
        return super()._action_done()
