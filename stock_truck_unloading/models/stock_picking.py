# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    manage_truck_arrival = fields.Boolean(default=False)
    is_arrived = fields.Boolean(default=False, copy=False)
    date_truck_arrival = fields.Datetime(readonly=True, copy=False)

    @api.onchange("manage_truck_arrival")
    def on_change_manage_truck_arrival(self):
        if not self.manage_truck_arrival:
            self.is_arrived = False
            self.date_truck_arrival = False

    def do_truck_arrived(self):
        for pick in self:
            if pick.manage_truck_arrival:
                pick.is_arrived = not pick.is_arrived

                if pick.is_arrived:
                    pick.date_truck_arrival = datetime.now()
                else:
                    pick.date_truck_arrival = None
            else:
                raise UserError(
                    _(
                        "You can not declare a truck arrival for a line where the option 'Manage Truck Arrival' is not checked. Line concerned by the error : "
                    )
                    + pick.name
                )
