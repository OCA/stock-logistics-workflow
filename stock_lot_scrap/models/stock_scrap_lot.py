# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError
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
                       'string': _('Scrap')})
        header_element.append(button_element)
        res['arch'] = etree.tostring(eview)
        return res

    @api.multi
    def _prepare_picking_vals(self, quant, scrap_location_id):
        warehouse = (
            quant.history_ids[-1:].picking_id.picking_type_id.warehouse_id
        )
        return {
            'origin': _('Lot: %s') % self.name,
            'picking_type_id': warehouse.int_type_id.id or self.env.ref(
                'stock.picking_type_internal').id,
            'location_id': quant.location_id.id,
            'location_dest_id': scrap_location_id,
        }

    @api.multi
    def _prepare_move_vals(self, picking, quant, scrap_location_id):
        self.ensure_one()
        move_obj = self.env['stock.move']
        product = quant.product_id
        res = move_obj.onchange_product_id(
            prod_id=product.id, loc_id=quant.location_id.id,
            loc_dest_id=scrap_location_id,
        )['value']
        res.update({
            'product_id': product.id,
            'product_uom_qty': quant.qty,
            'picking_id': picking.id,
            'scrapped': True,
        })
        return res

    @api.multi
    def action_scrap_lot(self):
        self.ensure_one()
        quants = self.quant_ids.filtered(
            lambda x: x.location_id.usage == 'internal',
        )
        if not quants:
            raise UserError(
                _("This lot doesn't contain any quant in internal location."),
            )
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.browse()
        scrap_location_id = self.env.ref('stock.stock_location_scrapped').id
        location_ids = []
        for quant in quants.sorted(key=lambda x: x.history_ids[-1:].
                                   picking_id.picking_type_id.warehouse_id.id):
            if quant.location_id.id not in location_ids:
                location_ids.append(quant.location_id.id)
                picking = picking_obj.create(
                    self._prepare_picking_vals(quant, scrap_location_id),
                )
                pickings |= picking
            move = move_obj.create(
                self._prepare_move_vals(picking, quant, scrap_location_id),
            )
            quant.reservation_id = move.id
            move.action_confirm()
            move.action_assign()
        result = self.env.ref('stock.action_picking_tree').read()[0]
        result['context'] = self.env.context
        if len(pickings) != 1:  # pragma: no cover
            result['domain'] = "[('id', 'in', %s)]" % pickings.ids
        else:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pickings.id
        return result
