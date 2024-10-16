# 2024 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    result_package_id = fields.Many2one(
        domain="['|', '|', ('location_id', '=', False), ('location_id', '=', location_dest_id),"
        " ('id', '=', package_id), '|', ('package_type_id.restrict_reuse', '=', False),"
        " ('disposable_used', '=', False)]"
    )
    package_id = fields.Many2one(
        domain="[('location_id', '=', location_id), '|', "
        "('package_type_id.restrict_reuse', '=', False), ('disposable_used', '=', False)]"
    )

    @api.constrains("package_id", "result_package_id")
    def _check_disposable_package_constrain(self):
        for record in self:
            record._check_disposable_packages()

    def _check_disposable_packages(self):
        if (
            self.package_id
            and self.package_id.package_type_id.restrict_reuse
            and self.package_id.package_use == "disposable"
            and self.package_id.disposable_used
        ):
            raise ValidationError(
                _(
                    "You can't reuse package %(package_name)s because it is a"
                    " disposable package that has already been used in a delivery.",
                    package_name=self.package_id.name,
                )
            )

        if (
            self.result_package_id
            and self.result_package_id.package_type_id.restrict_reuse
            and self.result_package_id.package_use == "disposable"
            and self.result_package_id.disposable_used
        ):
            raise ValidationError(
                _(
                    "You can't reuse package %(package_name)s because it is a"
                    " disposable package that has already been used in a delivery.",
                    package_name=self.result_package_id.name,
                )
            )

    def _assign_package_disposable_used(self, package_id, picking_code):
        package = self.env["stock.quant.package"].browse(package_id)
        if package.package_use == "disposable" and picking_code == "outgoing":
            package.disposable_used = True

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for vals in vals_list:
            if "result_package_id" in vals:
                picking = self.env["stock.picking"].browse(
                    vals.get("picking_id", False)
                )
                picking_code = picking.picking_type_id.code
                self._assign_package_disposable_used(
                    vals["result_package_id"], picking_code
                )
        return res

    def write(self, vals):
        res = super().write(vals)
        if "result_package_id" in vals:
            self._assign_package_disposable_used(
                vals["result_package_id"], self.picking_code
            )
        return res
