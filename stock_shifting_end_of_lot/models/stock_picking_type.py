# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    end_lot_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="End of lot destination",
        help="If defined, allows to move all quantity rest from Source Location "
        "after first customer/outgoing or internal picking "
        "with this picking type operation",
    )
    end_lot_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="End of lot picking type",
        help="If specified, used when an end of lot picking is done.",
    )
