# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    reception_screen_id = fields.Many2one(
        comodel_name="stock.reception.screen",
        string=u"Reception Screen",
        copy=False,
    )

    def action_reception_screen_open(self):
        self.ensure_one()
        # Do not allow to process draft or processed pickings
        if self.state != "assigned":
            raise UserError(
                _("Your transfer has to be ready to receive goods."))
        # Create the reception screen record
        # NOTE: it is difficult to work with a transient model as we have to
        # reference the screen from the picking/move/move_line.
        if not self.reception_screen_id:
            screen_model = self.env["stock.reception.screen"]
            self.reception_screen_id = screen_model.create(
                {"picking_id": self.id})
        # If we are in a final step
        steps = self.reception_screen_id.get_reception_screen_steps()
        current_step = self.reception_screen_id.current_step
        if not steps[current_step].get("next_steps"):
            # Check if moves have been added manually in the meantime,
            # and reset the current step if necessary
            if self.reception_screen_id._before_step_select_move():
                self.reception_screen_id.current_step = "select_move"
        screen_xmlid = (
            "stock_reception_screen.stock_reception_screen_view_form"
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self.reception_screen_id._name,
            "res_id": self.reception_screen_id.id,
            "views": [[self.env.ref(screen_xmlid).id, "form"]],
            "target": "fullscreen",
            "flags": {
                "headless": True,
                "form_view_initial_mode": "edit",
                "no_breadcrumbs": True,
            },
        }
