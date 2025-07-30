# Copyright (C) 2018 - TODAY, Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

DELTA_TYPES = ("day", "week", "month", "year")

class StockLot(models.Model):
    """ Inherit Stock Lot to add warranty expiration date """
    _inherit = "stock.lot"

    warranty_exp_date = fields.Date(string="Warranty Expiration Date")

    def _get_warranty_exp_date(self, start_date=None):
        if not start_date:
            start_date = fields.Date.context_today(self)
        elif hasattr(start_date, "astimezone"):
            # Datetime object, convert to date
            start_date = fields.Date.context_today(self, timestamp=start_date)
        delta_type = self.product_id.product_tmpl_id.warranty_type
        duration = self.product_id.product_tmpl_id.warranty
        if not duration or delta_type not in DELTA_TYPES:
            return False
        return start_date + relativedelta(**{f"{delta_type}s": duration})

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.warranty_exp_date = self._get_warranty_exp_date()
