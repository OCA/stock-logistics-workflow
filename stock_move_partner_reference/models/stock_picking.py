# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    partner_reference = fields.Char(
        compute='_compute_partner_reference',
        search='_search_partner_reference',
    )

    @api.multi
    def _get_partner_references_string(self, references):
        reference_list = []
        for reference in references:
            if reference not in reference_list:
                reference_list.append(reference)
        res = ','.join(reference_list)
        return res

    @api.multi
    @api.depends('move_lines.partner_reference')
    def _compute_partner_reference(self):
        for picking in self:
            references = picking.mapped('move_lines').filtered(
                lambda m: m.partner_reference).mapped('partner_reference')
            picking.partner_reference = self._get_partner_references_string(
                references
            )

    @api.model
    def _search_partner_reference(self, operator, value):
        return [('move_lines.partner_reference', operator, value)]
