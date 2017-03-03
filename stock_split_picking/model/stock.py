# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi, Guewen Baconnier, Yannick Vaucher
#    Copyright 2013-2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
"""Adds a split button on stock picking out to enable partial picking without
   passing backorder state to done"""
from odoo import models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def do_split(self):
        reset_to_zero = self.env['stock.pack.operation']
        remove_if_any_non_zeros = self.env['stock.pack.operation']
        for picking in self:
            picking_zeros = self.env['stock.pack.operation']
            if picking.state not in ('partially_available', 'assigned'):
                raise UserError(_("You can only split pickings that are partially or fully available."))
            all_zeros = True
            for operation in picking.pack_operation_ids:
                if operation.qty_done < 0:
                    raise UserError(_('No negative quantities allowed'))
                if operation.qty_done > 0:
                    operation.write({'product_qty': operation.qty_done})
                    all_zeros = False
                else:
                    picking_zeros |= operation
            if all_zeros:
                if picking.state != 'partially_available':
                    raise UserError(_("You should partially collect the picking to show what amounts are to be left on this picking"))
                else:
                    # Since the picking is partially available, we can assume the user wants to leave the
                    # current ungathered pack operations on this picking and split the rest off. Compare with
                    # the normal picking logic which processes all operations if they are all at 0 gathered.
                    for pack_op in picking.pack_operation_ids:
                        pack_op.qty_done = pack_op.product_qty
                    reset_to_zero += picking.pack_operation_ids
            else:
                # If there are non-zero ops in the picking, then any zero-ops need to be removed,
                # because the do_transfer function assumes it will not receive any
                remove_if_any_non_zeros |= picking_zeros
        remove_if_any_non_zeros.unlink()
        result = self.with_context(do_only_split=True).do_transfer()
        # These are not backorders we've created, only splits from the original picking
        new_pickings = self.search([('backorder_id', 'in', self.ids)])
        new_pickings.write(dict(backorder_id=False))
        self.write(dict(date_done=False))  # Not actually done
        # We've changed the lines on the picking(s), so recheck availability
        self.action_assign()
        new_pickings.action_assign()
        if reset_to_zero:
            reset_to_zero.write(dict(qty_done=0))
        return result

