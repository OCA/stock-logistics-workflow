# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_gather_domain(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        domain = super()._get_gather_domain(
            product_id=product_id,
            location_id=location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

        ignored_quant_ids = self.env.context.get("_loss_ignored_quant_ids")
        if ignored_quant_ids:
            domain = expression.AND([[("id", "not in", ignored_quant_ids)], domain])

        return domain

    def _lock_quants_for_loss(self):
        """
        This will set an SQL lock on selected quants in order to avoid
        further reservations during loss operation.

        TODO: Externalize this in a separate module
        """
        if not self.ids:
            _logger.warning(
                "You try to lock quants for update in a loss operation, "
                "but without ids provided."
            )
        else:
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
        return super()._apply_inventory()
