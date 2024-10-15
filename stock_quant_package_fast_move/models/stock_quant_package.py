# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def action_show_package_fast_move_wizard(self):
        """Open wizard for fast package movement."""
        return {
            "type": "ir.actions.act_window",
            "name": _("Move Packages"),
            "res_model": "stock.quant.package.fast.move.wizard",
            "target": "new",
            "view_id": self.env.ref(
                "stock_quant_package_fast_move.stock_quant_package_fast_move_wizard_view_form"
            ).id,
            "view_mode": "form",
            "context": self.env.context,
        }

    def create_batch_transfer(
        self, location, destination_package, validate, picking_type_id
    ):
        """
        Creates a new Batch Transfer and a separate picking for each package,
        adds them to the Batch Transfer, and confirms the transfer. If the "validate"
        option is enabled, the batch is also validated.

        Parameters:
        - location (recordset of stock.location): The destination location.
        - destination_package (recordset of stock.quant.package, optional):
        Optional destination package. If provided, it must belong to the specified location.
        - validate (boolean): If set to True, the created picking will be validated.
        Otherwise it will remain in the "Ready" state. Defaults to False.
        - picking_type_id (recordset of stock.picking.type):
        The picking type to be used for the transfer, as configured in settings.
        """
        # Create a batch transfer
        batch_vals = {
            "picking_type_id": picking_type_id.id,
        }
        batch_transfer = self.env["stock.picking.batch"].create(batch_vals)

        for package in self:
            # Create a picking
            picking_vals = {
                "location_id": package.location_id.id,
                "location_dest_id": location.id,
                "picking_type_id": picking_type_id.id,
            }
            picking = self.env["stock.picking"].create(picking_vals)

            # Create a package_level record
            package_level_vals = {
                "package_id": package.id,
                "package_dest_id": destination_package.id
                if destination_package
                else False,
                "picking_id": picking.id,
                "company_id": self.env.company.id,
                "location_id": package.location_id.id,
                "location_dest_id": location.id,
            }
            package_level = self.env["stock.package_level"].create(package_level_vals)
            package_level.write({"is_done": True})
            picking.write({"batch_id": batch_transfer.id})

        # Confirm the Batch Transfer
        batch_transfer.action_confirm()

        if validate:
            # Validate the Batch Transfer
            batch_transfer.action_done()

    def _move_to_location(self, location, destination_package=None, validate=False):
        """
        Move packages to a specified location.

        Parameters:
        - location (recordset of stock.location): The destination location.
        - destination_package (recordset of stock.quant.package, optional):
        Optional destination package. If provided, it must belong to the specified location.
        - validate (boolean, optional):
        If set to True, the created picking will be validated.
        Otherwise it will remain in the "Ready" state. Defaults to False.

        Returns:
        - bool: True if the move is successful.

        Raises:
        - exceptions.UserError: If the source location of the packages is different,
        If the destination location is the same as the current location
        or if the destination package does not belong to the specified location.
        """

        # Check if the location is different from the current location
        if location == self[0].location_id and not destination_package:
            raise exceptions.UserError(
                _("The destination location is the same as the current location.")
            )

        # Check if the destination package belongs to the same location
        # If the location_id is False it means that the package is new or empty
        if (
            destination_package
            and destination_package.location_id
            and destination_package.location_id != location
        ):
            raise exceptions.UserError(
                _("The destination package does not belong to the specified location.")
            )

        active_company = self.env.company
        picking_type_id = active_company.package_move_picking_type_id
        use_batch_transfers = active_company.use_batch_transfers

        if use_batch_transfers:
            self.create_batch_transfer(
                location, destination_package, validate, picking_type_id
            )
        else:
            # Create a picking
            picking_vals = {
                "location_id": self[0].location_id.id,
                "location_dest_id": location.id,
                "picking_type_id": picking_type_id.id,
            }
            picking = self.env["stock.picking"].create(picking_vals)

            for package in self:
                # Create a package_level record for each package
                package_level_vals = {
                    "package_id": package.id,
                    "package_dest_id": destination_package.id
                    if destination_package
                    else False,
                    "picking_id": picking.id,
                    "company_id": active_company.id,
                    "location_id": package.location_id.id,
                    "location_dest_id": location.id,
                }
                self.env["stock.package_level"].create(package_level_vals)

            picking.action_confirm()
            # Set the is_done flag to True for all package levels
            # associated with the created picking
            picking.package_level_ids.write({"is_done": True})
            if validate:
                # Validate the picking
                picking.button_validate()

        return True

    def create_new_package(self):
        """
        Create a new stock package.

        Returns:
        - package (recordset of stock.quant.package): The newly created package object.
        """
        package = self.env["stock.quant.package"].create({})
        return package
