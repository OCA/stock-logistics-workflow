# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuantPackageFastMoveWizard(models.TransientModel):
    _name = "stock.quant.package.fast.move.wizard"
    _description = "Stock Quant Package Fast Move Wizard"

    package_dest_id = fields.Many2one(
        "stock.quant.package",
        "Destination Package",
        domain="[('location_id', '=', location_dest_id)]",
    )
    location_dest_id = fields.Many2one(
        "stock.location", "Destination Location", required=True
    )
    put_in_new_package = fields.Boolean("Put in New Package")
    validate = fields.Boolean()

    def action_move(self):
        """
        Execute the package movement based on the specified parameters.
        """
        package_ids = self._context.get("active_ids")
        packages = self.env["stock.quant.package"].browse(package_ids)

        if self.put_in_new_package:
            destination_package_id = packages.create_new_package()
        else:
            destination_package_id = self.package_dest_id

        packages._move_to_location(
            self.location_dest_id,
            destination_package=destination_package_id,
            validate=self.validate,
        )

        return {"type": "ir.actions.act_window_close"}
