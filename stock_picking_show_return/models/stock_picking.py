# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2018-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import first


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    returned_ids = fields.Many2many(
        comodel_name="stock.picking", compute="_compute_returned_ids",
        string="Returned pickings")
    source_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        compute="_compute_source_picking_id",
        string="Source picking")

    @api.multi
    def _compute_returned_ids(self):
        for picking in self:
            picking.returned_ids = picking.mapped(
                'move_lines.returned_move_ids.picking_id')

    @api.depends('move_lines.origin_returned_move_id')
    def _compute_source_picking_id(self):
        """Get source piking from this picking. Only one origin is possible.
        """
        for picking in self:
            picking.source_picking_id = first(picking.mapped(
                'move_lines.origin_returned_move_id.picking_id'))

    def action_show_source_picking(self):
        """ Open source picking form action """
        return self.source_picking_id.get_formview_action()

    def action_show_return_picking(self):
        """ Open return form action """
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        result['context'] = {}
        pick_ids = self.returned_ids
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result
