# Copyright 2015 Francesco Apruzzese - Apulia Software srl
# Copyright 2015-2018 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_packs(self):
        self.ensure_one()
        pack_line_model = self.env['stock.picking.package.preparation.line']
        pack_lines = pack_line_model.search([
            ('move_id', '=', self.id),
            ])
        return pack_lines.mapped('package_preparation_id')

    @api.multi
    def write(self, values):
        res = super(StockMove, self).write(values)
        if not self.env.context.get('skip_update_line_ids', False):
            pack_to_update = self.env['stock.picking.package.preparation']
            for move in self:
                pack_to_update |= move.get_packs()
            if pack_to_update:
                pack_to_update._update_line_ids()
        return res

    @api.multi
    def unlink(self):
        pack_to_update = self.env['stock.picking.package.preparation']
        for move in self:
            pack_to_update |= move.get_packs()
        res = super(StockMove, self).unlink()
        if pack_to_update:
            pack_to_update._update_line_ids()
        return res
