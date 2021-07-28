# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import operator
from odoo import api, fields, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    use_manual_lot_selection = fields.Boolean(
        related="picking_id.picking_type_id.use_manual_lot_selection",
    )
    manual_lot_id = fields.Many2one("stock.production.lot", "Lot/Serial")

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        for vals, this in zip(vals_list, result):
            this._reserve_manual_lot(vals)
        return result

    def write(self, vals):
        result = super().write(vals)
        self._reserve_manual_lot(vals)
        return result

    def _reserve_manual_lot(self, vals):
        if "manual_lot_id" not in vals:
            return
        for this in self:
            if this.lot_id == this.manual_lot_id:
                continue
            if not this.picking_id.picking_type_id.use_manual_lot_selection:
                continue

            available_qty = self.env['stock.quant']._get_available_quantity(
                this.product_id,
                this.location_id,
                lot_id=this.manual_lot_id,
                package_id=this.package_id,
                owner_id=this.owner_id,
            )
            updated_picking_ids = []
            if available_qty < this.product_qty:
                # free_reservation might unassign pickings, so we record which
                # ones have been changed
                self.env.cr.execute("select now() at time zone 'UTC'")
                now, = self.env.cr.fetchone()
                this._free_reservation(
                    this.product_id,
                    this.location_id,
                    this.product_qty - available_qty,
                    lot_id=this.manual_lot_id,
                    package_id=this.package_id,
                    owner_id=this.owner_id,
                    ml_to_ignore=self,
                )
                self.env.cr.execute(
                    'select id from stock_picking where write_date = %s', (now,),
                )
                updated_picking_ids = list(map(
                    operator.itemgetter(0), self.env.cr.fetchall(),
                ))

            this.lot_id = this.manual_lot_id

            if updated_picking_ids:
                # see if we can assign pickings that were unassigned above
                try:
                    with self.env.cr.savepoint():
                        self.env['stock.picking'].browse(
                            updated_picking_ids
                        ).action_assign()
                except UserError:
                    pass
