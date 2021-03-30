# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_notification_sent = fields.Boolean(default=False)

    def _send_confirmation_email(self):
        for picking in self:
            if not picking.carrier_id:
                # If the current operation has no carrier defined, but a carrier
                # has been found in one of the chained transfers and is
                # configured to match the current operation type: force the
                # sending of the delivery notice to the carrier
                carrier = picking.get_carrier_from_chained_picking()
                related_ship = picking._get_carrier_operation_from_chained_picking()
                if (
                    carrier.integration_level == "rate_and_ship"
                    and carrier.send_delivery_notice_on == "custom"
                    and picking.picking_type_id
                    in carrier.send_delivery_notice_picking_type_ids
                ):
                    picking.carrier_id = carrier
                    picking.send_to_shipper()
                    picking.carrier_id = False
                    related_ship.delivery_notification_sent = True
            super(StockPicking, picking)._send_confirmation_email()

    def send_to_shipper(self):
        # Do not send delivery notice to the carrier if it has already been sent
        # through a previous operation (like a pack)
        self.ensure_one()
        if self.delivery_notification_sent:
            return False
        return super().send_to_shipper()

    def _get_carrier_operation_from_chained_picking(self):
        """Returns the first operation having a carrier defined in the next
        chained operations.
        """
        # FIXME: almost the same code than 'get_carrier_from_chained_picking'
        # of 'stock_helper_delivery' module, maybe to refactor/merge
        # to make 'get_carrier_from_chained_picking' returning both carrier
        # and its related picking?
        self.ensure_one()
        if self.carrier_id:
            return self

        def get_moves_dest(moves):
            return moves.move_dest_ids.filtered(
                lambda m: m.state not in ("cancel", "done")
            )

        moves_dest = get_moves_dest(self.move_lines)
        while moves_dest:
            for move_dest in moves_dest:
                if move_dest.picking_id.carrier_id:
                    return move_dest.picking_id
            moves_dest = get_moves_dest(moves_dest)
        return self.browse()

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # Override to hide the "Send to shipper" button if the delivery
        # notification has already been sent
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if result.get("name") == "stock.picking.form":
            # TODO
            # result["arch"] = self._fields_view_get_adapt_send_to_shipper_attrs(
            #     result["arch"]
            # )
            pass
        return result

    # def _fields_view_get_adapt_send_to_shipper_attrs(self, view_arch):
    #     doc = etree.XML(view_arch)
    #     # TODO
    #     return etree.tostring(doc, encoding="unicode")
