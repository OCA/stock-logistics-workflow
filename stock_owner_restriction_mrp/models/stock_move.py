# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_owner_for_assign(self):
        """The raw material of a manufacturing order takes the partner its order
        ends up delivering to.

        There is no picking to read a partner from, so the base module resolved
        to nothing. Under *Picking partner* that does not mean "unrestricted",
        it means "restricted to nobody": the reservation looks for stock owned
        by no one in particular and, where the goods on hand belong to partners,
        finds none. The order reserves nothing and manufacturing stops with
        nothing on screen explaining why.

        A manufacturing order has no partner of its own to offer either
        (`mrp.production` carries no `partner_id` or `owner_id`, only the
        responsible `user_id`), so the answer comes from the same chain the base
        method already follows for the finished product. Manufacturing to stock
        chains to nothing and keeps resolving to no partner, which is the right
        answer for it.
        """
        partner = super()._get_owner_for_assign()
        if not partner and self.raw_material_production_id:
            production = self.raw_material_production_id
            partner = production.move_finished_ids.move_dest_ids.picking_id.owner_id
        return partner

    def _get_production_components_owner(self, restriction):
        """The partner every consumed component of this production belongs to.

        Returns an empty partner when the production consumed nothing owned,
        which is the ordinary case, and what each restriction means here is not
        the same:

        - *Unassigned owner* says no component may belong to anybody. The
          reservation should have made that impossible, so an owned component
          points at something that went around it — the `_set_quantity_done`
          path, a hand-picked quant — and blessing it would quietly hand the
          finished product over to a partner nobody decided to give it to.
          Refused.
        - *Picking partner* says every component comes from that one partner.
          Finding company stock among them is equally anomalous, and there is no
          way to say what came out belongs partly to each. Refused.
        - *Picking partner or unassigned owner* is the one mode where mixing is
          the designed behaviour: it reserves from the partner and completes
          with unowned stock. So a mix is expected, and what comes out goes to
          the partner — the alternative being to leave their share of it at zero
          cost, which is the very problem this module exists to stop.

        Two different partners have no answer under any of them.
        """
        self.ensure_one()
        production = self.production_id
        lines = production.move_raw_ids.move_line_ids.filtered("quantity")
        owners = lines.owner_id
        if not owners:
            return owners
        if restriction == "unassigned_owner":
            raise UserError(
                _(
                    "%(production)s is set to consume unowned stock only, but "
                    "these components belong to %(owners)s. Free the stock or "
                    "change the operation type restriction before validating.",
                    production=production.display_name,
                    owners=", ".join(owners.mapped("display_name")),
                )
            )
        if len(owners) > 1:
            raise UserError(
                _(
                    "%(production)s consumes components of more than one owner: "
                    "%(owners)s. What comes out of it cannot belong partly to "
                    "each, so split it into one manufacturing order per owner.",
                    production=production.display_name,
                    owners=", ".join(owners.mapped("display_name")),
                )
            )
        if restriction == "picking_partner" and any(
            not line.owner_id for line in lines
        ):
            raise UserError(
                _(
                    "%(production)s mixes components of %(owner)s with the "
                    "company's own, and its operation type restricts it to the "
                    "partner's stock. What comes out of it cannot belong partly "
                    "to each: split it, or allow unassigned stock on the "
                    "operation type.",
                    production=production.display_name,
                    owner=owners.display_name,
                )
            )
        return owners

    def _set_owner_from_production_components(self):
        """What is made out of somebody else's goods belongs to them too.

        Odoo declines to value the consumption of a partner's goods —
        `stock.move._is_out()` skips any line carrying an `owner_id` — and then
        values the finished product anyway, at whatever the components cost,
        which is now nothing. The order books stock out of thin air, the average
        cost of the product collapses and everything made from it afterwards
        inherits the collapse.

        Naming the owner on the way out is what stops it at the source: the move
        produces no valuation layer at all, not even a zero-cost one. Both
        fields are needed and they do different things: `owner_id` on the lines
        keeps the quantity out of the valuation layer
        (`stock_account/models/stock_move.py`, which filters
        `_get_in_move_lines` by `_should_exclude_for_valuation`), while
        `restrict_partner_id` on the move keeps it out of the journal entries
        (`_account_entry_move`). Writing only one of them leaves the job half
        done. This is what `stock.picking._action_done` already does for a
        picking with an owner.
        """
        for move in self.filtered("production_id"):
            restriction = move.production_id.picking_type_id.owner_restriction
            if not restriction or restriction == "standard_behavior":
                continue
            owner = move._get_production_components_owner(restriction)
            if not owner:
                continue
            move.restrict_partner_id = owner
            move.move_line_ids.owner_id = owner

    def _action_done(self, cancel_backorder=False):
        # The raw material is validated before the finished product in
        # `mrp.production._post_inventory`, so by now the consumed lines already
        # carry their definitive owner.
        self._set_owner_from_production_components()
        return super()._action_done(cancel_backorder=cancel_backorder)
