# © 2016 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockInventoryLine(models.Model):

    _inherit = "stock.inventory.line"

    @api.model
    def _resolve_inventory_line(self, inventory_line):
        diff = inventory_line.theoretical_qty - inventory_line.product_qty
        allow_locked = (
            inventory_line.location_id.allow_locked
            if diff < 0
            else inventory_line.product_id.property_stock_inventory.allow_locked
        )
        return super(
            StockInventoryLine, self.with_context(allow_not_blocked=allow_locked)
        )._resolve_inventory_line(inventory_line)
