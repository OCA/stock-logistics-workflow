# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import UserError


class PickingDispatchCreator(models.TransientModel):
    """Create a picking dispatch from stock.picking. This will take all related
    stock move from the selected picking and put them in the dispatch order."""

    _name = 'picking.dispatch.creator'
    _description = 'Picking Dispatch Creator'

    name = fields.Text(
        'Name', size=96, required=True,
        default=lambda x: x.env['ir.sequence'].next_by_code(
            'picking.dispatch'
        ),
        help='Name of the picking dispatch'
    )
    date = fields.Date(
        'Date', required=True, select=True, default=fields.Date.context_today,
        help='Date on which the picking dispatched is to be processed'
    )

    picker_id = fields.Many2one(
        'res.users', string='Picker', required=True,
        default=lambda self: self.env.user.company_id.default_picker_id,
        help='The user to which the pickings are assigned'
    )

    notes = fields.Text('Notes', help='free form remarks')

    @api.multi
    def action_create_dispatch(self):
        """
        Open the historical margin view
        """
        move_obj = self.env['stock.move']
        selected_moves = move_obj.search(
            [('picking_id', 'in', self.env.context['active_ids'])]
        )
        ok_move_ids = move_obj
        already_dispatched_ids = {}
        wrong_state_ids = {}
        for move in selected_moves:
            if move.dispatch_id:
                already_dispatched_ids.setdefault(
                    move.dispatch_id.name, []
                ).append(
                    (move.id, move.picking_id.name)
                )
            elif move.state not in ('confirmed', 'waiting', 'assigned'):
                wrong_state_ids.setdefault(
                    move.picking_id.name, {}
                ).setdefault(move.state, []).append(move.id)
            else:
                ok_move_ids |= move

        if not ok_move_ids:
            problems = [
                _("No valid stock moves found to create the dispatch!"),
                _("(Only move that are not part of a dispatch order and in "
                  "confirm, waiting or assigned state can be used)")
            ]
            for dispatch_name, mvs in already_dispatched_ids.iteritems():
                mvs.sort()

                problems.append(
                    _('Dispatch %s already covers moves %s') %
                    (dispatch_name,
                     u', '.join(['%s [%s]' % (mv, pck) for mv, pck in mvs]))
                )
            for pck, states in wrong_state_ids.iteritems():
                for state, mvs in states.iteritems():
                    problems.append(
                        _('Moves %s from picking %s are in state %s') %
                        (tuple(mvs), pck, state))
            raise UserError(u'\n'.join(problems))

        dispatch = self.env['picking.dispatch'].create({
            'name': self.name,
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
        })

        ok_move_ids.write({'dispatch_id': dispatch.id})
