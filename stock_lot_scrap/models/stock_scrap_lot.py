# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from lxml import etree


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):  # pragma: no cover
        """Inject the button here to avoid conflicts with other modules
         that add a header element in the main view.
        """
        res = super(StockProductionLot, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        eview = etree.fromstring(res['arch'])
        xml_header = eview.xpath("//header")
        if not xml_header:
            # Create a header
            header_element = etree.Element('header')
            # Append it to the view
            forms = eview.xpath("//form")
            if forms:
                forms[0].insert(0, header_element)
        else:
            header_element = xml_header[0]
        button_element = etree.Element(
            'button', {'type': 'object',
                       'name': 'action_scrap_lot',
                       'confirm': _('This will scrap the whole lot. Are you'
                                    ' sure you want to continue?'),
                       'string': _('Scrap')})
        header_element.append(button_element)
        res['arch'] = etree.tostring(eview)
        return res

    def _prepare_scrap_vals(self, quant, scrap_location_id):
        self.ensure_one()
        return {
            'origin': quant.lot_id.name,
            'product_id': quant.product_id.id,
            'product_uom_id': quant.product_id.uom_id.id,
            'scrap_qty': quant.qty,
            'location_id': quant.location_id.id,
            'scrap_location_id': scrap_location_id,
            'lot_id': self.id,
            'picking_id': quant.history_ids[-1:].picking_id.id,
            'package_id': quant.package_id.id,
        }

    @api.multi
    def action_scrap_lot(self):
        self.ensure_one()
        quants = self.quant_ids.filtered(
            lambda x: x.location_id.usage == 'internal',
        )
        if not quants:
            raise ValidationError(
                _("This lot doesn't contain any quant in internal location."),
            )
        scrap_obj = self.env['stock.scrap']
        scraps = scrap_obj.browse()
        scrap_location_id = self.env.ref('stock.stock_location_scrapped').id
        for quant in quants.sorted(key=lambda x: x.history_ids[-1:].
                                   picking_id.picking_type_id.warehouse_id.id):
            scrap = scrap_obj.create(
                self._prepare_scrap_vals(quant, scrap_location_id),
            )
            scraps |= scrap
        result = self.env.ref('stock.action_stock_scrap').read()[0]
        result['context'] = self.env.context
        if len(scraps) != 1:
            result['domain'] = "[('id', 'in', %s)]" % scraps.ids
        else:  # pragma: no cover
            res = self.env.ref('stock.stock_scrap_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = scraps.id
        return result
