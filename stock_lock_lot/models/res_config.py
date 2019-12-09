# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockConfig(models.TransientModel):
    """Add an option for strict locking"""

    _inherit = "stock.config.settings"

    stock_lock_lot_strict = fields.Boolean(
        string="Strictly forbid moves on blocked Serial Numbers/lots.",
        help="When this box is checked, users are not allowed to force the"
        "availability on blocked Serial Numbers/lots.",
    )

    def _get_parameter(self, key, default=False):
        param_obj = self.env["ir.config_parameter"]
        rec = param_obj.search([("key", "=", key)])
        return rec or default

    def _write_or_create_param(self, key, value):
        param_obj = self.env["ir.config_parameter"]
        rec = self._get_parameter(key)
        if rec:
            rec.value = str(value)
        else:
            param_obj.create({"key": key, "value": str(value)})

    @api.multi
    def get_default_parameter_stock_lock_lot_strict(self):
        def get_value(key, default=""):
            rec = self._get_parameter(key)
            return rec and rec.value and rec.value != "False" or default

        return {"stock_lock_lot_strict": get_value("stock.lock.lot.strict", False)}

    @api.multi
    def set_parameter_stock_lock_lot_strict(self):
        self._write_or_create_param("stock.lock.lot.strict", self.stock_lock_lot_strict)
