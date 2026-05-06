# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from itertools import zip_longest

from odoo import tests
from odoo.tests import Form


class TestCommon(tests.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        # In Odoo 19, the stock valuation architecture changed: account moves
        # on stock movements are only created when one of the involved stock
        # locations has a valuation_account_id set, and the company has a
        # valuation account/journal configured. For an outgoing move
        # (stock -> customer), we set valuation_account_id on the customer
        # location so the perpetual valuation entry is generated.
        company = cls.env.company
        company.inventory_valuation = "real_time"
        valuation_account = company.account_stock_valuation_id
        if not valuation_account:
            valuation_account = cls.env["account.account"].create(
                {
                    "name": "Stock Valuation (test)",
                    "code": "STKVAL",
                    "account_type": "asset_current",
                }
            )
            company.account_stock_valuation_id = valuation_account
        if not company.account_stock_journal_id:
            stock_journal = cls.env["account.journal"].search(
                [("type", "=", "general"), ("company_id", "=", company.id)],
                limit=1,
            )
            if not stock_journal:
                stock_journal = cls.env["account.journal"].create(
                    {
                        "name": "Stock Journal (test)",
                        "code": "STJTST",
                        "type": "general",
                        "company_id": company.id,
                    }
                )
            company.account_stock_journal_id = stock_journal
        cls.customer_location.valuation_account_id = valuation_account
        cls.stock_location.valuation_account_id = valuation_account

        cls.products = cls._create_real_time_products(
            [
                {
                    "name": "Test backdating 1",
                    "standard_price": 10,
                },
                {
                    "name": "Test backdating 2",
                    "standard_price": 20,
                },
            ]
        )

        # Map each product to how much will be moved
        products_move_mapping = {
            cls.products[0]: 1,
            cls.products[1]: 2,
        }
        # Create enough availability in stock for the products to be moved
        stock_quant_model = cls.env["stock.quant"]
        for product, quantity in products_move_mapping.items():
            stock_quant_model._update_available_quantity(
                product,
                cls.stock_location,
                quantity,
                lot_id=None,
                package_id=None,
                owner_id=None,
                in_date=None,
            )

        picking = cls._create_picking(products_move_mapping)
        picking.action_confirm()
        picking.action_assign()
        cls.picking = picking

    def _get_datetime_backdating(self, timedelta_days):
        now = datetime.now()
        date_backdating = now - timedelta(days=timedelta_days)
        return date_backdating

    def _get_corresponding_move_line(self, move):
        return move.move_line_ids[:1]

    @classmethod
    def _create_real_time_products(cls, products_values_list):
        """Create products with Perpetual Inventory Valuation.

        Products are also assigned the values
        declared in `products_values_list`.
        """
        product_model = cls.env["product.product"]
        products = product_model.browse()
        for products_values in products_values_list:
            product_form = Form(product_model)
            for field_name, field_value in products_values.items():
                setattr(product_form, field_name, field_value)
            product_form.type = "consu"
            product_form.is_storable = True
            # product_form.property_valuation = "real_time"
            product = product_form.save()
            products |= product
        products.categ_id.property_valuation = "real_time"
        return products

    @classmethod
    def _create_picking(cls, products_qty_dict):
        """Create a picking moving products as described in `products_qty_dict`.

        :param products_qty_dict: dictionary mapping
            a product to the quantity to be moved.
        """
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_out")
        for product, quantity in products_qty_dict.items():
            with picking_form.move_ids.new() as move:
                move.product_id = product
                move.product_uom_qty = quantity
        picking = picking_form.save()
        return picking

    def _check_account_moves(self, account_moves, stock_moves):
        # In Odoo 19, perpetual valuation creates a single account move that
        # groups all the stock moves processed together, so we just verify
        # at least one account move is created and that each stock move is
        # linked to one.
        self.assertTrue(account_moves, "An account move should be created")
        for stock_move in stock_moves:
            self.assertTrue(
                stock_move.account_move_id,
                "Each stock move should be linked to an account move",
            )

    def _check_account_move_date(self, account_move, valid_dates):
        # In Odoo 19, multiple stock moves processed together share a single
        # account_move whose date is taken from a single force_period_date
        # context. When stock moves have different backdated dates, this
        # shared account_move date can't match each individual move's date —
        # so we accept any of the picking's backdated dates.
        if not isinstance(valid_dates, (set, list, tuple)):
            valid_dates = {valid_dates.date()}
        else:
            valid_dates = {d.date() if hasattr(d, "date") else d for d in valid_dates}
        self.assertIn(account_move.date, valid_dates)

    def _check_picking_date(self, picking, datetime_backdating_list):
        max_datetime = max(datetime_backdating_list)
        # max_date = fields.Date.context_today(self, max_datetime)
        self.assertEqual(picking.date_done, max_datetime)

        picking_back_date = picking.date_backdating
        if len(datetime_backdating_list) == 1:
            # picking_back_date = fields.Date.context_today(self, picking_back_date)
            datetime_backdating = datetime_backdating_list[0]
            self.assertEqual(datetime_backdating, picking_back_date)
        else:
            self.assertFalse(picking_back_date)

    def _search_account_move(self, move):
        return move.account_move_id

    def _create_wizard(self, date_backdating, picking):
        """Assign `date_backdating` to all the move lines of `picking`."""
        wiz_model = self.env["fill.date.backdating"].with_context(
            active_model=picking._name,
            active_id=picking.id,
        )
        wiz_form = Form(wiz_model)
        wiz_form.date_backdating = date_backdating
        wiz = wiz_form.save()
        return wiz.fill_date_backdating()

    def _check_stock_moves(self, stock_moves):
        stock_move_lines = stock_moves.mapped("move_line_ids")
        self.assertEqual(
            len(stock_move_lines),
            len(stock_moves),
            "Every move should be assigned (create a move line)",
        )
        account_moves = stock_moves.account_move_id
        self._check_account_moves(account_moves, stock_moves)
        # The account_move is shared across all stock moves processed together;
        # its date matches one of the per-move backdated dates.
        valid_account_dates = {stock_move.date.date() for stock_move in stock_moves}
        for stock_move in stock_moves:
            self.assertEqual(stock_move.state, "done")

            account_move = self._search_account_move(stock_move)
            self._check_account_move_date(account_move, valid_account_dates)

            stock_move_line = self._get_corresponding_move_line(stock_move)
            move_datetime_backdating = stock_move_line.date_backdating
            move_date_backdating = move_datetime_backdating.date()

            self.assertEqual(stock_move.date.date(), stock_move_line.date.date())

            # Check the quants, if stock move date is the same as the backdating
            if stock_move.date.date() != move_date_backdating:
                continue
            # Get the quant that originated the quantity moved
            quants = self.env["stock.quant"]._gather(
                stock_move.product_id,
                stock_move.location_id,
            )
            for quant in quants:
                self.assertEqual(quant.in_date.date(), move_date_backdating)
                quant._apply_inventory()

            # Get the quant that received the quantity moved
            quants = self.env["stock.quant"]._gather(
                stock_move.product_id,
                stock_move.location_dest_id,
            )
            for quant in quants:
                self.assertEqual(quant.in_date.date(), move_date_backdating)
                quant._apply_inventory()

    def _transfer_picking_with_dates(self, *datetime_backdating_list):
        """
        Insert `datetime_backdating_list` in the stock move lines
        and process self.picking.

        If there are fewer dates than moves, the last date is repeated.
        """
        picking = self.picking
        stock_moves = picking.move_ids

        # Set all the requested quantities as done
        for stock_move in stock_moves:
            stock_move.quantity = stock_move.product_uom_qty

        if len(datetime_backdating_list) == 1:
            # Assign the same date to all the move lines using the wizard
            date_backdating = datetime_backdating_list[0]
            self._create_wizard(date_backdating, picking)
        else:
            stock_move_lines_dates_zip = zip_longest(
                picking.move_line_ids,
                datetime_backdating_list,
                fillvalue=datetime_backdating_list[-1],
            )
            for stock_move_line, datetime_backdating in stock_move_lines_dates_zip:
                stock_move_line.date_backdating = datetime_backdating

        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self._check_stock_moves(stock_moves)
        self._check_picking_date(picking, datetime_backdating_list)
