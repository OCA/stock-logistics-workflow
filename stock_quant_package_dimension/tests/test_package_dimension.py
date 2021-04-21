# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from psycopg2 import OperationalError
from odoo import fields
from . import common


class TestStockQuantPackageProductPackaging(
    common.TestStockQuantPackageCommon
):
    @classmethod
    def setUpClass(cls):
        super(TestStockQuantPackageProductPackaging, cls).setUpClass()
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "10 pack",
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "qty": 10,
                "lngth": 12,
                "width": 13,
                "height": 14,
                "max_weight": 15,
            }
        )
        cls.product.packaging_ids = cls.packaging

    def _get_removal_strategy(self, product_id, location_id):
        if product_id.categ_id.removal_strategy_id:
            return product_id.categ_id.removal_strategy_id.method
        loc = location_id
        while loc:
            if loc.removal_strategy_id:
                return loc.removal_strategy_id.method
            loc = loc.location_id
        return "fifo"

    def _gather_quants(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        from odoo.osv import expression

        StockQuant = self.env["stock.quant"]
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = StockQuant._quants_removal_get_order(
            removal_strategy
        )
        domain = [
            ("product_id", "=", product_id.id),
        ]
        if not strict:
            if lot_id:
                domain = expression.AND([[("lot_id", "=", lot_id.id)], domain])
            if package_id:
                domain = expression.AND(
                    [[("package_id", "=", package_id.id)], domain]
                )
            if owner_id:
                domain = expression.AND(
                    [[("owner_id", "=", owner_id.id)], domain]
                )
            domain = expression.AND(
                [[("location_id", "child_of", location_id.id)], domain]
            )
        else:
            domain = expression.AND(
                [[("lot_id", "=", lot_id and lot_id.id or False)], domain]
            )
            domain = expression.AND(
                [
                    [
                        (
                            "package_id",
                            "=",
                            package_id and package_id.id or False,
                        )
                    ],
                    domain,
                ]
            )
            domain = expression.AND(
                [
                    [("owner_id", "=", owner_id and owner_id.id or False)],
                    domain,
                ]
            )
            domain = expression.AND(
                [[("location_id", "=", location_id.id)], domain]
            )

        query = StockQuant._where_calc(domain)
        StockQuant._apply_ir_rules(query, "read")
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_str = where_clause and (" WHERE %s" % where_clause) or ""
        query_str = (
            'SELECT "%s".id FROM ' % StockQuant._table
            + from_clause
            + where_str
            + " ORDER BY "
            + removal_strategy_order
        )
        # pylint: disable=sql-injection
        self.env.cr.execute(query_str, where_clause_params)
        res = self.env.cr.fetchall()
        # No uniquify list necessary as auto_join is not applied anyways...
        return StockQuant.browse([x[0] for x in res])

    def _quant_update_available_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
    ):
        """ Increase or decrease `reserved_quantity` of a set of quants
         for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :param datetime in_date: Should only be passed when calls to this
                                 method are done in
                                 order to move a quant. When creating a tracked
                                 quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        quants = self._gather_quants(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=True,
        )

        incoming_dates = [d for d in quants.mapped("in_date") if d]
        incoming_dates = [
            fields.Datetime.from_string(incoming_date)
            for incoming_date in incoming_dates
        ]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/
        # package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = fields.Datetime.to_string(min(incoming_dates))
        else:
            in_date = fields.Datetime.now()

        for quant in quants:
            try:
                with self.env.cr.savepoint():
                    self.env.cr.execute(
                        "SELECT 1 FROM stock_quant WHERE id = %s "
                        "FOR UPDATE NOWAIT",
                        [quant.id],
                        log_exceptions=False,
                    )
                    quant.write(
                        {"qty": quant.quantity + quantity, "in_date": in_date}
                    )
                    break
            except OperationalError as e:
                if e.pgcode == "55P03":  # could not obtain the lock
                    continue
                else:
                    raise
        else:
            self.env["stock.quant"].create(
                {
                    "product_id": product_id.id,
                    "location_id": location_id.id,
                    "qty": quantity,
                    "lot_id": lot_id and lot_id.id,
                    "package_id": package_id and package_id.id,
                    "owner_id": owner_id and owner_id.id,
                    "in_date": in_date,
                }
            )

    def assertRecordValues(self, records, expected_values):
        # a naive backport from 13.0 to ease the comparison of the code
        # between this backport into 10.0 from 13.0
        for record, values in zip(records, expected_values):
            for field, value in values.items():
                self.assertEqual(record[field], value)

    def test_set_dimensions_on_write(self):
        self.package.with_context(
            _auto_assign_packaging=True
        ).product_packaging_id = self.packaging
        self.assertRecordValues(
            self.package,
            [{"lngth": 12, "width": 13, "height": 14, "pack_weight": 15}],
        )

    def test_set_dimensions_on_write_no_override(self):
        values = {"lngth": 22, "width": 23, "height": 24, "pack_weight": 25}
        self.package.write(values)
        self.package.with_context(
            _auto_assign_packaging=True
        ).product_packaging_id = self.packaging
        self.assertRecordValues(self.package, [values])

    def test_set_dimensions_onchange(self):
        values = {"lngth": 22, "width": 23, "height": 24, "pack_weight": 25}
        self.package.write(values)
        new_values = values.copy()
        new_values["product_packaging_id"] = self.packaging.id
        res = self.package.onchange(
            new_values, ["product_packaging_id"], {"product_packaging_id": "1"}
        )
        self.package.update(res.get("value", {}))
        # onchange overrides values
        self.assertRecordValues(
            self.package,
            [{"lngth": 12, "width": 13, "height": 14, "pack_weight": 15}],
        )

    def test_package_estimated_pack_weight(self):
        self._quant_update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            7.0,
            package_id=self.package,
        )
        # Weight are taken from product, like the delivery module
        self.assertEqual(self.package.estimated_pack_weight, 7)
        self.move.action_assign()
        for operation in self.move.linked_move_operation_ids.mapped(
            "operation_id"
        ):
            operation.qty_done = operation.product_qty
            operation.result_package_id = self.package
        self.assertEqual(
            self.package.with_context(
                picking_id=self.move.picking_id.id
            ).estimated_pack_weight,
            7,
        )
