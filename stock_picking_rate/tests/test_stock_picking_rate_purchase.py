# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestHelper


class TestStockPickingRate(TestHelper):

    def setUp(self):
        super(TestStockPickingRate, self).setUp()
        self.rate_ids = [self.new_record(), self.new_record()]
        self.Wizard = self.env['stock.picking.rate.purchase']
        self.wizard_vals = {
            'rate_ids': [(6, 0, [r.id for r in self.rate_ids])],
        }

    def test_default_rate_ids(self):
        """ It should default to active rate ids """
        exp = [r.id for r in self.rate_ids]
        rec_id = self.Wizard.with_context(
            active_ids=exp,
            active_model=self.Wizard._name,
        ).create({})
        res = [r.id for r in rec_id.rate_ids]
        self.assertEquals(
            res, exp,
            '\rGot: %s \rExpected: %s' % (
                res, exp
            )
        )

    def test_default_rate_ids_no_model(self):
        """ It should return None if not same model """
        recs = [r.id for r in self.rate_ids]
        rec_id = self.Wizard.with_context(
            active_ids=recs,
            active_model=None,
        ).create({})
        self.assertFalse(
            rec_id.rate_ids,
        )

    def test_action_purchase(self):
        """ Test action_purchase attrs correctly returned """
        recs = [r.id for r in self.rate_ids]
        rec_id = self.Wizard.with_context(
            active_ids=recs,
            active_model=self.Wizard._name,
        ).create({})

        res_action_purchase = rec_id.action_purchase()
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
        exp_keys = {
            'name': action_id.name,
            'help': action_id.help,
            'type': action_id.type,
            'view_mode': 'tree',
            'view_id': tree_id.id,
            'target': 'current',
            'context': rec_id._context.copy(),
            'res_model': action_id.res_model,
        }
        self.assertEquals(
            len(res_action_purchase['res_ids']),
            1,
        )
        self.assertEquals(
            res_action_purchase['views'][0][0],
            tree_id.id,
        )
        self.assertEquals(
            res_action_purchase['views'][1][0],
            form_id.id,
        )
        for key in exp_keys:
            res = res_action_purchase[key]
            exp = exp_keys[key]
            self.assertEquals(
                res, exp,
                '\rKey: %s \rGot: %s \rExpected: %s' % (
                    key, res, exp
                )
            )

    def test_action_show_wizard(self):
        """ Test action_show_wizard attrs correctly returned """
        recs = [r.id for r in self.rate_ids]
        rec_id = self.Wizard.with_context(
            active_ids=recs,
            active_model=self.Wizard._name,
        ).create({})

        res_action_show_wizard = rec_id.action_show_wizard()
        model_obj = self.env['ir.model.data']
        _prefix = 'stock_picking_rate.stock_picking_rate_purchase'
        form_id = model_obj.xmlid_to_object(
            '%s_view_form' % _prefix,
        )
        action_id = model_obj.xmlid_to_object(
            '%s_action' % _prefix,
        )
        exp_keys = {
            'name': action_id.name,
            'help': action_id.help,
            'type': action_id.type,
            'view_mode': 'form',
            'view_id': form_id.id,
            'target': 'new',
            'context': rec_id._context.copy(),
            'res_model': action_id.res_model,
            'res_id': rec_id.id,
        }
        self.assertEquals(
            res_action_show_wizard['views'][0][0],
            form_id.id,
        )
        for key in exp_keys:
            res = res_action_show_wizard[key]
            exp = exp_keys[key]
            self.assertEquals(
                res, exp,
                '\rKey: %s \rGot: %s \rExpected: %s' % (
                    key, res, exp
                )
            )

    def test_get_purchase_line_vals(self):
        """ Test returns correct attrs """
        recs = [r.id for r in self.rate_ids]
        rec_id = self.Wizard.with_context(
            active_ids=recs,
            active_model=self.Wizard._name,
        ).create({})
        res_get_line_vals = rec_id._get_purchase_line_vals(self.rate_ids[0])
        exp_keys = {
            'product_id': self.rate_ids[0].service_id.product_id.id,
            'name': self.rate_ids[0].display_name,
            'date_planned': rec_id.date_po,
            'product_qty': 1,
            'product_uom': self.env.ref('product.product_uom_unit').id,
            'price_unit': self.rate_ids[0].rate,
            'currency_id': self.rate_ids[0].rate_currency_id.id,
        }
        for key in exp_keys:
            res = res_get_line_vals[key]
            exp = exp_keys[key]
            self.assertEquals(
                res, exp,
                '\rKey: %s \rGot: %s \rExpected: %s' % (
                    key, res, exp
                )
            )

    def test_get_purchase_order_vals(self):
        """ Test returns correct attrs """
        recs = [r.id for r in self.rate_ids]
        rec_id = self.Wizard.with_context(
            active_ids=recs,
            active_model=self.Wizard._name,
        ).create({})
        res_get_order_vals = rec_id._get_purchase_order_vals(self.rate_ids)
        exp_keys = {
            'partner_id': self.rate_ids[0].partner_id.id,
            'date_planned': rec_id.date_po,
            'state': 'purchase',
            'order_line': [
                (
                    0, 0,
                    rec_id._get_purchase_line_vals(r)
                ) for r in self.rate_ids
            ]
        }
        for key in exp_keys:
            res = res_get_order_vals[key]
            exp = exp_keys[key]
            self.assertEquals(
                res, exp,
                '\rKey: %s \rGot: %s \rExpected: %s' % (
                    key, res, exp
                )
            )
