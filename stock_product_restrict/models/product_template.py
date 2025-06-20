# Copyright 2024 Odoo Community Association (OCA)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models
from odoo.exceptions import AccessError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        if not self._check_product_create_permission():
            raise AccessError(
                "Você não tem permissão para criar produtos. Entre em contato com o administrador."
            )
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if not self._check_product_create_permission():
            raise AccessError(
                "Você não tem permissão para modificar produtos. Entre em contato com o administrador."
            )
        return super(ProductTemplate, self).write(vals)

    def unlink(self):
        if not self._check_product_create_permission():
            raise AccessError(
                "Você não tem permissão para excluir produtos. Entre em contato com o administrador."
            )
        return super(ProductTemplate, self).unlink()

    def _check_product_create_permission(self):
        """Check if current user has permission to create/modify products"""
        # Allow if user is admin
        if self.env.user._is_admin():
            return True

        # Check if user is in the product creation group
        group_create = self.env.ref(
            "stock_product_restrict.group_product_create", raise_if_not_found=False
        )
        if group_create and group_create in self.env.user.groups_id:
            return True

        return False


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        if not self._check_product_create_permission():
            raise AccessError(
                "Você não tem permissão para criar produtos. Entre em contato com o administrador."
            )
        return super(ProductProduct, self).create(vals)

    def write(self, vals):
        if not self._check_product_create_permission():
            raise AccessError(
                "Você não tem permissão para modificar produtos. Entre em contato com o administrador."
            )
        return super(ProductProduct, self).write(vals)

    def unlink(self):
        if not self._check_product_create_permission():
            raise AccessError(
                "Você não tem permissão para excluir produtos. Entre em contato com o administrador."
            )
        return super(ProductProduct, self).unlink()

    def _check_product_create_permission(self):
        """Check if current user has permission to create/modify products"""
        # Allow if user is admin
        if self.env.user._is_admin():
            return True

        # Check if user is in the product creation group
        group_create = self.env.ref(
            "stock_product_restrict.group_product_create", raise_if_not_found=False
        )
        if group_create and group_create in self.env.user.groups_id:
            return True

        return False
