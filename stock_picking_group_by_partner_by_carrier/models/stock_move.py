import re
from collections import namedtuple

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _assign_picking(self):
        return super(
            StockMove, self.with_context(picking_no_overwrite_partner_origin=1)
        )._assign_picking()

    def _assign_picking_post_process(self, new=False):
        res = super()._assign_picking_post_process(new=new)
        if not new:
            picking = self.mapped("picking_id")
            picking.ensure_one()
            sales = self.mapped("sale_line_id.order_id")
            for sale in sales:
                pattern = r"\b%s\b" % sale.name
                if not re.search(pattern, picking.origin):
                    picking.origin += " " + sale.name
                    picking.message_post_with_view(
                        "mail.message_origin_link",
                        values={"self": picking, "origin": sale},
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )
        return res

    def _search_picking_for_assignation(self):
        # totally reimplement this one to add a hook to change the domain
        self.ensure_one()
        picking = self.env["stock.picking"].search(
            self._domain_search_picking_for_assignation(), limit=1
        )
        return picking

    def _domain_search_picking_for_assignation(self):
        states = ("draft", "confirmed", "waiting", "partially_available", "assigned")
        if (
            not self.picking_type_id.group_pickings
            or self.group_id.sale_id.picking_policy == "one"
        ):
            # use the normal domain from the stock module
            domain = [
                ("group_id", "=", self.group_id.id),
            ]
        else:
            domain = [
                # same partner
                ("partner_id", "=", self.group_id.partner_id.id),
                # avoid mixing picking policies
                ("move_type", "=", self.group_id.move_type),
                # don't search on the procurement.group
            ]
            # same carrier only for outgoing transfers
            if self.picking_type_id.code == "outgoing":
                domain += [
                    ("carrier_id", "=", self.group_id.carrier_id.id),
                ]
            else:
                domain += [("carrier_id", "=", False)]
        domain += [
            ("location_id", "=", self.location_id.id),
            ("location_dest_id", "=", self.location_dest_id.id),
            ("picking_type_id", "=", self.picking_type_id.id),
            ("printed", "=", False),
            ("immediate_transfer", "=", False),
            ("state", "in", states),
        ]
        if self.env.context.get("picking_no_copy_if_can_group"):
            # we are in the context of the creation of a backorder:
            # don't consider the current move's picking
            domain.append(("id", "!=", self.picking_id.id))
        return domain

    def _key_assign_picking(self):
        return (
            self.sale_line_id.order_id.partner_shipping_id,
            PickingPolicy(id=self.sale_line_id.order_id.picking_policy),
        ) + super()._key_assign_picking()


# we define a named tuple because the code in module stock expects the values in
# the tuple returned by _key_assign_picking to be records with an id attribute
PickingPolicy = namedtuple("PickingPolicy", ["id"])
