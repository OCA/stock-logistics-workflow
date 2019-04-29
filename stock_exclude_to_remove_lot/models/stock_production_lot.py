# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression


class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    @api.model
    def _get_exclude_to_remove_lots_domain(self):
        removal_domain = expression.AND([
            [('removal_date', '!=', False)],
            [('removal_date', '>', fields.Datetime.now())],
        ])
        domain = expression.OR([
            [('removal_date', '=', False)],
            removal_domain,
        ])
        return domain

    @api.model
    def _get_search_to_remove_lots_args(self, args):
        pack_id = self.env.context.get('active_pack_operation')
        if pack_id:
            pack = self.env['stock.pack.operation'].browse(pack_id)
            if pack.picking_id.picking_type_id.exclude_to_remove_lots:
                domain = self._get_exclude_to_remove_lots_domain()
                args = expression.AND([
                    args,
                    domain,
                ])
        return args

    @api.model
    def _search(
            self,
            args,
            offset=0,
            limit=None,
            order=None,
            count=False,
            access_rights_uid=None):
        """
        Overrides the search to restrict expired removal date lots
        :param args:
        :param offset:
        :param limit:
        :param order:
        :param count:
        :return:
        """
        args = self._get_search_to_remove_lots_args(args)
        res = super(StockProductionLot, self)._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid)
        return res
