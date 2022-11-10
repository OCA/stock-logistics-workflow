from math import log10

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round


class StockPickingReallocation(models.Model):
    _name = "stock.picking.reallocation"
    _description = "Stock Picking Reallocation"

    name = fields.Char(
        string="Name", required=True, default=lambda self: self._default_name()
    )
    picking_id = fields.Many2one("stock.picking", "Initial Picking")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        copy=False,
        default="draft",
        index=True,
        readonly=True,
    )

    allocation_ids = fields.One2many(
        "stock.picking.allocation",
        "reallocation_id",
        "Allocations",
        default=lambda self: self._default_allocation_ids(),
    )

    date_1 = fields.Datetime(
        string="Date 1", required=True, default=lambda self: self._default_date()
    )
    date_2 = fields.Datetime(string="Date 2", required=True)
    date_3 = fields.Datetime(string="Date 3")
    date_4 = fields.Datetime(string="Date 4")
    date_5 = fields.Datetime(string="Date 5")

    def cancel(self):
        self.state = "cancel"

    def reallocate(self):
        self.ensure_one()
        new_moves_list = self._initialize_reallocation_moves()
        allocation_indexes = sorted(
            list(range(1, len(new_moves_list) + 2)),
            key=lambda x: getattr(self, "date_%d" % x),
        )
        base_index = allocation_indexes[0]
        base_date = getattr(self, "date_%d" % base_index)

        for allocation in self.allocation_ids:
            base_quantity = getattr(allocation, "quantity_%d" % base_index)

            move = allocation.move_id
            # We have to allocate the demand between the current move and the new moves
            demand = move.product_uom_qty
            # Excess represent the remaining quantity to allocate
            excess = demand
            rounding = move.product_uom.rounding
            precision_digits = max(0, -int(log10(rounding)))

            # We need to check that we are not lowering demand below already done
            if (
                float_compare(
                    base_quantity,
                    move.quantity_done,
                    precision_rounding=rounding,
                )
                < 0
            ):
                raise UserError(
                    _(
                        "Cannot allocate less in current picking (%s) than what "
                        "was already done for %s (%s)"
                    )
                    % (
                        float_repr(base_quantity, precision_digits=precision_digits),
                        move.product_id.name,
                        float_repr(
                            move.quantity_done, precision_digits=precision_digits
                        ),
                    )
                )

            move.date = base_date

            excess -= base_quantity

            for i, new_moves in enumerate(new_moves_list[:]):
                move_index = allocation_indexes[i + 1]
                index_date = getattr(self, "date_%d" % move_index)
                index_quantity = getattr(allocation, "quantity_%d" % move_index)

                # If this quantity is zero, there's no move to create for this date
                if float_is_zero(index_quantity, precision_rounding=rounding):
                    continue

                index_quantity = move.product_uom._compute_quantity(
                    index_quantity, move.product_id.uom_id, rounding_method="HALF-UP"
                )

                # Prepare the new move for this date
                new_move = self._allocate_new_move(move, index_quantity, index_date)
                new_moves_list[i] = new_moves | new_move

                # Update the excess
                excess -= new_move.product_uom_qty

            if not float_is_zero(excess, precision_rounding=rounding):
                difference = float_round(excess, precision_rounding=rounding)
                msg = (
                    _("There is still %s to allocate for %s.")
                    if difference > 0
                    else _("There is an excess of %s in allocation of %s.")
                )
                raise UserError(
                    msg
                    % (
                        float_repr(abs(difference), precision_digits=precision_digits),
                        move.product_id.name,
                    )
                )

        # Create the new reallocation pickings
        new_pickings = self._create_pickings_for_reallocation(new_moves_list)

        # Ensure scheduled_date is updated on the picking
        self.picking_id.scheduled_date = base_date

        # Write notifications about reallocation in the original pickings
        # and in the new ones
        self._notify_picking_of_reallocation(new_pickings)

        self.state = "done"

    def _initialize_reallocation_moves(self):
        """Return a list of moves to be reallocated according to specified dates."""
        new_moves = []
        for n in range(2, 6):
            date_n = getattr(self, "date_%d" % n)
            if date_n:
                new_moves.append(self.env["stock.move"])
            else:
                break
        return new_moves

    def _allocate_new_move(self, move, quantity, date):
        """Return the move for the requested quantity"""
        if (
            float_compare(
                quantity,
                move.product_uom_qty,
                precision_rounding=move.product_uom.rounding,
            )
            == 0
        ):
            # If we take all quantity from the original move we need to
            # reassign the original move instead of splitting
            move.date = date
            return move

        # Otherwise just split the move
        new_move_vals = move._split(quantity)
        if len(move.move_line_ids) > 1:
            raise UserError(
                _("Cannot reallocate a move with multiple move lines for product %s")
                % move.product_id.name
            )
        # Create the new move for the date
        new_move = self.env["stock.move"].create(new_move_vals)
        new_move.date = date
        new_move._action_confirm(merge=False)

        # Update move lines quantities
        if len(move.move_line_ids) == 1:
            move.move_line_ids[0].write({"product_uom_qty": move.product_uom_qty})

        return new_move

    def _create_pickings_for_reallocation(self, new_moves_list):
        """Create pickings for the reallocation according to the new moves list"""
        new_pickings = []
        # Create the new reallocation pickings
        for new_moves in new_moves_list:
            if new_moves:
                moves_date = min(new_moves.mapped("date"))
                new_picking = self._create_picking_for_reallocation(moves_date)
                new_moves.write({"picking_id": new_picking.id})
                new_moves.mapped("move_line_ids").write({"picking_id": new_picking.id})
                new_moves._action_assign()
                new_pickings.append(new_picking)
        return new_pickings

    def _create_picking_for_reallocation(self, moves_date):
        return self.picking_id.copy(
            {
                "name": "/",
                "move_lines": [],
                "move_line_ids": [],
                "backorder_id": self.picking_id.id,
                "scheduled_date": moves_date,  # We need to set it here also
                # because of the way stock.picking._compute_scheduled_date
                # works
            }
        )

    def _notify_picking_of_reallocation(self, new_pickings):
        self.picking_id.message_post(
            body=_("This picking has been reallocated into the following pickings: ")
            + ", ".join(
                [
                    '<a href="#" '
                    'data-oe-model="stock.picking" '
                    'data-oe-id="%d">%s</a>' % (new_picking.id, new_picking.name)
                    for new_picking in new_pickings
                ]
            )
        )
        for new_picking in new_pickings:
            new_picking.message_post(
                body=_("This picking has been created from the reallocation of ")
                + (
                    '<a href="#" '
                    'data-oe-model="stock.picking" '
                    'data-oe-id="%d">%s</a>'
                    % (self.picking_id.id, self.picking_id.name)
                )
            )

    def _get_current_picking(self):
        if self.picking_id:
            return self.picking_id
        picking = self._context.get("default_picking_id")
        if picking:
            return self.env["stock.picking"].browse(picking)

    def _default_name(self):
        name = "picking"
        picking = self._get_current_picking()
        if picking:
            name = picking.name
        return "Reallocation of {}".format(name)

    def _default_date(self):
        picking = self._get_current_picking()
        if picking:
            return picking.scheduled_date
        return False

    def _default_allocation_ids(self):
        picking = self._get_current_picking()
        if picking:
            return [
                (0, 0, {"move_id": move.id, "quantity_1": move.product_uom_qty})
                for move in picking.move_lines
            ]
        return False

    @api.constrains("date_1", "date_2", "date_3", "date_4", "date_5", "allocation_ids")
    def _check_non_empty_allocation_ids(self):
        for record in self:
            for i in range(1, 6):
                if getattr(self, "date_%d" % i):
                    if sum(record.allocation_ids.mapped("quantity_%d" % i)) == 0:
                        raise UserError(
                            _("You must allocate some quantity for date %d") % i
                        )

    def _onchange_date_n(self, n):
        if not getattr(self, "date_%d" % n):
            for allocation in self.allocation_ids:
                if getattr(allocation, "quantity_%d" % n):
                    setattr(allocation, "quantity_%d" % n, 0)
                    allocation._onchange_quantity_n(n)

    @api.onchange("date_3")
    def onchange_date_3(self):
        self._onchange_date_n(3)

    @api.onchange("date_4")
    def onchange_date_4(self):
        self._onchange_date_n(4)

    @api.onchange("date_5")
    def onchange_date_5(self):
        self._onchange_date_n(5)


class StockPickingAllocation(models.Model):
    _name = "stock.picking.allocation"
    _description = "Stock Picking Allocation"

    move_id = fields.Many2one("stock.move", "Move")
    product_name = fields.Char(related="move_id.product_id.name", string="Product")
    demand = fields.Float(related="move_id.product_uom_qty", string="Demand")
    edited = fields.Boolean(default=False, string="Edited")
    unchanged = fields.Boolean(default=False, string="Unchanged")

    quantity_1 = fields.Float("Date 1")
    quantity_2 = fields.Float("Date 2")
    quantity_3 = fields.Float("Date 3")
    quantity_4 = fields.Float("Date 4")
    quantity_5 = fields.Float("Date 5")

    reallocation_id = fields.Many2one("stock.picking.reallocation", "Reallocation")

    def _get_excess(self):
        return float_round(
            self.demand
            - self.quantity_1
            - self.quantity_2
            - self.quantity_3
            - self.quantity_4
            - self.quantity_5,
            precision_rounding=self.move_id.product_uom.rounding,
        )

    def _set_clamped_quantity(self, n, excess=0):
        quantity = getattr(self, "quantity_%d" % n)
        new_quantity = float_round(
            quantity + excess, precision_rounding=self.move_id.product_uom.rounding
        )

        clamped_quantity = max(min(new_quantity, self.demand), 0)
        if clamped_quantity != quantity:
            setattr(self, "quantity_%d" % n, clamped_quantity)

    def _update_quantities(self, n):
        # Reset quantity to clamped quantity if needed
        self._set_clamped_quantity(n)
        if not self.reallocation_id.date_2:
            self._set_clamped_quantity(n, self._get_excess())
            return

        for m in range(1, 6):
            if m == n:
                continue

            excess = self._get_excess()
            # If there is no excess anymore abort
            if not excess:
                return

            self._set_clamped_quantity(m, excess)

    def _onchange_quantity_n(self, n):
        self.edited = True
        self._update_quantities(n)

    @api.onchange("quantity_1")
    def onchange_quantity_1(self):
        self._onchange_quantity_n(1)

    @api.onchange("quantity_2")
    def onchange_quantity_2(self):
        self._onchange_quantity_n(2)

    @api.onchange("quantity_3")
    def onchange_quantity_3(self):
        self._onchange_quantity_n(3)

    @api.onchange("quantity_4")
    def onchange_quantity_4(self):
        self._onchange_quantity_n(4)

    @api.onchange("quantity_5")
    def onchange_quantity_5(self):
        self._onchange_quantity_n(5)
