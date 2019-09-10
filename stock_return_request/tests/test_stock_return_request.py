# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .test_stock_return_request_common import StockReturnRequestCase


class PurchaseReturnRequestCase(StockReturnRequestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_return_request_to_customer(self):
        """Find pickings from the customer and make the return"""
        self.return_request_customer.write({
            'line_ids': [(0, 0, {
                'product_id': self.prod_1.id,
                'quantity': 12.0,
            })],
        })
        self.return_request_customer.action_confirm()
        pickings = self.return_request_customer.returned_picking_ids
        moves = self.return_request_customer.returned_picking_ids.mapped(
            'move_lines')
        # There are two pickings found with 10 units delivered each.
        # The return moves are filled up to the needed quantity
        self.assertEqual(len(pickings), 2)
        self.assertEqual(len(moves), 2)
        self.assertAlmostEqual(
            sum(moves.mapped('product_uom_qty')), 12.0)
        # Process the return to validate all the pickings
        self.return_request_customer.action_validate()
        self.assertTrue(all([
            True if x == 'done' else False for x in pickings.mapped('state')]))
        # Now we've got those 12.0 units back in our stock (there were 80.0)
        prod_1_qty = self.prod_1.with_context(
            location=self.wh1.lot_stock_id.id).qty_available
        self.assertAlmostEqual(prod_1_qty, 92.0)

    def test_02_return_request_to_supplier(self):
        """Find pickings from the supplier and make the return"""
        self.return_request_supplier.write({
            'line_ids': [(0, 0, {
                'product_id': self.prod_1.id,
                'quantity': 12.0,
            })],
        })
        self.return_request_supplier.action_confirm()
        pickings = self.return_request_supplier.returned_picking_ids
        moves = self.return_request_supplier.returned_picking_ids.mapped(
            'move_lines')
        # There are two pickings found with 10 and 90 units. The older beign
        # the one with 10. So two pickings are get.
        # The return moves are filled up to the needed quantity
        self.assertEqual(len(pickings), 2)
        self.assertEqual(len(moves), 2)
        self.assertAlmostEqual(
            sum(moves.mapped('product_uom_qty')), 12.0)
        # Process the return to validate all the pickings
        self.return_request_supplier.action_validate()
        self.assertTrue(all([
            True if x == 'done' else False for x in pickings.mapped('state')]))
        # We've returned 12.0 units from the 80.0 we had
        prod_1_qty = self.prod_1.with_context(
            location=self.wh1.lot_stock_id.id).qty_available
        self.assertAlmostEqual(prod_1_qty, 68.0)

    def test_03_return_request_to_supplier_with_lots(self):
        """Find pickings from the supplier and make the return"""
        self.return_request_supplier.write({
            'line_ids': [
                (0, 0, {
                    'product_id': self.prod_3.id,
                    'lot_id': self.prod_3_lot1.id,
                    'quantity': 50.0,
                }),
                (0, 0, {
                    'product_id': self.prod_3.id,
                    'lot_id': self.prod_3_lot2.id,
                    'quantity': 5.0,
                }),
            ],
        })
        self.return_request_supplier.action_confirm()
        pickings = self.return_request_supplier.returned_picking_ids
        moves = self.return_request_supplier.returned_picking_ids.mapped(
            'move_lines')
        # There are two pickings found with that lot and 90 units.
        # The older has 20 and the newer 70, so only 30 units will be returned
        # from the second.
        self.assertEqual(len(pickings), 2)
        self.assertEqual(len(moves), 2)
        self.assertAlmostEqual(
            sum(moves.mapped('product_uom_qty')), 55.0)
        # Process the return to validate all the pickings
        self.return_request_supplier.action_validate()
        self.assertTrue(all([
            True if x == 'done' else False for x in pickings.mapped('state')]))
        # We've returned 50.0 units from the 90.0 we had for that lot
        prod_3_qty_lot_1 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id,
            lot_id=self.prod_3_lot1.id).qty_available
        prod_3_qty_lot_2 = self.prod_3.with_context(
            location=self.wh1.lot_stock_id.id,
            lot_id=self.prod_3_lot2.id).qty_available
        self.assertAlmostEqual(prod_3_qty_lot_1, 40.0)
        self.assertAlmostEqual(prod_3_qty_lot_2, 5.0)
