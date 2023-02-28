# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# Copyright 2023 FactorLibre - Boris Alias
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"
    # TODO: Integrate in existent field
    description_warehouse = fields.Text(string="Warehouse Description", translate=True)
