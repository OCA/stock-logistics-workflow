# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def _lock_quants_for_loss(self):
        """
        This will set an SQL lock on selected quants in order to avoid
        further reservations during loss operation.

        TODO: Externalize this in a separate module
        """
        self.env.cr.execute(
            "SELECT id FROM stock_quant WHERE id in %s FOR UPDATE NOWAIT",
            (tuple(self.ids),),
        )

    def _apply_inventory(self):
        """When an inventory is validated, we need to cancel any remaining
        pending moves created to make the quantity no more available
        in case of loss declaration.
        """
        moves_to_cancel = self.env["stock.move"]
        if self.env.context.get("inventory_mode"):
            for quant in self:
                loss_picking_type = quant.warehouse_id.loss_type_id
                search_domain = [
                    ("reserved_uom_qty", ">", 0.0),
                    ("product_id", "=", quant.product_id.id),
                    ("package_id", "=", quant.package_id.id),
                    ("location_id", "=", quant.location_id.id),
                    ("picking_type_id", "=", loss_picking_type.id),
                    (
                        "location_dest_id",
                        "=",
                        loss_picking_type.default_location_dest_id.id,
                    ),
                    ("lot_id", "=", quant.lot_id.id),
                    ("owner_id", "=", quant.owner_id.id),
                ]
                lines = self.env["stock.move.line"].search(search_domain)
                if lines:
                    moves_to_cancel |= lines.mapped("move_id")
            if moves_to_cancel:
                moves_to_cancel._action_cancel()
        return super(StockQuant, self)._apply_inventory()
