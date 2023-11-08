# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackageLevel(models.Model):
    _inherit = "stock.package_level"

    package_dest_id = fields.Many2one(
        "stock.quant.package",
        "Destination Package",
        compute="_compute_package_dest_id",
        inverse="_inverse_package_dest_id",
        store=True,
        readonly=False,
        check_company=True,
        domain="[('company_id', 'in', [False, company_id]), "
        "'|', ('location_id', 'child_of', parent.location_dest_id), "
        "('location_id', '=', False)]",
    )

    @api.depends("move_line_ids.result_package_id")
    def _compute_package_dest_id(self):
        """
        Compute `package_dest_id` based on `result_package_id` of related move lines.
        Set `package_dest_id` if all move lines share the same `result_package_id`.
        """
        for level in self:
            result_package_ids = level.move_line_ids.result_package_id
            level.package_dest_id = (
                result_package_ids[0] if len(result_package_ids) == 1 else False
            )

    def _inverse_package_dest_id(self):
        """
        Inverse method for `package_dest_id`. Flags the package level as done if needed and
        updates `result_package_id` on related move lines.
        """
        for level in self:
            if level.package_dest_id and not level.is_done:
                level.is_done = True

            if level.package_dest_id:
                level.move_line_ids.write(
                    {"result_package_id": level.package_dest_id.id}
                )
