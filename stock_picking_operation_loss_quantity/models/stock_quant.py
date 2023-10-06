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
