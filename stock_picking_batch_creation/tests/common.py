# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class ClusterPickingCommonFeatures(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(ClusterPickingCommonFeatures, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls._create_partner("Unittest partner", "12344566777878")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.location_out = cls.env.ref("stock.stock_location_output")
        cls.uom_id = cls.env.ref("uom.product_uom_unit").id
        cls.uom_m = cls.env["uom.uom"].search([("name", "=", "m")])

        cls.p1 = cls._create_product("Unittest P1", 10.0, 10.0, 1, 1)
        cls.p2 = cls._create_product("Unittest P2", 20.0, 20.0, 1, 1)
        cls.p3 = cls._create_product("Unittest P3", 30.0, 30.0, 1, 1)
        cls.p4 = cls._create_product("Unittest P4", 40.0, 40.0, 1, 1)

        cls._set_quantity_in_stock(cls.stock_location, cls.p1)
        cls._set_quantity_in_stock(cls.stock_location, cls.p2)
        cls._set_quantity_in_stock(cls.stock_location, cls.p3)
        cls._set_quantity_in_stock(cls.stock_location, cls.p4)

        cls.makePickingBatch = cls.env["make.picking.batch"]
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        picking_sequence = cls.warehouse_1.pick_type_id.sequence_id

        cls.device1 = cls._create_device(
            "device1",
            min_volume=5,
            max_volume=50,
            max_weight=100,
            nbr_bins=6,
            sequence=100,
        )
        cls.device2 = cls._create_device(
            "device2",
            min_volume=70,
            max_volume=190,
            max_weight=250,
            nbr_bins=10,
            sequence=70,
        )
        cls.device3 = cls._create_device(
            "device3",
            min_volume=30,
            max_volume=100,
            max_weight=150,
            nbr_bins=1,
            sequence=50,
        )
        cls.device4 = cls._create_device(
            "device4",
            min_volume=30,
            max_volume=100,
            max_weight=150,
            nbr_bins=3,
            sequence=100,
        )
        cls.device5 = cls._create_device(
            "device5",
            min_volume=10,
            max_volume=70,
            max_weight=100,
            nbr_bins=10,
            sequence=70,
        )
        cls.device6 = cls._create_device(
            "device6",
            min_volume=50,
            max_volume=200,
            max_weight=300,
            nbr_bins=15,
            sequence=50,
        )

        cls.picking_type_1 = cls.env["stock.picking.type"].create(
            {
                "name": "First picking type",
                "code": "internal",
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": cls.location_out.id,
                "color": 7,
                "sequence": 4,
                "sequence_id": picking_sequence.id,
                "sequence_code": "test1",
            }
        )
        cls.picking_type_2 = cls.env["stock.picking.type"].create(
            {
                "name": "Second Picking type",
                "code": "internal",
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": cls.location_out.id,
                "color": 7,
                "sequence": 4,
                "sequence_id": picking_sequence.id,
                "sequence_code": "test2",
            }
        )

        # the processing order for picks of type 1 will be:
        # pick3 (priority), pick1 (lower id), pick2
        cls.pick1 = cls._create_picking_pick_and_assign(
            cls.picking_type_1.id,
        )
        cls.pick2 = cls._create_picking_pick_and_assign(
            cls.picking_type_1.id, products=cls.p2
        )
        cls.pick3 = cls._create_picking_pick_and_assign(
            cls.picking_type_1.id, priority="1", products=cls.p1 | cls.p2
        )
        cls.make_picking_batch = cls.makePickingBatch.create(
            {
                "user_id": cls.env.user.id,
                "picking_type_ids": [(4, cls.picking_type_1.id)],
                "stock_device_type_ids": [
                    (4, cls.device1.id),
                    (4, cls.device2.id),
                    (4, cls.device3.id),
                ],
                # disable lock: All tests are run in the same transaction
                "picking_locking_mode": False,
            }
        )
        cls.picks = cls.pick1 | cls.pick2 | cls.pick3

    @classmethod
    def _set_quantity_in_stock(cls, location, product, qty=10):

        cls.env["stock.quant"].create(
            {
                "location_id": location.id,
                "product_id": product.id,
                "inventory_quantity": qty,
            }
        ).action_apply_inventory()

    @classmethod
    def _create_partner(cls, name, ref):
        return cls.env["res.partner"].create({"name": name, "ref": ref})

    @classmethod
    def _create_product(
        cls, name, weight, length, height, width, uom_id=None, product_type=None
    ):
        if not uom_id:
            uom_id = cls.uom_id
        if not product_type:
            product_type = "product"
        volume = length * height * width
        return cls.env["product.product"].create(
            {
                "name": name,
                "uom_id": uom_id,
                "type": product_type,
                "weight": weight,
                "product_length": length,
                "product_height": height,
                "product_width": width,
                "volume": volume,
                "dimensional_uom_id": cls.uom_m.id,
            }
        )

    @classmethod
    def _create_device(
        cls, name, min_volume, max_volume, max_weight, nbr_bins, sequence
    ):
        return cls.env["stock.device.type"].create(
            {
                "name": name,
                "min_volume": min_volume,
                "max_volume": max_volume,
                "max_weight": max_weight,
                "nbr_bins": nbr_bins,
                "sequence": sequence,
            }
        )

    @classmethod
    def _create_picking_pick_and_assign(
        cls, picking_type_id, priority=None, products=None, partner=None, warehouse=None
    ):
        if not partner:
            partner = cls.partner1
        if not products:
            products = cls.p1
        if not priority:
            priority = "0"
        if not warehouse:
            warehouse = cls.warehouse_1
        picking_values = {
            "partner_id": partner.id,
            "picking_type_id": picking_type_id,
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "location_dest_id": warehouse.wh_output_stock_loc_id.id,
            "priority": priority,
            "move_ids": [
                (
                    0,
                    0,
                    {
                        "name": p.name,
                        "product_id": p.id,
                        "picking_type_id": picking_type_id,
                        "product_uom_qty": 1,
                        "product_uom": p.uom_id.id,
                        "location_id": cls.env.ref("stock.stock_location_stock").id,
                        "location_dest_id": warehouse.wh_output_stock_loc_id.id,
                    },
                )
                for p in products
            ],
        }
        picking = cls.env["stock.picking"].create(picking_values)
        picking.action_confirm()
        picking.action_assign()
        return picking

    @classmethod
    def _add_product_to_picking(cls, picking, product):
        dest_location = cls.warehouse_1.wh_output_stock_loc_id.id
        src_location = cls.env.ref("stock.stock_location_stock").id
        picking.write(
            {
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "picking_type_id": cls.picking_type_1.id,
                            "product_uom_qty": 1,
                            "product_uom": product.uom_id.id,
                            "location_id": src_location,
                            "location_dest_id": dest_location,
                            "sequence": "3",
                        },
                    )
                ]
            }
        )
        picking.action_confirm()
        picking.action_assign()

    @classmethod
    def _get_picks_by_type(cls, picking_type):
        return cls.env["stock.picking"].search(
            [("picking_type_id", "=", picking_type.id)]
        )
