# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    lot_default_locked = fields.Boolean(
        string="Block new Serial Numbers/lots",
        help="If checked, future Serial Numbers/lots will be created blocked "
        "by default",
    )

    @api.constrains("lot_default_locked")
    def _check_category_lock_unlock(self):
        if not self.user_has_groups("stock_lock_lot.group_lock_lot"):
            raise exceptions.AccessError(
                _("You are not allowed to block/unblock Serial Numbers/Lots")
            )
