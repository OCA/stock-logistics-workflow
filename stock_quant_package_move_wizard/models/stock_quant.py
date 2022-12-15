# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.misc import formatLang


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _prepare_move_to_stock_move(self, qty, dest_location, picking_id, origin=False):
        # qty is in the product's uom_id
        self.ensure_one()
        if dest_location.usage == "view":
            raise UserError(
                _("Cannot move to '%s' which is a view location.")
                % dest_location.display_name
            )
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        raise_dict = {
            "qty": formatLang(self.env, qty, digits=prec),
            "uom": self.product_id.uom_id.display_name,
            "product_name": self.product_id.display_name,
            "dest_location": dest_location.display_name,
            "quant_quantity": formatLang(self.env, self.quantity, digits=prec),
        }
        if self.location_id == dest_location:
            raise UserError(
                _(
                    "You are trying to move %(qty)s %(uom)s of a quant of product "
                    "%(product_name)s to %(dest_location)s, but it is already on "
                    "that location!"
                )
                % raise_dict
            )
        if float_compare(qty, self.quantity, precision_digits=prec) > 0:
            raise UserError(
                _(
                    "You are trying to move %(qty)s %(uom)s of a quant of product "
                    "%(product_name)s that has a quantity of "
                    "%(quant_quantity)s %(uom)s."
                )
                % raise_dict
            )
        if float_compare(self.quantity, 0, precision_digits=prec) <= 0:
            raise UserError(
                _(
                    "You are trying to move %(qty)s %(uom)s of a quant of product "
                    "%(product_name)s, but that quant has a negative quantity "
                    "(%(quant_quantity)s %(uom)s)."
                )
                % raise_dict
            )
        if float_compare(qty, 0, precision_digits=prec) <= 0:
            raise UserError(
                _(
                    "You are trying to move %(qty)s %(uom)s of a quant of product "
                    "%(product_name)s: the quantity to move must be strictly positive."
                )
                % raise_dict
            )
        product_id = self.product_id.id
        location_id = self.location_id.id
        location_dest_id = dest_location.id
        uom_id = self.product_id.uom_id.id
        vals = {
            "picking_id": picking_id,
            "name": "%s: Move to %s"
            % (self.product_id.display_name, dest_location.display_name),
            "product_id": product_id,
            "location_id": location_id,
            "location_dest_id": location_dest_id,
            "product_uom_qty": qty,
            "product_uom": uom_id,
            "origin": origin,
            "move_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product_id,
                        "product_uom_id": uom_id,
                        "qty_done": qty,
                        "location_id": location_id,
                        "location_dest_id": location_dest_id,
                        "lot_id": self.lot_id.id or False,
                    },
                )
            ],
        }
        return vals

    def _prepare_move_to_stock_picking(self, dest_location, picking_type, origin=False):
        vals = {
            "picking_type_id": picking_type.id,
            "location_dest_id": dest_location.id,
            "origin": origin,
        }
        return vals

    def move_full_quant_to(self, dest_location, picking_type=False, origin=False):
        assert dest_location
        picking_id = False
        if picking_type:
            picking_vals = self._prepare_move_to_stock_picking(
                dest_location, picking_type, origin=origin
            )
            picking_id = self.env["stock.picking"].create(picking_vals).id
        smo = self.env["stock.move"]
        stock_move_ids = []
        for quant in self:
            vals = quant._prepare_move_to_stock_move(
                quant.quantity, dest_location, picking_id, origin=origin
            )
            new_move = smo.create(vals)
            # No group has write access on stock.quant -> we need sudo()
            new_move._action_done()
            assert new_move.state == "done"
            stock_move_ids.append(new_move.id)
        return {
            "picking_id": picking_id,
            "stock_move_ids": stock_move_ids,
        }
