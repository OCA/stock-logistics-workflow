# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockPickingRate(models.Model):
    _name = 'stock.picking.rate'
    _description = 'Stock Picking Dispatch Rate'

    picking_id = fields.Many2one(
        string='Stock Picking',
        comodel_name='stock.picking',
        required=True,
    )
    service_id = fields.Many2one(
        string='Carrier Service',
        comodel_name='delivery.carrier',
        required=True,
    )
    date_generated = fields.Datetime(
        required=True,
        default=lambda s: fields.Datetime.now(),
    )
    date_purchased = fields.Datetime(
        store=True,
        compute='_compute_date_purchased',
    )
    rate_currency_id = fields.Many2one(
        string='Rate Currency',
        comodel_name='res.currency',
        required=True,
    )
    rate = fields.Float(
        digits=dp.get_precision('Product Price'),
        required=True,
    )
    retail_rate = fields.Float(
        digits=dp.get_precision('Product Price'),
    )
    retail_rate_currency_id = fields.Many2one(
        string='Retail Rate Currency',
        comodel_name='res.currency',
    )
    list_rate = fields.Float(
        digits=dp.get_precision('Product Price'),
    )
    list_rate_currency_id = fields.Many2one(
        string='List Rate Currency',
        comodel_name='res.currency',
    )
    delivery_days = fields.Integer()
    date_delivery = fields.Datetime(
        string='Est Delivery Date',
    )
    is_guaranteed = fields.Boolean(
        string='Date is Guaranteed?',
    )
    partner_id = fields.Many2one(
        string='Carrier Partner',
        comodel_name='res.partner',
        related='service_id.partner_id',
    )
    state = fields.Selection([
        ('new', 'Quoted'),
        ('purchase', 'Purchased'),
        ('cancel', 'Voided'),
    ],
        default='new',
    )
    is_purchased = fields.Boolean(
        compute='_compute_is_purchased',
    )

    @api.multi
    @api.depends('state')
    def _compute_date_purchased(self):
        for rec_id in self:
            if rec_id.state == 'purchase' and not rec_id.date_purchased:
                rec_id.date_purchased = fields.Datetime.now()

    @api.multi
    def _compute_is_purchased(self):
        for rec_id in self:
            rec_id.is_purchased = bool(rec_id.date_purchased)

    @api.multi
    def name_get(self):
        res = []
        for rec_id in self:
            name = '{partner_name} {service_name} - {rate}'.format(
                partner_name=rec_id.partner_id.name,
                service_name=rec_id.service_id.name,
                rate=rec_id.rate,
            )
            res.append((rec_id.id, name))
        return res

    @api.multi
    def action_purchase(self):
        wizard_id = self.env['stock.picking.rate.purchase'].create({
            'rate_ids': [(6, 0, [r.id for r in self])],
        })
        return wizard_id.action_show_wizard()

    @api.multi
    def buy(self):
        self.state = 'purchase'

    @api.multi
    def _expire_other_rates(self):
        """ Expires rates in picking that are not record """
        for rec_id in self:
            rate_ids = rec_id.picking_id.dispatch_rate_ids.filtered(
                lambda r: r.id != rec_id.id
            )
            rate_ids.write({
                'state': 'cancel',
            })
