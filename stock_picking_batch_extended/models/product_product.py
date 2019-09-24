# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"
    # TODO: Integrate in existent field
    description_warehouse = fields.Text('Warehouse Description',
                                        translate=True)
