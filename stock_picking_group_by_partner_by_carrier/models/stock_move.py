# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from collections import namedtuple

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # store the first group the move was in when created, used to keep track of
    # original group's name when creating a joint group for merged transfers,
    # and for cancellation of a sales order (to cancel only the moves related
    # to it)
    original_group_id = fields.Many2one(
        comodel_name="procurement.group", string="Original Procurement Group",
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        # Prevent merging pulled moves. This allows to cancel a SO without
        # canceling pulled moves from other SO as we ensure they are not
        # merged.
        return super()._prepare_merge_moves_distinct_fields() + ["original_group_id"]

    def _assign_picking(self):
        result = super(
            StockMove, self.with_context(picking_no_overwrite_partner_origin=1)
        )._assign_picking()
        self.picking_id._merge_procurement_groups()
        return result

    def _assign_picking_post_process(self, new=False):
        res = super()._assign_picking_post_process(new=new)
        if not new:
            self._on_assign_picking_message_link()
        return res

    def _on_assign_picking_message_link(self):
        picking = self.picking_id
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

    def _search_picking_for_assignation(self):
        # totally reimplement this one to add a hook to change the domain
        self.ensure_one()
        picking = self.env["stock.picking"].search(
            self._domain_search_picking_for_assignation(), limit=1
        )
        return picking

    def _domain_search_picking_handle_move_type(self):
        """Hook to handle the move type. Can be overloaded by other modules.
        By default the move type is taken from the procurement group.
        """
        # avoid mixing picking policies
        return [("move_type", "=", self.group_id.move_type)]

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
                # don't search on the procurement.group
            ]
            domain += self._domain_search_picking_handle_move_type()
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
