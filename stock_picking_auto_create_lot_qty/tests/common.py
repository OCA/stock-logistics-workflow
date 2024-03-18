# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


class CommonStockPickingAutoCreateLotQty(object):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.lot_obj = cls.env["stock.lot"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier - test"})

    @classmethod
    def _create_product(
        cls, tracking="lot", auto=True, every_n=0, multiple_allow=False
    ):
        name = "{tracking} - {auto}".format(tracking=tracking, auto=auto)
        return cls.env["product.product"].create(
            {
                "name": name,
                "type": "product",
                "tracking": tracking,
                "auto_create_lot": auto,
                "create_lot_every_n": every_n,
                "only_multiples_allowed": multiple_allow,
            }
        )

    @classmethod
    def _create_picking(cls):
        cls.picking = (
            cls.env["stock.picking"]
            .with_context(default_picking_type_id=cls.picking_type_in.id)
            .create(
                {
                    "partner_id": cls.supplier.id,
                    "picking_type_id": cls.picking_type_in.id,
                    "location_id": cls.supplier_location.id,
                }
            )
        )

    @classmethod
    def _create_move(cls, product=None, qty=1.0):
        location_dest = cls.picking.picking_type_id.default_location_dest_id
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test-{product}".format(product=product.name),
                "product_id": product.id,
                "picking_id": cls.picking.id,
                "picking_type_id": cls.picking.picking_type_id.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": location_dest.id,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "reserved_uom_qty": qty,
                            "product_uom_id": product.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": location_dest.id,
                            "picking_id": cls.picking.id,
                        },
                    )
                ],
            }
        )
