# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError


def format_link(object):
    return '<a href=# data-oe-model=%s data-oe-id=%d>%s</a>' % (
        object._name, object.id, object.name)


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _action_cancel(self):

        orig_moves = self.mapped('move_orig_ids')
        all_om_canceled_or_done = all(
            move.state in ('cancel', 'done') for move in orig_moves)
        all_om_in_self = all(om in self for om in orig_moves)

        if (
                self.env.context.get('bypass_check_state') or
                all_om_canceled_or_done or
                all_om_in_self
        ):
            return super(StockMove, self.with_context(
                bypass_check_state=True))._action_cancel()
        else:
            blocking_moves = self.get_blocking_moves(orig_moves)
            blocking_objects = self.identify_blocking_objects(blocking_moves)
            error_objects = ''
            for object_type, objects in blocking_objects.items():
                error_objects += _('- %s : %s. \n' % (
                    object_type, ','.join([format_link(o) for o in objects])))
            # TODO Fix error message:
            # We'd like the links to be clickable but they are interpreted as
            # raw text
            raise UserError(
                _("Cancelation of destination move is restricted if any "
                  "previous move is not canceled or done."
                  "Original moves are not canceled or done on the following "
                  "objects : \n%s") % error_objects)

    def get_blocking_moves(self, orig_moves):
        not_canceled_or_done = orig_moves.filtered(
            lambda m: m.state not in ('cancel', 'done')
        )
        not_in_self = orig_moves.filtered(
            lambda m: m not in self
        )
        return not_in_self & not_canceled_or_done

    def identify_blocking_objects(self, blocking_moves):
        pickings = blocking_moves.mapped('picking_id')
        if pickings:
            return {'pickings': pickings}
        else:
            return {}
