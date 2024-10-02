# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_picking_backorder_link = fields.Boolean(
        help="""If enabled, then:
        If a picking is validated with less qty than expected and you don't
        create a backorder, the previous moves still to do in a backorder can be
        automatically cancelled as you "will not need" the remaining quantities.
        Also lowers the dest moves quantity.
        If you cancel a Backorder it will cancel the origin moves related as
        you "will not need" the remaining quantities.""",
    )
