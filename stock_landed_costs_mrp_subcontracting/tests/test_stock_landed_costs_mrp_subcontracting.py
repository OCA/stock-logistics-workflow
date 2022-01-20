# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockAutoMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Activate the subcontracting flag in the res.config.settings.
        # Create a vendor that will be in charge of the subcontracting.
        # Create a vendor that will be in charge of the additional landed costs.
        # Create a product category with costing method FIFO and inventory
        # valuation = automated.
        # Create a product that will be the subcontracted, using the category
        # that was created. Add the buy route
        # Add a supplierinfo record to the product, with the subcontracting
        # vendor and the cost of $10 corresponding to the subcontracting
        # service.
        # Create a component product. Set the routes 'Buy' and 'Resupply
        # Subcontractor on Order'. Add a starting cost of $10.
        # Add 1 units to the stock on hand for the component.
        # Create a bill of materials of type subcontracting and add the above
        # component. 1 unit of the finished product requires 1 unit of the
        # component. Set as vendor of the bill of material the subcontracting
        # partner.
        # Create a product for the landed costs. Set the flag 'landed cost'.

    def test_01(self):
        # Create a purchase order for the subcontracting vendor and the
        # subcontracted product. Confirm the PO
        # Locate the delivery order that has been created for the component
        # from the stock location to the subcontracting location and complete
        # it.
        # Locate the incoming shipment associated with the Purchase Order and
        # complete it.
        # Check that inventory valuation for the subcontracted product is now
        # $20 ($10 for the subcontracting process + $10 for the component)
        # Create a vendor bill for the landed costs. Add the landed cost
        # vendor and add a line with the landed cost product, with cost $10.
        # Create a landed cost from the vendor bill and add the incoming
        # shipment associated with the PO.
        # Compute the landed cost and complete it.
        # Verify that the inventory valuation for the subcontracted product
        # is now $30 (the inventory valuation has increased by $10 due to the
        # landed cost being added.)
        to_complete = 1
