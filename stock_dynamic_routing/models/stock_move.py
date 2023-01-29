# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import uuid
from collections import OrderedDict, defaultdict, namedtuple

from psycopg2 import sql

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    RoutingDetails = namedtuple(
        "RoutingDetails",
        # rule is the routing rule to apply
        # push_original_destination is used only for push rules, store the
        # original location
        "rule push_original_destination",
    )

    def _no_routing_details(self):
        return self.RoutingDetails(
            rule=self.env["stock.routing.rule"].browse(),
            push_original_destination=self.env["stock.location"].browse(),
        )

    def write(self, values):
        result = super().write(values)
        if not self.env.context.get("__applying_routing_rule") and values.get(
            "location_id"
        ):
            self.filtered(lambda r: r.state == "waiting")._chain_apply_routing()
        return result

    def _chain_apply_routing(self):
        """Apply routing on moves waiting for another one in a chained flow

        When the first move of a chain is reserved, it might trigger a change
        in the routing, we want to adapt the moves along the chained flow.
        """
        if not self:
            return
        move_routing_rules = self.env["stock.routing"]._routing_rule_for_moves(self)
        moves_with_routing_details = {}
        for move, rule in move_routing_rules.items():
            if rule:
                moves_with_routing_details[move] = self.RoutingDetails(
                    rule=rule,
                    # Never change the destination of push rules in a chain,
                    # it's done only on the first move re-routed
                    push_original_destination=self.env["stock.location"].browse(),
                )
            else:
                moves_with_routing_details[move] = self._no_routing_details()

        self._apply_routing_rule_pull(moves_with_routing_details)
        self._apply_routing_rule_push(moves_with_routing_details)

    def _action_assign(self, force_qty=False):
        if self.env.context.get("exclude_apply_dynamic_routing"):
            return super()._action_assign(force_qty=force_qty)
        else:
            # these methods will call _action_assign in a savepoint
            # and modify the routing if necessary
            moves = self._split_and_apply_routing()
            return super(StockMove, moves)._action_assign()

    def _split_and_apply_routing(self):
        """Apply routing rules

        * calls super()._action_assign() (in a savepoint) on moves not yet
          available to compute the routing rules
        * split the moves if their move lines have different source or
          destination locations and need routing
        * apply the routing rules (pull and push)

        Important: if you inherit this method to skip the routing for some
        moves, the method has to return the moves in ``self`` so they are
        assigned.
        """
        moves_routing = self._prepare_routing_pull()
        if not moves_routing:
            # When we have no routing rules, _prepare_routing_pull already
            # called _action_assign(), returning an empty recordset will
            # prevent the caller of the method to call _action_assign() again
            # on the same moves
            return self.browse()
        # apply the routing
        moves_with_routing_details = self._routing_splits(moves_routing)
        moves = self.browse(move.id for move in moves_with_routing_details)
        moves._apply_routing_rule_pull(moves_with_routing_details)
        moves._apply_routing_rule_push(moves_with_routing_details)
        return moves

    def _prepare_routing_pull(self):
        """Prepare pull routing rules for moves

        When a move has move lines with different routing rules or lines with
        routing rules and lines without, on the source/dest location, we have
        to split the moves. This method assigns the moves in a savepoint to
        compute the routing rules according the move lines.

        If no routing has to be applied, the savepoint is released.
        If routing must be applied on at least one move, the savepoint is
        rollbacked and will be called after the routing rules have been applied.

        Return the computed routing rules for the next step, which will be
        to split the moves.
        """
        if not self:
            return self

        savepoint_name = uuid.uuid1().hex
        self.env.flush_all()
        # pylint: disable=sql-injection
        self.env.cr.execute(
            sql.SQL("SAVEPOINT {}").format(sql.Identifier(savepoint_name))
        )
        super()._action_assign()

        moves_routing = self._routing_compute_rules()
        if not any(
            details.rule for routing in moves_routing.values() for details in routing
        ):
            # no routing to apply, so the reservations done by _action_assign
            # are valid and we can resolve to a normal flow
            self.env.flush_all()
            # pylint: disable=sql-injection
            self.env.cr.execute(
                sql.SQL("RELEASE SAVEPOINT {}").format(sql.Identifier(savepoint_name))
            )
            return {}

        # rollback _action_assign, it'll be called again after the routing
        self.env.clear()
        # pylint: disable=sql-injection
        self.env.cr.execute(
            sql.SQL("ROLLBACK TO SAVEPOINT {}").format(sql.Identifier(savepoint_name))
        )
        return moves_routing

    def _routing_compute_rules(self):
        """Compute routing pull rules

        Called in a savepoint (_prepare_routing_pull).
        Return a dictionary {move: {rule: reserved quantity}}. The rule for a quantity
        can be an empty recordset, which means no routing rule.
        """
        move_routing_rules = self.env["stock.routing"]._routing_rule_for_move_ids(self)
        moves_routing = {}
        no_loc = self.env["stock.location"].browse()
        for move in self:
            if move.state not in ("assigned", "partially_available"):
                continue

            # Group move lines per their rule, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            routing_rules = move_routing_rules[move]
            moves_routing[move] = {}
            # use product_qty and not product_uom_qty, because we'll use
            # this for the _split() and this method expect product_qty
            # units
            for rule, move_lines in routing_rules.items():
                if rule.method == "push":
                    dests = defaultdict(lambda: 0.0)
                    for line in move_lines:
                        dests[line.location_dest_id] += line.reserved_qty
                    for destination, qty in dests.items():
                        moves_routing[move][
                            self.RoutingDetails(rule, destination)
                        ] = qty
                else:
                    moves_routing[move][self.RoutingDetails(rule, no_loc)] = sum(
                        move_lines.mapped("reserved_qty")
                    )
            if move.state == "partially_available":
                # consider unreserved quantity as without routing, so it will
                # be split if another part of the quantity need a routing
                missing_reserved_uom_quantity = (
                    move.product_uom_qty - move.reserved_availability
                )
                missing_reserved_quantity = move.product_uom._compute_quantity(
                    missing_reserved_uom_quantity,
                    move.product_id.uom_id,
                    # this matches what is done in StockMove._action_assign()
                    rounding_method="HALF-UP",
                )
                routing_details = self._no_routing_details()
                moves_routing[move].setdefault(routing_details, 0)
                moves_routing[move][routing_details] += missing_reserved_quantity
        return moves_routing

    def _routing_splits(self, moves_routing):
        """Split moves according to routing rules

        This method splits the move in as many routing pull rules they have.

        This method returns the routing details that will be passed to
        ``_apply_routing_rule_pull`` / ``_apply_routing_rule_push`` to apply
        them.
        """
        moves_with_routing_details = {}
        for move, routing_quantities in moves_routing.items():
            moves_with_routing_details[move] = self._no_routing_details()
            for routing_details, qty in routing_quantities.items():
                # When the rule is empty, it means we have no dynamic routing
                # for the move, so we have nothing to do, it will behave as
                # normally.
                if not routing_details.rule:
                    continue
                # If we have a dynamic routing, the move may have several
                # lines with different routing (or lines with a dynamic
                # routing, lines without). We split the lines according to
                # these.
                new_move_vals = move._split(qty)
                if new_move_vals:
                    new_move = self.env["stock.move"].create(new_move_vals)
                    new_move._action_confirm(merge=False)
                else:
                    # If no split occurred keep the current move
                    new_move = move
                moves_with_routing_details[new_move] = routing_details

        return moves_with_routing_details

    def _apply_routing_rule_pull(self, routing_details):
        """Apply pull dynamic routing

        When a move has a dynamic routing configured on its location and the
        destination of the move does not match the destination of the routing,
        this method updates the move's destination and it's picking type with
        the routing ones and creates a new chained move after it.
        """
        pickings_to_check_for_emptiness = self.env["stock.picking"]
        move_ids_to_assign_per_location = defaultdict(list)
        move_ids_to_assign_nonrelocated = []
        next_moves_to_update = self.browse()
        routing_to_apply = [
            (move, detail.rule) for move, detail in routing_details.items()
        ]
        for move, routing_rule in routing_to_apply:
            if not routing_rule:
                move_ids_to_assign_nonrelocated.append(move.id)
                continue

            if routing_rule.method == "push":
                # In this case, we should not assign the move inside the
                # pull dynamic routing. The push move must first be added before the
                # initial move is assigned. Otherwise, when the destination
                # location of the initial move is changed by the push rule, the
                # putaway won't be recomputed as it is already assigned.
                continue

            if move.picking_id.picking_type_id == routing_rule.picking_type_id:
                # already correct
                move_ids_to_assign_nonrelocated.append(move.id)
                continue

            # we expect all the lines to go to the same destination for
            # pull routing rules
            original_destination = move.location_dest_id
            current_picking_type = move.picking_id.picking_type_id
            move.with_context(
                __applying_routing_rule=True
            ).location_id = routing_rule.location_src_id
            move.picking_type_id = routing_rule.picking_type_id
            dest_location = move.location_dest_id
            rule_location = routing_rule.location_dest_id
            if rule_location.is_sublocation_of(dest_location):
                # The destination of the move, is a parent of the destination
                # of the routing, goes to the correct place, but is not precise
                # enough: set the new destination to match the rule's one.
                move.location_dest_id = routing_rule.location_dest_id
                # After the reservation, the source of the dest. move will be
                # changed to match it, which may reapply a new routing rule on
                # the dest. move.
                next_moves_to_update |= move.move_dest_ids.filtered(
                    lambda r: r.state == "waiting"
                )

            elif not dest_location.is_sublocation_of(rule_location):
                # The destination of the move is unrelated (nor identical, nor
                # a parent or a child) to the routing destination: in this case
                # we have to add a routing move after to reach the original destination
                move.location_dest_id = routing_rule.location_dest_id
                # create a copy of the move with the current picking type and
                # going to its original destination: it will be assigned to the
                # same picking as the original picking of our move
                routing_move = move._insert_routing_moves(
                    current_picking_type,
                    # the source of the next move has to be the same as the
                    # destination of the current move
                    routing_rule.location_dest_id,
                    original_destination,
                )
                # Get any routing for this new move
                routing_rule = self.env["stock.routing"]._routing_rule_for_moves(
                    routing_move
                )[routing_move]
                if routing_rule:
                    # Add a new routing to apply for this new move
                    routing_to_apply.append((routing_move, routing_rule))

            pickings_to_check_for_emptiness |= move.picking_id
            move._assign_picking()
            move_ids_to_assign_per_location[move.location_id].append(move.id)

        # We have two kind of "routed" moves:
        #
        # * The ones where only the picking type / destination has been changed
        # * The ones which are assigned to a new picking and a new move is inserted
        #   to reach the destination
        #
        # For these 2 kinds, we have to call _action_assign() here because if
        # the move has been split because of partial availability, we want to
        # ensure to reserve the move which has been "routed" before the moves
        # without routing. Even if _action_assign() is called again, it will
        # not be an issue (unless a custom module does not check the current
        # state) because the move's state will be "assigned" and will be
        # excluded by the method.
        #
        # Now among these moves, some may have their source location changed by
        # the dynamic routing, for instance:
        #
        # * A move of 20 units has a source location: Stock
        # * We have this in stock:
        #   * 10 in Stock/Shelving
        #   * 10 in Stock/Reserve
        # * a routing is configured to insert a new move to do Stock/Reserve ->
        #   Stock/Shelving
        #
        # The source location for the reserve move is now Stock/Reserve. The
        # source location for the other move is still "Stock".
        # If the move to reserve the first move in "Stock" is reserved
        # first, it may take the goods in Stock/Reserve, which should be
        # reserved by the second one.
        #
        # Besides this, we have to reserve them in the same order as they were
        # initially, otherwise we may not reserve the correct quant (e.g., we
        # reserve in X in the savepoint, the dynamic routing changes the
        # picking type, and the new reservation reserves in Y because X has
        # been reserved by another move).
        #
        # To ensure moves don't reserve something which was initially reserved
        # by another move, sort the moves by their source location, from the
        # most precise to the least precise. The order of the move ids within
        # one location is preserved.
        #
        # The non routed moves are assigned at last. This allows compatibility
        # with the module stock_move_source_relocate and ensures we call
        # _action_assign on the complete set of moves
        sorted_locations = sorted(
            move_ids_to_assign_per_location, key=lambda l: l.parent_path, reverse=True
        )
        to_assign_ids = []
        for location in sorted_locations:
            to_assign_ids += move_ids_to_assign_per_location[location]
        to_assign_ids += move_ids_to_assign_nonrelocated

        self.browse(to_assign_ids).with_context(
            exclude_apply_dynamic_routing=True
        )._action_assign()

        # Update the destination moves. This might trigger a new routing on the
        # destination move.
        next_moves_to_update._routing_pull_switch_source()

        pickings_to_check_for_emptiness._dynamic_routing_handle_empty()

    def _routing_pull_switch_source(self):
        """Switch the source location of the move in place.

        When the destination of the next move has changed, we do not insert a
        new move but switch the source location of the current move.  This
        might trigger a new routing on the destination move.
        """
        for move in self:
            origmoves_by_location = OrderedDict()
            for orig_move in move.move_orig_ids:
                origmoves_by_location.setdefault(
                    orig_move.location_dest_id, move.browse()
                )
                origmoves_by_location[orig_move.location_dest_id] |= orig_move
            for location_id, orig_moves in reversed(origmoves_by_location.items()):
                qty = sum(orig_moves.mapped("product_qty"))
                split_move = move
                split_move_vals = move._split(qty)
                if split_move_vals:
                    split_move = self.create(split_move_vals)
                    split_move._action_confirm(merge=False)
                if split_move != move:
                    # No split occurs if the quantity was the same.
                    # But if it did split, detach it from the move on which
                    # we have a different routing
                    move.move_orig_ids -= orig_moves
                    split_move.move_orig_ids = orig_moves
                split_move.location_id = location_id

    def _apply_routing_rule_push(self, routing_details):
        """Apply push dynamic routing

        When a move has a dynamic routing configured on its location and the
        destination of the move does not match the destination of the routing,
        this method updates the move's destination and it's picking type with
        the routing ones and creates a new chained move after it.
        """
        pickings_to_check_for_emptiness = self.env["stock.picking"]
        for move in self:
            move_routing_details = routing_details[move]
            # At this point, we should not have lines with different source
            # locations, they have been split by _routing_splits()
            routing_rule = move_routing_details.rule
            if not routing_rule.method == "push":
                continue
            if move.picking_id.picking_type_id == routing_rule.picking_type_id:
                # the routing rule has already been applied and re-classified
                # the move in the picking type
                continue
            if move.location_dest_id == routing_rule.location_src_id:
                # the routing rule has already been applied and added a new
                # routing move after this one
                continue

            rule_location = routing_rule.location_src_id
            location = move.location_id
            if location.is_sublocation_of(rule_location):
                # The source is already correct (or more precise than the routing),
                # but we still want to classify the move in the routing's picking
                # type.
                # If the source location of the move is a child of the routing's
                # source location, we don't need to change it.
                picking = move.picking_id
                move._routing_push_switch_picking_type(routing_rule)
                pickings_to_check_for_emptiness |= picking
            else:
                # Fall here when the source location is unrelated to the
                # routing's one. Redirect the move and move line to go through
                # the routing and add a new move after it to reach the
                # destination of the routing.
                move._routing_push_insert_move(
                    routing_rule, move_routing_details.push_original_destination
                )

        pickings_to_check_for_emptiness._dynamic_routing_handle_empty()

    def _routing_push_switch_picking_type(self, routing_rule):
        """Switch the picking type of the move in place

        In this case, do not insert a new move but only change the picking type
        and reassign to a picking, so the move will be included in a transfer
        of the same type or a new transfer will be created.
        """
        self.picking_type_id = routing_rule.picking_type_id
        self._assign_picking()

    def _routing_push_insert_move(self, routing_rule, destination):
        """Change destination of the current move and add a move after it

        The routing rules are applied on the move after its destination has
        been changed in case it would need again a new move or a switch of
        picking type.

        When the new move is the one that triggered the routing in the first
        place (put-away assigned in the final Bin for instance), the initial
        destination of the original move line is kept so we are sure the move
        goes to the correct place. For all other moves, the destination is the
        one of the picking type to respect the locations chain.
        """
        self.location_dest_id = routing_rule.location_src_id
        self.move_line_ids.location_dest_id = routing_rule.location_src_id
        routing_move = self._insert_routing_moves(
            routing_rule.picking_type_id,
            routing_rule.location_src_id,
            # destination should be set only for the initial move, which
            # was the destination location of the stock.move.line generated
            # for the initial move (by a put-away rule for instance).
            destination or routing_rule.location_dest_id,
        )
        routing_move._assign_picking()
        # recursively apply chain in case we have several routing steps (since
        # the destination of the move has changed, a new push rule may apply)
        self._chain_apply_routing()

    def _insert_routing_moves(self, picking_type, location, destination):
        """Create a chained move for a routing rule"""
        self.ensure_one()
        dest_moves = self.move_dest_ids
        # Insert move between the source and destination for the new
        # operation
        routing_move_values = self._prepare_routing_move_values(
            picking_type, location, destination
        )
        routing_move = self.copy(routing_move_values)
        # force picking_type since it's a computed field from the stock_picking
        # and the copy method will assign the one from the original move
        routing_move.picking_type_id = picking_type

        # modify the chain to include the new move
        self.write(
            {"move_dest_ids": [(3, m.id) for m in dest_moves] + [(4, routing_move.id)]}
        )
        if dest_moves:
            dest_moves.write({"move_orig_ids": [(3, self.id), (4, routing_move.id)]})
        routing_move._action_confirm(merge=False)
        return routing_move

    def _prepare_routing_move_values(self, picking_type, source, destination):
        return {
            "location_id": source.id,
            "location_dest_id": destination.id,
            "state": "waiting",
            "picking_type_id": picking_type.id,
            # copy=False was missing on this field up to
            # https://github.com/odoo/odoo/commit/ecf726ae
            # to be on the safe side, force it to False
            "package_level_id": False,
        }
