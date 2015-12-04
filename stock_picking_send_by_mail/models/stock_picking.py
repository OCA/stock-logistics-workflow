# -*- coding: utf-8 -*-
# © <2015> <Sandra Figueroa Varela>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv


class StockPicking(osv.osv):
    _name = "stock.picking"
    _inherit = ['mail.thread', 'stock.picking']

    def action_picking_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email,
        with the stock picking template message loaded by default
        '''
        assert len(ids) == 1, '''This option should only be used for
        a single id at a time.'''
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(
                cr, uid, 'stock', 'email_template_stock_picking')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'stock.picking',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
