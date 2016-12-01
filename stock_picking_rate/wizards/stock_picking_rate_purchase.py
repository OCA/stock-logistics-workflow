# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class StockPickingRatePurchase(models.TransientModel):
    """ Purchase a set of stock rates """
    _name = "stock.picking.rate.purchase"
    _description = 'Stock Picking Dispatch Rate Purchase'

    rate_ids = fields.Many2many(
        string='Rates',
        readonly=True,
        comodel_name='stock.picking.rate',
        relation='stock_picking_rate_purchase_rel',
        default=lambda s: s._default_rate_ids(),
    )
    date_po = fields.Datetime(
        string='Purchase Order Date',
        required=True,
        default=lambda s: fields.Datetime.now(),
    )
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('commercial', 'Carrier Commercial Partner'),
        ('carrier', 'Carrier Partner'),
        ('service', 'Carrier Service'),
    ],
        default='carrier',
        required=True,
        help='When creating purchase orders, this will be used to determine'
             ' the rates that go on each order.',
    )

    @api.model
    def _default_rate_ids(self):
        model = 'stock.picking.rate'
        if self.env.context.get('active_model') != model:
            return None
        return [(6, 0, self.env.context.get('active_ids'))]

    @api.multi
    def action_purchase(self):
        """ Purchase rate quotes """

        self.ensure_one()

        purchase_rates = {}
        for rate_id in self.rate_ids:
            group_map = {
                'none': rate_id.id,
                'commercial': rate_id.partner_id.commercial_partner_id.id,
                'carrier': rate_id.partner_id.id,
                'service': rate_id.service_id.id,
            }
            po_id = group_map[self.group_by]
            try:
                purchase_rates[po_id].append(rate_id)
            except KeyError:
                purchase_rates[po_id] = [rate_id]
            rate_id.buy()

        po_id_ints = []
        for rate_ids in purchase_rates.values():
            po_id = self.env['purchase.order'].create(
                self._get_purchase_order_vals(rate_ids)
            )
            po_id_ints.append(po_id.id)

        self.rate_ids._expire_other_rates()

        model_obj = self.env['ir.model.data']
        form_id = model_obj.xmlid_to_object(
            'purchase.purchase_order_form'
        )
        tree_id = model_obj.xmlid_to_object(
            'purchase.purchase_order_tree'
        )
        action_id = model_obj.xmlid_to_object(
            'purchase.purchase_form_action'
        )
        return {
            'name': action_id.name,
            'help': action_id.help,
            'type': action_id.type,
            'view_mode': 'tree',
            'view_id': tree_id.id,
            'views': [
                (tree_id.id, 'tree'),
                (form_id.id, 'form'),
            ],
            'target': 'current',
            'context': self.env.context,
            'res_model': action_id.res_model,
            'res_ids': po_id_ints,
            'domain': [('id', 'in', po_id_ints)],
        }

    @api.multi
    def action_show_wizard(self):
        """ Utility method to show the wizard
        Returns:
            Wizard action for completion of delivery packing
        """
        self.ensure_one()
        model_obj = self.env['ir.model.data']
        _prefix = 'stock_picking_rate.stock_picking_rate_purchase'
        form_id = model_obj.xmlid_to_object(
            '%s_view_form' % _prefix,
        )
        action_id = model_obj.xmlid_to_object(
            '%s_action' % _prefix,
        )
        return {
            'name': action_id.name,
            'help': action_id.help,
            'type': action_id.type,
            'view_mode': 'form',
            'view_id': form_id.id,
            'views': [
                (form_id.id, 'form'),
            ],
            'target': 'new',
            'context': self.env.context,
            'res_model': action_id.res_model,
            'res_id': self.id,
        }

    @api.multi
    def _get_purchase_line_vals(self, rate_id):
        """ Get values used for purchasing dispatch rates
        This will be useful for classes requiring custom purchase logic,
        such as external carrier connectors
        """
        return {
            'product_id': rate_id.service_id.product_id.id,
            'name': rate_id.display_name,
            'date_planned': self.date_po,
            'product_qty': 1,
            'product_uom': self.env.ref('product.product_uom_unit').id,
            'price_unit': rate_id.rate,
            'currency_id': rate_id.rate_currency_id.id,
        }

    @api.multi
    def _get_purchase_order_vals(self, rate_ids):
        """ Get values for use in purchase order creation """
        self.ensure_one()
        if not len(rate_ids):
            return
        return {
            'partner_id': rate_ids[0].partner_id.id,
            'date_planned': self.date_po,
            'state': 'purchase',
            'order_line': [
                (0, 0, self._get_purchase_line_vals(r)) for r in rate_ids
            ]
        }
