# Copyright 2026 360ERP (https://www.360erp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPackage(models.Model):
    _inherit = "stock.package"

    def action_put_in_pack(
        self, *, package_id=False, package_type_id=False, package_name=False
    ):
        # Putting packages into another (parent) package is also a put in
        # pack action: block it on transfer types that forbid packages.
        move_lines = self.move_line_ids.filtered(
            lambda line: line.state not in ("done", "cancel")
        )
        move_lines._get_put_in_pack_picking_types()._check_put_in_pack_allowed()
        return super().action_put_in_pack(
            package_id=package_id,
            package_type_id=package_type_id,
            package_name=package_name,
        )
