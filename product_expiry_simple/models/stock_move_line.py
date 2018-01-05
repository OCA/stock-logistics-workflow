# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2018 Jarsa Sistemas (Sarai Osorio <sarai.osorio@jarsa.com.mx>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    expiry_date = fields.Date(string='Expiry Date')

    @api.model
    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        for rec in self:
            if rec.move_id.picking_type_id.use_create_lots:
                if rec.lot_id:
                    rec.lot_id.write({'expiry_date': rec.expiry_date})
