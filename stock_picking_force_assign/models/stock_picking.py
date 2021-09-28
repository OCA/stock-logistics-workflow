# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import functools
from odoo import _, exceptions, models, tools


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_force_assign_pickings(self):
        """ Unreserve other pickings in order to reserve pickings in self """
        link_template = '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>'
        if self.state == 'waiting':
            self._unchain_waiting(link_template)
        to_unreserve = self._force_assign_find_moves()
        if to_unreserve:
            to_unreserve.mapped(lambda m: m._do_unreserve())
            self.message_post(body=_(
                'Unreserved picking(s) %s in order to assign this one'
            ) % ', '.join(to_unreserve.mapped('picking_id').mapped(
                lambda x: link_template % (x._name, x.id, x.name)
            )))
            to_unreserve.mapped('picking_id').mapped(lambda p: p.message_post(body=_(
                'Unreserved this picking in order to assign %s'
            ) % ', '.join(self.mapped(
                lambda x: link_template % (x._name, x.id, x.name)
            ))))
            # Set procure_method of the affected moves to make_to_stock to not get stuck
            to_unreserve.filtered(
                lambda x: x.procure_method == 'make_to_order'
            ).write({
                'procure_method': 'make_to_stock'
            })
        return self.action_assign()

    def _force_assign_find_moves(self):
        """ Return moves to unreserve in order to reserve pickings in self """
        result = self.env['stock.move']
        float_compare = functools.partial(
            tools.float_compare,
            precision_digits=result._fields['product_qty'].digits,
        )

        for move in self.mapped('move_lines'):
            if move.state == 'cancel':
                continue
            demand = (
                move.product_qty - move.reserved_availability -
                move.availability
            )
            if float_compare(demand, 0) <= 0:
                continue
            candidates = self.env['stock.move'].search([
                ('id', 'not in', result.ids),
                ('picking_id', 'not in', self.ids),
                ('location_id', '=', move.location_id.id),
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

    def _unchain_waiting(self, link_template):
        """Set moves to make_to_stock and unlink move_orig_ids from moves.
        Moves must be unlinked because _action_assign will otherwise only
        consider availability in linked moves, instead of considering the
        availability at the location.
        Moves that have procure_method set to make_to_order will also
        be skipped by _action_assign, so we set it to make_to_stock.
        """
        res = False
        to_unchain = self.move_lines.mapped('move_orig_ids')
        if to_unchain:
            self.message_post(body=_(
                'Decoupled operation(s) %s in order to assign this one'
            ) % ', '.join(to_unchain.mapped(
                lambda move: link_template % (move._name, move.id, move.name)
            )))
        res = self.mapped('move_lines').filtered(
            lambda move: move.procure_method == 'make_to_order'
            or move.move_orig_ids
        ).write(
            {'procure_method': 'make_to_stock', 'move_orig_ids': [(5, 0, 0)]}
        )
        return res
