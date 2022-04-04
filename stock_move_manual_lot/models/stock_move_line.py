# Copyright 2021 Hunki Enterprises BV
# Copyright 2021 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    use_manual_lot_selection = fields.Boolean(
        related="picking_id.picking_type_id.use_manual_lot_selection",
    )
    manual_lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot/Serial",
        copy=False,
    )

    def _store_product_qty(self):
        """Ensure consistent values for product_qty in the database

        This module triggers (re)assignment of affected pickings within a
        x2many write on a picking's move lines. The quantity to assign depends
        on stock.move's reserved_quantity, which depends on the recompute of
        stock.move.line's `product_qty` whenever `product_uom_quantity is
        written. Because the x2many commands are processed under the scope of
        env.norecompute(), we have to take care of this ourselves.
        """
        field = self._fields["product_qty"]
        mls = self.env.field_todo(field).exists()
        for ml in mls:
            ml._write({"product_qty": ml.product_qty})
        self.env.remove_todo(field, mls)

    @api.multi
    def unlink(self):
        """Keep move lines if they are assigned a manual lot in a batch"""
        if self.env.context.get("manual_lot_move_lines"):
            to_keep = self.filtered(
                lambda ml: ml.id in self.env.context["manual_lot_move_lines"])
            to_keep.write({
                "lot_id": False,
                "manual_lot_id": False,
                "product_uom_qty": 0,
            })
            self -= to_keep
        if not self:
            return True
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        """Reuse zero quantity move line from the same move."""
        to_super = vals_list
        result = self.env["stock.move.line"]
        if self.env.context.get("manual_lot_move_lines"):
            to_super = []
            for vals in vals_list:
                if not vals.get("manual_lot_id") and vals.get("move_id"):
                    existing = self.search(
                        [("product_uom_qty", "=", 0),
                         ("move_id", "=", vals["move_id"])],
                        limit=1)
                    if existing:
                        result += existing
                        existing.with_context(
                            bypass_reservation_update=True).write(vals)
                    else:
                        to_super.append(vals)
        result += super().create(to_super)
        if not self.env.recompute:
            self._store_product_qty()
        for vals, this in zip(vals_list, result):
            this._reserve_manual_lot(vals)
        return result

    def write(self, vals):
        result = super().write(vals)
        if "product_uom_qty" in vals and not self.env.recompute:
            self._store_product_qty()
        self._reserve_manual_lot(vals)
        return result

    def _reserve_manual_lot(self, vals):
        if "manual_lot_id" not in vals and "lot_id" not in vals:
            return
        for this in self:
            if this.product_id.tracking == 'none':
                if "manual_lot_id" not in vals:
                    if this.manual_lot_id != this.lot_id:
                        this.manual_lot_id = this.lot_id
                    continue
            elif not vals.get("manual_lot_id"):
                if (not this.picking_id.picking_type_id.use_manual_lot_selection
                        and this.manual_lot_id != this.lot_id):
                    this.manual_lot_id = this.lot_id
                continue
            if this.lot_id == this.manual_lot_id:
                continue
            product_qty = this.product_qty
            product_uom_qty = this.product_uom_qty
            if this.id in self.env.context.get("manual_lot_move_lines", {}):
                product_qty = self.env.context["manual_lot_move_lines"][this.id]
                if float_compare(
                        product_qty, this.product_qty,
                        this.product_uom_id.rounding):
                    product_uom_qty = this.product_id.uom_id._compute_quantity(
                        product_qty, this.product_uom_id,
                        rounding_method="HALF-UP")

            available_qty = self.env['stock.quant']._get_available_quantity(
                this.product_id,
                this.location_id,
                lot_id=this.manual_lot_id,
                package_id=this.package_id,
                owner_id=this.owner_id,
            )
            updated_picking_ids = []
            if available_qty < product_qty:
                # free_reservation might unassign pickings, so we record which
                # ones have been changed
                self.env.cr.execute("select now() at time zone 'UTC'")
                now, = self.env.cr.fetchone()
                this._free_reservation(
                    this.product_id,
                    this.location_id,
                    product_qty - available_qty,
                    lot_id=this.manual_lot_id,
                    package_id=this.package_id,
                    owner_id=this.owner_id,
                    ml_to_ignore=self,
                )
                self.env.cr.execute(
                    'select distinct picking_id from stock_move where write_date = %s',
                    (now,),
                )
                updated_picking_ids = [row for row, in self.env.cr.fetchall() if row]

            this.lot_id = this.manual_lot_id
            if this.product_qty < product_qty:
                try:
                    self.env["stock.quant"]._update_reserved_quantity(
                        this.product_id,
                        this.location_id,
                        product_qty - this.product_qty,
                        lot_id=this.manual_lot_id,
                        package_id=this.package_id,
                        owner_id=this.owner_id,
                        # For untracked products, reservation of stock
                        # without serial is enforced.
                        strict=(not this.manual_lot_id
                                and this.product_id.tracking == 'none'),
                    )
                except UserError as ex:
                    raise UserError(
                        _("Error assigning lot %s: %s") % (
                            this.manual_lot_id.name, ex.args[0]))
                this.product_uom_qty = product_uom_qty
            if updated_picking_ids:
                # see if we can assign pickings that were unassigned above
                try:
                    with self.env.cr.savepoint():
                        self.env['stock.picking'].browse(
                            updated_picking_ids
                        ).action_assign()
                except UserError:
                    pass
