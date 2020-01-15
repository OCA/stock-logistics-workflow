# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SuggestReturnRequestLot(models.TransientModel):
    _name = "suggest.return.request.lot"
    _description = "Suggest lots for the return request line"

    request_line_id = fields.Many2one(
        comodel_name="stock.return.request.line",
        default=lambda self: self._default_request_line_id(),
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    lot_suggestion_mode = fields.Selection(
        selection=[
            ('sum', 'Total by lot'),
            ('detail', 'Total by move'),
        ],
        default='sum',
    )
    suggested_lot = fields.Selection(
        selection="_get_suggested_lots_selection",
        string="Suggested Lots",
        help="You can return these lots",
    )
    suggested_lot_detail = fields.Selection(
        selection="_get_suggested_lots_detail_selection",
        string="Suggested Lots",
        help="You can return these lots",
    )

    @api.model
    def _default_request_line_id(self):
        if (self.env.context.get('active_model', False) !=
                'stock.return.request.line'):
            return False
        return self.env.context.get('active_id', False)

    def _get_suggested_lots_data(self):
        """Returns dict with returnable lots and qty"""
        if (
            self.env.context.get("active_model", False)
            != "stock.return.request.line"
        ):
            return (False, False)
        request_line = (
            self.request_line_id or
            self.request_line_id.browse(self.env.context.get('active_id')))
        if not request_line:
            return (False, False)
        moves = self.env["stock.move"].search(
            request_line.with_context(ignore_rr_lots=True)._get_moves_domain(),
            order=request_line.request_id.return_order
        )
        suggested_lots_totals = {}
        suggested_lots_moves = {}
        for line in moves.mapped("move_line_ids"):
            qty = line.move_id._get_lot_returnable_qty(line.lot_id)
            suggested_lots_moves[line] = qty
            suggested_lots_totals.setdefault(line.lot_id, 0)
            suggested_lots_totals[line.lot_id] += qty
        return (suggested_lots_totals, suggested_lots_moves)

    def _get_suggested_lots_selection(self):
        """Return selection tuple with lots selections and qtys"""
        suggested_lots, suggested_lots_moves = self._get_suggested_lots_data()
        if not suggested_lots:
            return
        if self.lot_suggestion_mode == 'detail':
            return [(
                ml.lot_id.id, '{} - {} - {}'.format(
                    ml.date, ml.name, suggested_lots_moves[ml])
            ) for ml in suggested_lots_moves.keys()]
        return [(
            x.id, '{} - {}'.format(x.name, suggested_lots[x]))
            for x in suggested_lots.keys()]

    def _get_suggested_lots_detail_selection(self):
        """Return selection tuple with lots selections and qtys"""
        suggested_lots, suggested_lots_moves = self._get_suggested_lots_data()
        if not suggested_lots_moves:
            return
        return [(
            ml.lot_id.id, '{} - {} - {} - {}'.format(
                ml.date, ml.lot_id.name,
                ml.reference, suggested_lots_moves[ml])
        ) for ml in suggested_lots_moves.keys()]

    def action_confirm(self):
        # TODO: In v12, selection keys are forced to strings, so the should be
        # converted to integers in order to write the into the register
        if self.lot_suggestion_mode == 'sum' and self.suggested_lot:
            self.request_line_id.lot_id = self.suggested_lot
        elif (self.lot_suggestion_mode == 'detail' and
              self.suggested_lot_detail):
            self.request_line_id.lot_id = self.suggested_lot_detail
