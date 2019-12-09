# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class StockProductionLot(models.Model):
    _name = "stock.production.lot"
    _inherit = ["stock.production.lot", "mail.thread"]
    _mail_post_access = "read"

    def _get_product_locked(self, product):
        """Should create locked? (including categories and parents)

        @param product: browse-record for product.product
        @return True when the category of the product or one of the parents
                demand new lots to be locked"""
        _locked = product.categ_id.lot_default_locked
        categ = product.categ_id.parent_id
        while categ and not _locked:
            _locked = categ.lot_default_locked
            categ = categ.parent_id
        return _locked

    def _get_locked_value(self):
        return self._get_product_locked(self.product_id)

    locked = fields.Boolean(
        string="Blocked", default=lambda x: x._get_locked_value(), tracking=True
    )
    product_id = fields.Many2one(track_visibility="onchange")

    @api.onchange("product_id")
    def onchange_product_id(self):
        """Instruct the client to lock/unlock a lot on product change"""
        self.locked = self._get_product_locked(self.product_id)

    @api.constrains("locked")
    def _check_lock_unlock(self):
        if not self.user_has_groups("stock_lock_lot.group_lock_lot"):
            raise exceptions.AccessError(
                _("You are not allowed to block/unblock Serial Numbers/Lots")
            )
        reserved_quants = self.env["stock.quant"].search(
            [
                ("lot_id", "in", self.filtered("locked").ids),
                ("reserved_quantity", "!=", 0.0),
            ]
        )
        if reserved_quants:
            raise exceptions.ValidationError(
                _(
                    "You are not allowed to block/unblock, there are"
                    " reserved quantities for these Serial Numbers/Lots"
                )
            )

    def button_unlock(self):
        """"Lock the lot if the permissions allow it"""
        if not self.user_has_groups("stock_lock_lot.group_lock_lot"):
            raise exceptions.AccessError(
                _("You are not allowed to unblock Serial Numbers/Lots")
            )
        return self.write({"locked": False})

    @api.model
    def create(self, vals):
        """Force the locking/unlocking, ignoring the value of 'locked'."""
        product = self.env["product.product"].browse(
            vals.get(
                "product_id",
                # Web quick-create provide in context
                self.env.context.get(
                    "product_id", self.env.context.get("default_product_id", False)
                ),
            )
        )
        vals["locked"] = self._get_product_locked(product)
        return super(StockProductionLot, self).create(vals)

    def write(self, values):
        """"Lock the lot if changing the product and locking is required"""
        if "product_id" in values:
            product = self.env["product.product"].browse(values["product_id"])
            values["locked"] = self._get_product_locked(product)
        return super(StockProductionLot, self).write(values)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "locked" in init_values:
            if self.locked:
                return self.env.ref("stock_lock_lot.mt_lock_lot")
            return self.env.ref("stock_lock_lot.mt_unlock_lot")
        return super()._track_subtype(init_values)
