# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    accounting_date = fields.Date(
        copy=False,
        help="Define the date that will be used in the related account move,"
        "if the field is empty it will use the validation date.",
    )
