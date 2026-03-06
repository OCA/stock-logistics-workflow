# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND, OR


class StockLotRemovalWizard(models.TransientModel):

    _name = "stock.lot.removal.wizard"
    _description = "Expired Lot Auto Move Wizard"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        default=lambda self: self._default_warehouse_id()
        and self.env.context.get("active_id", False),
    )

    description = fields.Html(
        compute="_compute_description",
        help="This wizard will generate removal moves for the quants of the "
        "lots to remove from the selected warehouse to the designated destination "
        "location",
    )

    removal_date = fields.Date(
        string="Expiration Date",
        default=fields.Date.context_today,
        required=True,
        help="Lots with removal date before this date will be moved.",
    )

    def _default_warehouse_id(self):
        # if the wizard is opened from a stock.warehouse record, use that warehouse
        wh_id = self.env.context.get(
            "active_model"
        ) == "stock.warehouse" and self.env.context.get("active_id", False)
        if not wh_id:
            # the wizard is opened from the menu or from another model,
            wh_id = (
                self.env["stock.warehouse"]
                .search([("company_id", "=", self.env.company.id)], limit=1)
                .id
            )
        return wh_id

    @property
    def _pick_location_dest(self):
        """Return the destination location for the expired lots."""
        self.ensure_one()
        return self.warehouse_id.lot_remove_picking_type_id.default_location_dest_id

    @property
    def _pick_location_src(self):
        """Return the origin location for the expired lots."""
        self.ensure_one()
        return self.warehouse_id.lot_remove_picking_type_id.default_location_src_id

    @api.depends("warehouse_id", "removal_date")
    def _compute_description(self):
        """Compute the description based on the warehouse settings."""
        qweb_date = self.env["ir.qweb.field.date"]
        for record in self:
            warehouse = record.warehouse_id
            if not warehouse:
                record.description = ""
                continue

            field_descr = (
                self.env["stock.lot"]
                ._fields["removal_date"]
                ._description_string(self.env)
            )
            origin_locations = ", ".join(
                warehouse.lot_remove_orig_location_ids.mapped("display_name")
            )
            desc = _(
                "<p>This wizard will plan moves to remove lots from "
                "locations <b>%(orig_locations)s</b> to <b>%(dest_location)s</b></p>"
                "<p>Removed lots are those with <b>'%(field_descr)s' before "
                "%(removal_date)s</b>.</p>",
                orig_locations=origin_locations,
                dest_location=self._pick_location_dest.display_name,
                field_descr=field_descr,
                removal_date=qweb_date.value_to_html(record.removal_date, {}),
            )
            record.description = desc

    def button_action_run(self):
        """Run the wizard and return the action to view the created picking."""
        self.ensure_one()
        picking = self.action_run()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all",
        )
        if picking:
            action["domain"] = [("id", "in", picking.ids)]
        return action

    def _ensure_configuration(self):
        """Ensure that the warehouse is configured for expired lot removal."""
        if (
            not self.warehouse_id.lot_remove_orig_location_ids
            or not self.warehouse_id.lot_remove_picking_type_id
        ):
            raise ValidationError(
                _(
                    "Warehouse '%(wh_name)s' is not properly configured for expired "
                    "lot removal. Please set the origin locations "
                    "and the picking type.",
                    wh_name=self.warehouse_id.display_name,
                )
            )

    def action_run(self):
        """Main entry point to find expired lots and create a transfer picking.
        This method will:
        1. Find expired quants based on the removal date.
        2. Unreserve moves that are linked to these quants.
        3. Create a transfer picking to move these quants to the destination location.
        4. Reassign the moves that were unreserved.

        return: The created picking record.
        """
        self.ensure_one()
        self._ensure_configuration()

        quants = self._get_expired_quants()
        if not quants:
            return

        reserved_moves = self._get_moves_to_unreserve(quants)
        reserved_moves = self._remove_qty_done(reserved_moves, quants)
        if reserved_moves:
            self._unreserve_moves(reserved_moves)

        picking = self._create_transfer_expired_lots(quants, reserved_moves)
        moves = picking.move_ids
        if picking:
            picking.action_confirm()
            picking.action_assign()
        if reserved_moves:
            self._reassign_moves(reserved_moves)
        return moves.mapped("picking_id")

    def _get_quants_to_remove_location_domain(self):
        """Build the domain to get the locations to search for expired quants."""
        domain = [
            ("usage", "=", "internal"),
            ("warehouse_id", "=", self.warehouse_id.id),
            ("scrap_location", "=", False),
        ]
        locations_domain = OR(
            [("location_id", "child_of", loc.id)]
            for loc in self.warehouse_id.lot_remove_orig_location_ids
        )
        return AND([domain, locations_domain])

    def _get_quants_to_remove_quant_domain(self):
        """Build the domain to find expired quants. The domain will not
        include criteria on location.

        An additional criteria will be added to the sql query to filter
        """
        return [
            ("removal_date", "<", self.removal_date),
            ("quantity", ">", 0),
            ("package_id", "=", False),  # Exclude quants in packages
        ]

    def _get_expired_quants(self):
        Quant = self.env["stock.quant"]
        Location = self.env["stock.location"]
        quant_query = Quant._search(self._get_quants_to_remove_quant_domain())

        location_query = Location._search(self._get_quants_to_remove_location_domain())
        # join the the location query to the quant
        _table, query, params = location_query.get_sql()
        quant_query.add_table(Location._table)
        quant_query.add_where(query, params)
        quant_query.add_where('("stock_location"."id" = "stock_quant"."location_id")')

        return Quant.browse(quant_query)

    def _get_move_to_unreserve_picking_type_domain(self, quants):
        """Build the domain to apply to picking type to find moves to unreserve.

        This domain is joined to the move and oicking domains to find
        moves to unreserve into the _get_moves_to_unreserve method.
        """
        return [
            ("disable_unassign_lots_to_remove", "=", False),
        ]

    def _get_move_to_unreserve_picking_domain(self, quants):
        """Build the domain to apply to pickings to find moves to unreserve.

        This domain is joined to the move line and move domains to find
        moves to unreserve into the _get_moves_to_unreserve method.
        """
        return [
            ("state", "in", ("assigned", "confirmed")),
            ("picking_type_id", "!=", self.warehouse_id.lot_remove_picking_type_id.id),
            ("printed", "=", False),
        ]

    def _get_move_to_unreserve_move_line_domain(self, quants):
        """Build the domain to apply to move lines to find moves to unreserve.

        This domain is joined to the move and picking domains to find
        moves to unreserve into the _get_moves_to_unreserve method.

        A new

        """
        domain = [
            ("lot_id", "in", quants.mapped("lot_id").ids),
            ("reserved_uom_qty", ">", 0),
            ("state", "not in", ("cancel", "done")),
        ]
        locations_domain = OR(
            [("location_id", "child_of", loc.id)]
            for loc in self.warehouse_id.lot_remove_orig_location_ids
        )
        return AND([domain, locations_domain])

    def _get_move_to_unreserve_move_domain(self, quants):
        """Build the domain to apply to moves to find moves to unreserve.

        This domain is joined to the move line and picking domains to find
        moves to unreserve into the _get_moves_to_unreserve method.

        """
        return [
            ("state", "in", ("assigned", "confirmed")),
        ]

    def _get_moves_to_unreserve(self, quants):
        """Get the moves to unreserve based on the quants."""
        Move = self.env["stock.move"]
        MoveLine = self.env["stock.move.line"]
        Picking = self.env["stock.picking"]

        move_domain = self._get_move_to_unreserve_move_domain(quants)
        move_line_domain = self._get_move_to_unreserve_move_line_domain(quants)
        picking_domain = self._get_move_to_unreserve_picking_domain(quants)
        picking_type_domain = self._get_move_to_unreserve_picking_type_domain(quants)

        move_query = Move._search(move_domain)
        move_line_query = MoveLine._search(move_line_domain)
        picking_query = Picking._search(picking_domain)
        picking_type_query = self.env["stock.picking.type"]._search(picking_type_domain)

        # Join the move line query to the move query
        _table, query, params = move_line_query.get_sql()
        move_query.add_table(MoveLine._table)
        move_query.add_where(query, params)
        move_query.add_where('("stock_move_line"."move_id" = "stock_move"."id")')

        # Join the picking query to the move query
        _table, query, params = picking_query.get_sql()
        move_query.add_table(Picking._table)
        move_query.add_where(query, params)
        move_query.add_where('("stock_picking"."id" = "stock_move"."picking_id")')

        # Join the picking type query to the move query
        _table, query, params = picking_type_query.get_sql()
        move_query.add_table("stock_picking_type")
        move_query.add_where(query, params)
        move_query.add_where(
            '("stock_picking"."picking_type_id" = "stock_picking_type"."id")'
        )
        move_query.add_where(
            '("stock_move"."picking_type_id" = "stock_picking_type"."id")'
        )
        return Move.browse(move_query)

    def _remove_qty_done(self, moves, quants):
        """For move linked to move lines with qty_done > 0, split
        the move lines to isolate the qty_done > 0
        into a new move.
        """
        for move in moves:
            move_lines = move.move_line_ids.filtered(lambda ml: ml.qty_done > 0)
            if not move_lines:
                continue
            # Split the move lines with qty_done > 0
            if move_lines:
                qty_done = sum(move_lines.mapped("qty_done"))
                # for each move line we must update the reserved quantity to
                # reflect the qty_done
                for move_line in move_lines:
                    move_line.reserved_uom_qty = move_line.qty_done
                qty_done_move = self.env["stock.move"].create(move._split(qty_done))
                move_lines.write({"move_id": qty_done_move.id})
        return moves

    def _unreserve_moves(self, moves):
        moves._do_unreserve()

    def _get_transfer_move_vals(self, quant):
        """Get the values to create a transfer move for a quant."""
        name = _(
            "Move expired lot %(lot_name)s (%(product_name)s)",
            lot_name=quant.lot_id.name,
            product_name=quant.product_id.name,
        )
        return {
            "name": name,
            "product_id": quant.product_id.id,
            "product_uom": quant.product_uom_id.id,
            "product_uom_qty": quant.quantity - quant.reserved_quantity,
            "location_id": quant.location_id.id,
            "location_dest_id": self._pick_location_dest.id,
            "lot_ids": [Command.set(quant.lot_id.ids)],
        }

    def get_transfer_picking_vals(self, quants, moves_unreserved):
        """Get the values to create a transfer picking for a quant."""
        return {
            "picking_type_id": self.warehouse_id.lot_remove_picking_type_id.id,
            "location_id": self._pick_location_src.id,
            "location_dest_id": self._pick_location_dest.id,
            "origin": _("Auto Expired Lot Move"),
            "move_ids": [
                Command.create(self._get_transfer_move_vals(quant)) for quant in quants
            ],
        }

    def _create_transfer_expired_lots(self, quants, moves_unreserved):
        """Create transfer of expired lots."""
        quants = quants.filtered(lambda q: q.quantity - q.reserved_quantity > 0)
        if not quants:
            return self.env["stock.picking"]
        return self.env["stock.picking"].create(
            self.get_transfer_picking_vals(quants, moves_unreserved)
        )

    def _reassign_moves(self, moves):
        """Try to reassign moves that were unreserved."""
        moves.picking_id.action_assign()
