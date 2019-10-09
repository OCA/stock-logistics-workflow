# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "barcodes.barcode_events_mixin"]

    _steps = {
        "select_move": {
            "label": _("Select Product"),
            "next_steps": [
                {
                    # Only if the product is managed by lots
                    "before": "_before_step_set_lot_number",
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
                    "before": "_before_step_select_move",
                    "next": "select_move",
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

    current_step = fields.Char(default="select_move", copy=False)
    current_step_descr = fields.Char(
        string="Operation",
        compute="_compute_current_step_descr",
    )
    # current move
    current_move_id = fields.Many2one(comodel_name='stock.move', copy=False)
    current_move_product_display_name = fields.Char(
        related="current_move_id.product_id.display_name", string="Product")
    current_move_product_uom_qty = fields.Float(
        related="current_move_id.product_uom_qty")
    current_move_product_uom_id = fields.Many2one(
        related="current_move_id.product_uom")
    # current move line
    current_move_line_id = fields.Many2one(
        comodel_name='stock.move.line', copy=False)
    current_move_line_lot_name = fields.Char(
        related="current_move_line_id.lot_name",
        string="Lot NumBer",
        readonly=False,
    )
    current_move_line_lot_life_date = fields.Datetime(
        related="current_move_line_id.lot_life_date",
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

    def _compute_current_step_descr(self):
        for picking in self:
            picking.current_step_descr = False
            if self.current_step:
                steps = self.get_reception_screen_steps()
                step_descr = steps[self.current_step]["label"]
                picking.current_step_descr = step_descr

    @api.depends("current_move_line_id.qty_done")
    def _compute_current_move_line_qty_status(self):
        """Based on the total quantity received, a colored disk will
        appear in green/blue/red to the user.

        - green: the qty received match the planned qty
        - red: the qty received is inferior to the planned qty
        - blue: the qty received is superior to the planned qty
        """
        for picking in self:
            move_line = picking.current_move_line_id
            move = move_line.move_id
            if not move_line.qty_done:
                picking.current_move_line_qty_status =  ""
            elif move.quantity_done > move.product_uom_qty:
                picking.current_move_line_qty_status =  "gt"
            elif move.quantity_done < move.product_uom_qty:
                picking.current_move_line_qty_status =  "lt"
            else:
                picking.current_move_line_qty_status =  "eq"

    def get_reception_screen_steps(self):
        """Aim to be overloaded to update the reception steps."""
        self.ensure_one()
        return self._steps

    def action_reception_screen_open(self):
        self.ensure_one()
        # Do not allow to process draft or processed pickings
        if self.state != "assigned":
            raise UserError(
                _("Your transfer has to be ready to receive goods."))
        # If we are in a final step
        steps = self.get_reception_screen_steps()
        if not steps[self.current_step].get("next_steps"):
            # Check if moves have been added manually in the meantime,
            # and reset the current step if necessary
            if self._before_step_select_move():
                self.current_step = "select_move"
        screen_xmlid = (
            'stock_reception_screen.stock_picking_view_form_screen'
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'views': [[self.env.ref(screen_xmlid).id, 'form']],
            'res_id': self.id,
            'target': 'fullscreen',
            'flags': {
                'headless': True,
                'form_view_initial_mode': 'edit',
                'no_breadcrumbs': True,
            },
        }

    def action_reception_screen_close(self):
        """Close the reception screen.
        It'll automatically reload the picking form.
        """
        self.ensure_one()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

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

    def on_barcode_scanned(self, barcode):
        """Dispatch the barcode event to the right method (if any)."""
        self.ensure_one()
        method = 'on_barcode_scanned_{}'.format(self.current_step)
        if hasattr(self, method):
            getattr(self, method)(barcode)

    def on_barcode_scanned_select_move(self, barcode):
        """Try to find the corresponding move based on the barcode."""
        # First find a product/move corresponding to the barcode
        move = self.move_lines.filtered(
            lambda o: o.product_id.barcode == barcode)
        # Then try on the product code
        if not move:
            move = self.move_lines.filtered(
                lambda o: o.product_id.default_code == barcode)
        # And on the name
        if not move:
            move = self.move_lines.filtered(
                lambda o: o.product_id.name == barcode)
        if not move:
            raise UserError(
                _("Product corresponding to '{}' has not been found in the "
                  "current transfer.").format(barcode))
        self.current_move_id = move
        self.process_current_select_move()

    def on_barcode_scanned_set_lot_number(self, barcode):
        """Set the lot number on a move line."""
        # First check for an existing move line corresponding to the barcode
        move_lines = self.current_move_id.move_line_ids.filtered(
            lambda o: o.lot_name == barcode)
        # Then check for an existing move line without lot name
        # otherwise create one
        if not move_lines:
            move_lines = self.current_move_id.move_line_ids.filtered(
                lambda o: not o.lot_name)
        # Finally if there is no corresponding move line we create one
        if not move_lines:
            vals = self.current_move_id._prepare_move_line_vals(quantity=0)
            move_lines = self.env['stock.move.line'].create(vals)
        self.current_move_line_id = move_lines[0]
        # Set the lot number
        self.current_move_line_id.lot_name = barcode
        self.process_current_set_lot_number()

    def process_current_select_move(self):
        self.next_step()

    def process_current_set_lot_number(self):
        if not self.current_move_line_id.lot_name:
            raise UserError(_("You have to fill the lot number."))
        self.next_step()

    def process_current_set_expiry_date(self):
        """Set the lot life date on a move line."""
        if not self.current_move_line_id.lot_life_date:
            raise UserError(_("You have to set an expiry date."))
        self.next_step()

    def process_current_set_quantity(self):
        if not self.current_move_line_qty_done:
            raise UserError(_("You have to set the received quantity."))
        self.next_step()

    def button_save_step(self):
        """Save the current step."""
        self.ensure_one()
        if not self.current_move_id and not self.current_move_line_id:
            return
        method = 'process_current_{}'.format(self.current_step)
        getattr(self, method)()

    def button_cancel_step(self):
        """Reset the current step.

        This allows the user to choose another move to process.
        """
        self.ensure_one()
        self.current_step = "select_move"
        self.current_move_id = self.current_move_line_id = False
        return True

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

    def _before_step_set_lot_number(self):
        """Decide if we have to handle lots on the current move."""
        has_tracking = self.current_move_id.has_tracking != "none"
        if not has_tracking:
            self.current_move_line_id = self.current_move_id.move_line_ids[0]
        return has_tracking

    def _before_step_select_move(self):
        """Check if there is remaining moves to process."""
        move_to_process_ok = any(
            move.quantity_done < move.product_uom_qty
            for move in self.move_lines)
        if move_to_process_ok:
            self.current_move_id = False
            self.current_move_line_id = False
        return move_to_process_ok

    def _after_step_done(self):
        """Reset the current selected move line."""
        self.current_move_id = False
        self.current_move_line_id = False
        return True
