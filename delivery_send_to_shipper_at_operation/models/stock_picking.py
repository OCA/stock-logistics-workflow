# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from lxml import etree

from odoo import fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_ui_view import (
    transfer_modifiers_to_node,
    transfer_node_to_modifiers,
)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_notification_sent = fields.Boolean(default=False)

    def _send_confirmation_email(self):
        for picking in self:
            picking._handle_send_to_shipper_at_operation()
            super(StockPicking, picking)._send_confirmation_email()

    def _handle_send_to_shipper_at_operation(self):
        self.ensure_one()
        if not self.carrier_id:
            # If the current operation has no carrier defined, but a carrier
            # has been found in one of the chained transfers and is
            # configured to match the current operation type: force the
            # sending of the delivery notice to the carrier
            related_ship = self.get_picking_with_carrier_from_chain()
            carrier = related_ship.carrier_id
            if (
                carrier.integration_level == "rate_and_ship"
                and carrier.send_delivery_notice_on == "custom"
                and self.picking_type_id
                in carrier.send_delivery_notice_picking_type_ids
            ):
                self.carrier_id = carrier
                self.send_to_shipper()
                # Flag the current operation and the ship one.
                # Mandatory to not execute twice 'send_to_shipper' method
                self.delivery_notification_sent = True
                related_ship.delivery_notification_sent = True

    def send_to_shipper(self):
        # Do not send delivery notice to the carrier if it has already been sent
        # through a previous operation (like a pack)
        self.ensure_one()
        if self.delivery_notification_sent:
            return False
        return super().send_to_shipper()

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # Override to hide the "Send to shipper" button if the delivery
        # notification has already been sent
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if result.get("name") == "stock.picking.form":
            result["arch"] = self._fields_view_get_adapt_send_to_shipper_attrs(
                result["arch"]
            )
        return result

    def _fields_view_get_adapt_send_to_shipper_attrs(self, view_arch):
        """Hide 'Send to Shipper' button if 'delivery_notification_sent' is True."""
        doc = etree.XML(view_arch)
        xpath_expr = "//button[@name='send_to_shipper']"
        attrs_key = "invisible"
        nodes = doc.xpath(xpath_expr)
        for field in nodes:
            attrs = safe_eval(field.attrib.get("attrs", "{}"))
            if not attrs[attrs_key]:
                continue
            invisible_domain = expression.OR(
                [attrs[attrs_key], [("delivery_notification_sent", "=", True)]]
            )
            attrs[attrs_key] = invisible_domain
            field.set("attrs", str(attrs))
            modifiers = {}
            transfer_node_to_modifiers(
                field, modifiers, self.env.context, in_tree_view=True
            )
            transfer_modifiers_to_node(modifiers, field)
        return etree.tostring(doc, encoding="unicode")
