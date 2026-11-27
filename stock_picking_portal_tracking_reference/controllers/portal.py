# Copyright 2026 Ariel Barreiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_picking_portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _prepare_stock_operations_portal_rendering_values(self, *args, **kwargs):
        """Map each listed operation to a sudo copy for carrier tracking rendering."""
        values = super()._prepare_stock_operations_portal_rendering_values(
            *args, **kwargs
        )
        operations = values["stock_operation_ids"]
        values["stock_operations_tracking"] = {
            operation.id: operation for operation in operations.sudo()
        }
        return values
