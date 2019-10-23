# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class StockReceptionScreen(models.Model):
    _name = "stock.reception.screen"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Stock Reception Screen"

    _step_start = "select_product"
    _steps = {
        "select_product": {
            "label": _("Select Product"),
            "next_steps": [
                {
                    "next": "select_move",
                },
            ],
        },
        "select_move": {
            "label": _("Select Move"),
            "next_steps": [
                {
                    # Only if the product is managed by lots
                    "before": "_before_select_move_to_set_lot_number",
                    "next": "set_lot_number",
                },
                {
                    "next": "set_quantity",
                },
            ],
        },
        "set_lot_number": {
            "label": _("Set Lot Number"),
            "next_steps": [{"next": "set_expiry_date"}],
        },
        "set_expiry_date": {
            "label": _("Set Expiry Date"),
            "next_steps": [{"next": "set_quantity"}],
        },
        "set_quantity": {
            "label": _("Set Quantity"),
            "next_steps": [
                {
                    # Loop until all moves are processed
                    "before": "_before_set_quantity_to_select_move",
                    "next": "select_move",
                },
                {
                    # Only if there are remaining moves to process}
                    "before": "_before_set_quantity_to_select_product",
                    "next": "select_product",
                },
                {
                    "next": "done",
                    "after": "_after_step_done",
                },
            ],
        },
        "done": {
            "label": _("Done"),
            "next_steps": [],
        },
    }

    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string=u"Transfer",
        ondelete="cascade",
        required=True,
    )
    name = fields.Char(related="picking_id.name", store=True)
    picking_origin = fields.Char(related="picking_id.origin")
    picking_partner_id = fields.Many2one(related="picking_id.partner_id")
    picking_state = fields.Selection(related="picking_id.state")
    picking_move_lines = fields.One2many(related="picking_id.move_lines")
    picking_filtered_move_lines = fields.One2many(
        comodel_name="stock.move",
        compute="_compute_picking_filtered_move_lines"
    )
    current_step = fields.Char(default="select_product", copy=False)
    current_step_descr = fields.Char(
        string="Operation",
        compute="_compute_current_step_descr",
    )
    current_filter_product = fields.Char(string="Filter product", copy=False)
    # current move
    current_move_id = fields.Many2one(comodel_name="stock.move", copy=False)
    current_move_location_dest_id = fields.Many2one(
        string="Destination",
        related="current_move_id.location_dest_id",
    )
    current_move_location_dest_id2 = fields.Many2one(
        string="Destination",
        compute="_compute_current_move_location_dest_id2"
    )
    current_move_product_display_name = fields.Char(
        related="current_move_id.product_id.display_name", string="Product")
    current_move_product_uom_qty = fields.Float(
        related="current_move_id.product_uom_qty")
    current_move_product_uom_id = fields.Many2one(
        related="current_move_id.product_uom")
    current_move_product_packaging_ids = fields.One2many(
        related="current_move_id.product_id.packaging_ids")
    # current move line
    current_move_line_id = fields.Many2one(
        comodel_name='stock.move.line', copy=False)
    current_move_line_lot_id = fields.Many2one(
        related="current_move_line_id.lot_id",
        string="Lot NumBer",
    )
    current_move_line_lot_life_date = fields.Datetime(
        related="current_move_line_id.lot_id.life_date",
        string="End of Life Date",
        readonly=False,
    )
    current_move_line_qty_done = fields.Float(
        related="current_move_line_id.qty_done",
        string="Quantity",
        readonly=False,
    )
    current_move_line_uom_id = fields.Many2one(
        related="current_move_line_id.product_uom_id",
        string="UoM",
    )
    current_move_line_qty_status = fields.Char(
        string="Qty Status",
        compute="_compute_current_move_line_qty_status")

    @api.depends("picking_id.move_lines", "current_filter_product")
    def _compute_picking_filtered_move_lines(self):
        for screen in self:
            moves = screen.picking_id.move_lines
            screen.picking_filtered_move_lines = moves
            if screen.current_filter_product:
                filter_ = screen.current_filter_product
                search_args = [
                    ("id", "in", moves.ids),
                    '|', '|',
                    ("product_id.barcode", "=", filter_),
                    ("product_id.default_code", "=", filter_),
                    ("product_id.name", "ilike", filter_),
                ]
                moves = moves.search(search_args)
                screen.picking_filtered_move_lines = moves


    @api.depends("current_step")
    def _compute_current_step_descr(self):
        for wiz in self:
            wiz.current_step_descr = False
            if self.current_step:
                steps = self.get_reception_screen_steps()
                step_descr = steps[self.current_step]["label"]
                wiz.current_step_descr = step_descr

    @api.depends("current_move_id.location_dest_id")
    def _compute_current_move_location_dest_id2(self):
        for wiz in self:
            wiz.current_move_location_dest_id2 = False
            move = wiz.current_move_id
            rule = self.env["stock.putaway.rule"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("location_in_id", "=", move.location_dest_id.id),
                ],
                limit=1
            )
            if rule:
                wiz.current_move_location_dest_id2 = rule.location_out_id

    @api.depends("current_move_line_id.qty_done")
    def _compute_current_move_line_qty_status(self):
        """Based on the total quantity received, a colored disk will
        appear in green/blue/red to the user.

        - green: the qty received match the planned qty
        - red: the qty received is inferior to the planned qty
        - blue: the qty received is superior to the planned qty
        """
        for wiz in self:
            move_line = wiz.current_move_line_id
            move = move_line.move_id
            if not move_line.qty_done:
                wiz.current_move_line_qty_status = ""
            elif move.quantity_done > move.product_uom_qty:
                wiz.current_move_line_qty_status = "gt"
            elif move.quantity_done < move.product_uom_qty:
                wiz.current_move_line_qty_status = "lt"
            else:
                wiz.current_move_line_qty_status = "eq"

    def get_reception_screen_steps(self):
        """Aim to be overloaded to update the reception steps."""
        self.ensure_one()
        return self._steps

    def action_reception_screen_close(self):
        """Close the reception screen.
        It'll automatically reload the picking form.
        """
        self.ensure_one()
        picking_url = (
            "/web/#menu_id={}&action={}&view_type=form"
            "&id={}&model={}&active_id={}".format(
                self.env.ref("stock.menu_stock_root").id,
                self.env.ref("stock.action_picking_tree_ready").id,
                self.picking_id.id,
                self.picking_id._name,
                self.picking_id.id,
            )
        )
        return {
            "type" : "ir.actions.act_url",
            "url": picking_url,
            "target": "self",
        }

    def action_reception_screen_manual_barcode(self):
        """Display a window to fill manually a barcode.

        You don't need to open this window if you use a barcode scanner
        directly on the screen.
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking.manual.barcode',
            'view_mode': 'form',
            'name': _('Barcode'),
            'target': 'new',
        }

    def next_step(self):
        """Evaluate the next step for the operator."""
        if self.current_step:
            steps = self.get_reception_screen_steps()
            step = steps[self.current_step]
            for next_step in step["next_steps"]:
                if next_step.get("before"):
                    check = getattr(self, next_step["before"])()
                    if not check:
                        # This step can be skipped
                        continue
                self.current_step = next_step["next"]
                if next_step.get("after"):
                    getattr(self, next_step["after"])()
                break

    def on_barcode_scanned(self, barcode):
        """Dispatch the barcode event to the right method (if any)."""
        self.ensure_one()
        method = 'on_barcode_scanned_{}'.format(self.current_step)
        if hasattr(self, method):
            getattr(self, method)(barcode)

    def on_barcode_scanned_select_product(self, barcode):
        """Try to find the corresponding product based on the barcode."""
        moves = self.picking_id.move_lines
        # First find a moves corresponding to the barcode
        move = moves.filtered(lambda o: o.product_id.barcode == barcode)
        # Then try on the product code
        if not move:
            move = moves.filtered(
                lambda o: o.product_id.default_code == barcode)
        # And on the name
        if not move:
            move = moves.filtered(lambda o: barcode in o.product_id.name)
        if not move:
            self.env.user.notify_warning(
                message="",
                title=_("Product '{}' not found.").format(barcode),
            )
            return
        # If there are several moves/products corresponding to the search
        # criteria we want to propose the user to choose the right one
        # by filtering them
        if len(move) > 1:
            self.current_filter_product = barcode
        # Otherwise we select directly the available move
        else:
            self.current_move_id = move
        self.process_select_product()

    def _create_remaining_move_line(self, move):
        """Create one move line with a remaining qty to process equals to the
        difference between the planned qty and the already processed qty
        of the move.
        """
        remaining_qty = move.product_uom_qty - move.quantity_done
        vals = move._prepare_move_line_vals(quantity=remaining_qty)
        return self.env['stock.move.line'].create(vals)

    def on_barcode_scanned_set_lot_number(self, barcode):
        """Set the lot number on a move line."""
        # First, check if the lot already exists
        lot_model = self.env["stock.production.lot"]
        lot = lot_model.search([("name", "=", barcode)])
        if lot:
            self.env.user.notify_info(
                message="",
                title=_("Reuse the existing lot {}.").format(barcode),
            )
        else:
            lot_vals = {
                "name": barcode,
                "product_id": self.current_move_id.product_id.id,
            }
            lot = lot_model.create(lot_vals)
        # Check for an existing move line without lot otherwise create one
        move_lines = self.current_move_id.move_line_ids
        # Finally if there is no corresponding move line we create one
        # with a remaining qty to process equals to the difference between
        # the planned qty and the already processed qty.
        if not move_lines:
            move_lines = self._create_remaining_move_line(self.current_move_id)
        self.current_move_line_id = move_lines[0]
        # Set the lot
        self.current_move_line_id.lot_id = lot
        self.process_set_lot_number()

    def process_select_product(self):
        self.next_step()
        if self.current_move_id:
            # Go to the next step automatically if only one move has been found
            self.process_select_move()

    def _before_set_quantity_to_select_move(self):
        """Check if there is remaining moves to process for the
        selected product.
        """
        if not self.current_filter_product:
            return False
        moves_to_process_ok = any(
            move.quantity_done < move.product_uom_qty
            for move in self.picking_filtered_move_lines)
        if moves_to_process_ok:
            self.current_move_id = False
            self.current_move_line_id = False
        return moves_to_process_ok


    def _before_set_quantity_to_select_product(self):
        """Check if there is remaining products/moves to process."""
        moves_to_process_ok = any(
            move.quantity_done < move.product_uom_qty
            for move in self.picking_id.move_lines)
        if moves_to_process_ok:
            self.current_filter_product = False
            self.current_move_id = False
            self.current_move_line_id = False
        return moves_to_process_ok

    def process_select_move(self):
        self.next_step()
        # Select the move line to process for the remaining qty
        # (creating one if necessary)
        move_line = self.current_move_id.move_line_ids.filtered(
            lambda o: not o.qty_done)
        if not move_line:
            move_line = self._create_remaining_move_line(self.current_move_id)
        self.current_move_line_id = move_line[0]

    def _before_select_move_to_set_lot_number(self):
        """Decide if we have to handle lots on the current move."""
        return self.current_move_id.has_tracking != "none"

    def process_set_lot_number(self):
        if not self.current_move_line_id.lot_id:
            self.env.user.notify_warning(
                message="",
                title=_("You have to fill the lot number."),
            )
            return
        self.next_step()

    def process_set_expiry_date(self):
        """Set the lot life date on a move line."""
        if not self.current_move_line_id.lot_id.life_date:
            self.env.user.notify_warning(
                message="",
                title=_("You have to set an expiry date."),
            )
            return
        self.next_step()

    def process_set_quantity(self):
        if not self.current_move_line_qty_done:
            self.env.user.notify_warning(
                message="",
                title=_("You have to set the received quantity."),
            )
            return
        self.next_step()

    def _after_step_done(self):
        """Reset the current selected move line."""
        self.current_filter_product = False
        self.current_move_id = False
        self.current_move_line_id = False
        return True

    def button_save_step(self):
        """Save the current step."""
        self.ensure_one()
        if not self.current_move_id and not self.current_move_line_id:
            return
        method = 'process_{}'.format(self.current_step)
        getattr(self, method)()

    def button_reset(self):
        """Reset the current step.

        This allows the user to choose another product to process.
        """
        self.ensure_one()
        self.current_step = self._step_start
        self.current_filter_product = False
        self.current_move_id = self.current_move_line_id = False
        return True
