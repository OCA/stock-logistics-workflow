# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

SEND_DELIVERY_NOTICE_ON_HELP = """
    'Ship operation' (default): send the carrier notification after the
    operation having a delivery method defined has been marked as done.

    'Defined operations': send the carrier notification after the operation
    of the chosen types has been marked as done. In this case, the
    carrier will be taken looking at the next operations until a
    carrier is found. For instance, in a pick + pack + ship setup,
    if you set the notification to be sent on the pack operation type,
    it will look at the carrier defined in the next operation (the ship in this case).

    If no notification have been sent when reaching the ship step
    (e.g. re-route goods from carrier A to B), then a fallback ensure the
    ship operation will trigger the call anyway.
"""


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    send_delivery_notice_on = fields.Selection(
        selection=[("ship", "Ship operation"), ("custom", "Defined operations")],
        string="Send delivery notice on",
        default="ship",
        help=SEND_DELIVERY_NOTICE_ON_HELP,
    )
    send_delivery_notice_picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Send delivery notice operation types",
        help="""
            When an operation of the listed type will be mark as done, the
            notification will be sent to the carrier (instead of the default
            behavior, which is whenever a delivery method is set on an
            operation).
        """,
    )
