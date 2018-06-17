# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestStockPickingTransferLotAutoAssign(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingTransferLotAutoAssign, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.warehouse = cls.env['stock.warehouse'].search([], limit=1)
        cls.picking_type = cls.env['stock.picking.type'].search([
            ('warehouse_id', '=', cls.warehouse.id),
            ('code', '=', 'outgoing'),
        ], limit=1)
        cls.picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.picking_type.id,
            'location_id': cls.picking_type.default_location_src_id.id,
            'location_dest_id': cls.partner.property_stock_customer.id,
        })
        cls.Move = cls.env['stock.move']
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'type': 'product',
            'tracking': 'lot',
        })
        cls.product_no_lot = cls.env['product.product'].create({
            'name': 'Test product no lot',
            'type': 'product',
            'tracking': 'none',
        })
        cls.lot1 = cls.env['stock.production.lot'].create({
            'product_id': cls.product.id,
            'name': 'Lot 1',
        })
        cls.quant1 = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.picking.location_id.id,
            'quantity': 6,
            'lot_id': cls.lot1.id,
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'product_id': cls.product.id,
            'name': 'Lot 2',
        })
        cls.quant2 = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.picking.location_id.id,
            'quantity': 10,
            'lot_id': cls.lot2.id,
        })
        cls.move = cls.Move.create({
            'name': cls.product.name,
            'product_id': cls.product.id,
            'product_uom_qty': 10,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking.id,
            'location_id': cls.picking.location_id.id,
            'location_dest_id': cls.picking.location_dest_id.id})

    def test_transfer(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        pack_ops = self.picking.move_line_ids
        self.assertEqual(len(pack_ops), 2)
        self.assertEqual(len(pack_ops.mapped('lot_id')), 2)
        self.assertEqual(pack_ops[0].product_uom_qty, 6)
        self.assertEqual(pack_ops[1].product_uom_qty, 4)
        self.assertEqual(self.move.quantity_done, 10)
