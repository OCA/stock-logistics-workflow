# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import config


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_vacuum(self, company=None):
        """Overwrite method to do nothing when remaining quantity is negative."""
        if self.env.context.get("force_run_fifo_vacuum") or config["test_enable"]:
            return super()._run_fifo_vacuum(company=company)
        return
