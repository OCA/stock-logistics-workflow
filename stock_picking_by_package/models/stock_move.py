# opyright 2023 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        pick_packages = self.picking_id.package_level_ids.filtered(
            lambda x: x.state in ["draft"]
        )
        # Set the Package Level on the Move Line
        # This will force the reservation from that Package
        # Then reset the Package Level on Move Line, to that it stays visible
        if pick_packages:
            for pick_package in pick_packages:
                self.write({"package_level_id": pick_package.id})
                super()._action_assign(force_qty=force_qty)
                self._set_quantities_to_reservation()
                self.write({"package_level_id": None})
        # Items not found in Packages go through regular reservation
        to_assign = self.filtered(lambda x: not x.reserved_availability)
        res = super(StockMove, to_assign)._action_assign(force_qty=force_qty)
        return res

    def _do_unreserve(self):
        res = super()._do_unreserve()
        # Unreserve migh leave dangling Move Lines, because Quantity Done is set
        # Delete move lines with no reserved quantity and a Source Package set
        to_delete = self.move_line_ids.filtered(
            lambda x: x.package_id and not x.reserved_uom_qty
        )
        to_delete.unlink()
        return res
