# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import functools
from odoo import _, exceptions, models, tools


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_force_assign_pickings(self):
        """ Unreserve other pickings in order to reserve pickings in self """
        link_template = '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>'
        to_unreserve = self._force_assign_find_moves()
        to_unreserve._do_unreserve()
        self.message_post(body=_(
            'Unreserved picking(s) %s in order to assign this one'
        ) % ', '.join(to_unreserve.mapped('picking_id').mapped(
            lambda x: link_template % (x._name, x.id, x.name)
        )))
        to_unreserve.mapped('picking_id').message_post(body=_(
            'Unreserved this picking in order to assign %s'
        ) % ', '.join(self.mapped(
            lambda x: link_template % (x._name, x.id, x.name)
        )))
        return self.action_assign()

    def _force_assign_find_moves(self):
        """ Return moves to unreserve in order to reserve pickings in self """
        location = self.mapped('location_id')
        result = self.env['stock.move']
        assert len(location) == 1, 'Pickings need to be from the same location'
        float_compare = functools.partial(
            tools.float_compare,
            precision_digits=result._fields['product_qty'].digits,
        )

        for move in self.mapped('move_lines'):
            demand = (
                move.product_qty - move.reserved_availability -
                move.availability
            )
            if float_compare(demand, 0) <= 0:
                continue
            candidates = self.env['stock.move'].search([
                ('id', 'not in', result.ids),
                ('picking_id', 'not in', self.ids),
                ('location_id', '=', location.id),
                ('product_id', '=', move.product_id.id),
                ('state', 'in', ('partially_available', 'assigned')),
            ], order='write_date asc')

            for candidate in candidates:
                if float_compare(demand, 0) > 0:
                    result += candidate
                    demand -= candidate.reserved_availability
                else:
                    break

            if float_compare(demand, 0) > 0:
                raise exceptions.UserError(
                    _('Cannot unreserve enough %s, missing quantity is %d') % (
                        move.product_id.name, demand
                    )
                )
        return result
