# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

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
        """When an inventory is validated, we unlock any quants that were
        locked by to prevent further reservations due to loss declaration.
        """
        self.filtered("is_locked_by_picking").action_unlock_quant()
        return super()._apply_inventory()
