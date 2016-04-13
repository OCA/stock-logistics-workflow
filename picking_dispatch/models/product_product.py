# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class Product(orm.Model):
    _inherit = "product.product"

    _columns = {
        'description_warehouse': fields.text('Warehouse Description',
                                             translate=True),
    }
