# Copyright 2021 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _do_unreserve(self):
        """Prevent a loop between stock.move.line's unlink and this one that
        occurs because we keep the move line after freeing it for a manual lot
        assignment.
        """
        if not self:
            return True
        return super()._do_unreserve()
