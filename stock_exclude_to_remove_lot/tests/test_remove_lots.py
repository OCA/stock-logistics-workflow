# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import common


class TestRemoveLots(common.TransactionCase):

    def setUp(self):
        super(TestRemoveLots, self).setUp()

        self.picking_type = self.env.ref('stock.picking_type_internal')
        self.picking_type.exclude_to_remove_lots = True
        self.origin = self.env.ref('stock.stock_location_components')
        self.destination = self.env.ref('stock.stock_location_stock')
        self.product = self.env.ref('stock.product_icecream')
        self.product.tracking = 'lot'
        self.product.type = 'product'
        self.chg_qty_bj = self.env['stock.change.product.qty']
        self.lot_obj = self.env['stock.production.lot']
        self.move_obj = self.env['stock.move']

        self.existing_lots = self.lot_obj.search(
            [('removal_date', '=', False)])

        # Create Some lots
        vals = {
            'product_id': self.product.id,
            'removal_date': fields.Datetime.to_string(
                datetime.now() + timedelta(days=10)),
        }
        self.lot_1 = self.lot_obj.create(vals)

        vals = {
            'product_id': self.product.id,
            'removal_date': fields.Datetime.to_string(
                datetime.now() + timedelta(days=30)),
        }
        self.lot_2 = self.lot_obj.create(vals)

        vals = {
            'product_id': self.product.id,
            'removal_date': fields.Datetime.to_string(
                datetime.now() - timedelta(days=30)),
        }
        # To remove lot
        self.lot_3 = self.lot_obj.create(vals)

        vals = {
            'product_id': self.product.id,
            'removal_date': False,
        }
        # Lot without removal date
        self.lot_4 = self.lot_obj.create(vals)

        # Set Inventory with lots
        vals = {
            'product_id': self.product.id,
            'new_quantity': 10.0,
            'lot_id': self.lot_1.id,
            'location_id': self.origin.id,
        }
        wizard = self.chg_qty_bj.create(vals)
        wizard.change_product_qty()
        vals = {
            'product_id': self.product.id,
            'new_quantity': 10.0,
            'lot_id': self.lot_2.id,
            'location_id': self.origin.id,
        }
        wizard = self.chg_qty_bj.create(vals)
        wizard.change_product_qty()

        vals = {
            'product_id': self.product.id,
            'new_quantity': 10.0,
            'lot_id': self.lot_3.id,
            'location_id': self.origin.id,
        }
        wizard = self.chg_qty_bj.create(vals)
        wizard.change_product_qty()

        vals = {
            'product_id': self.product.id,
            'new_quantity': 10.0,
            'lot_id': self.lot_4.id,
            'location_id': self.origin.id,
        }
        wizard = self.chg_qty_bj.create(vals)
        wizard.change_product_qty()

        vals = {
            'name': 'PICKING REMOVAL',
            'picking_type_id': self.picking_type.id,
            'location_id': self.origin.id,
            'location_dest_id': self.destination.id,
        }
        self.picking1 = self.env['stock.picking'].create(vals)

        vals = {
            'name': 'MOVE REMOVAL',
            'picking_id': self.picking1.id,
            'product_id': self.product.id,
            'product_uom_qty': 3.0,
            'product_uom': self.product.uom_id.id,
            'location_id': self.origin.id,
            'location_dest_id': self.destination.id,
        }
        self.move_obj.create(vals)

    def test_removal(self):
        self.picking1.action_confirm()
        self.picking1.action_assign()
        self.assertEquals(
            1,
            len(self.picking1.pack_operation_ids),
        )
        operation = self.picking1.pack_operation_ids

        domain = [
            ('product_id', '=', self.product.id),
        ]
        # As the opening of the pack operation split lot window set
        # active_pack_operation in context
        lots = self.lot_obj.with_context(
            active_pack_operation=operation.id).search(domain)
        self.assertEquals(
            3,
            len(lots - self.existing_lots),
        )
