# Copyright 2017-2019 Akretion France (http://www.akretion.com/)
# Copyright 2018-2019 Jarsa Sistemas (Sarai Osorio <sarai.osorio@jarsa.com.mx>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    expiry_date = fields.Date(string='Expiry Date')

    @api.model
    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        for rec in self:
            if rec.move_id.picking_type_id.use_create_lots and rec.lot_id:
                rec.lot_id.write({'expiry_date': rec.expiry_date})
