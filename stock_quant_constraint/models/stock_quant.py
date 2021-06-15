# Copyright 2020-2021 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)

UNIQUE_QUANTS_STATEMENT = """\
WITH grouped_quants AS (
     SELECT count(*) as kount, sum(quantity) as quantity,
     location_id, product_id, lot_id, package_id, lot_id
     FROM stock_quant
     GROUP BY location_id, product_id, lot_id, package_id, lot_id
 )
 SELECT * from grouped_quants where kount > 1;
"""

STOCK_STATEMENT = """\
-- A done stock move line, decreases a quant at the source location,
-- and increases or creates a quant at the destination location.

-- 1. Sum all incoming moves per location
-- 2. Sum all outgoing moves per location
-- 3. Sum all quants per location
-- (per location: per product, location, lot, package and owner)
-- The quantity per quant should be the quantity that went in
-- minus the quantity that went out.
WITH outgoing_moves AS (
    SELECT
        ml.product_id, ml.location_id,
        ml.lot_id, ml.package_id, ml.owner_id,
        SUM(ml.qty_done) AS qty_done
    FROM stock_move_line ml
    WHERE ml.state = 'done'
    GROUP BY
        ml.product_id, ml.location_id, ml.lot_id, ml.package_id, ml.owner_id
),
incoming_moves AS (
    SELECT
        ml.product_id, ml.location_dest_id,
        ml.lot_id, ml.package_id, ml.owner_id,
        SUM(ml.qty_done) AS qty_done
    FROM stock_move_line ml
    WHERE ml.state = 'done'
    GROUP BY
        ml.product_id, ml.location_dest_id, ml.lot_id, ml.package_id, ml.owner_id
),
quants AS (
    SELECT
        sq.product_id, sq.location_id,
            sq.lot_id, sq.package_id, sq.owner_id,
            sq.quantity
    FROM stock_quant sq
),
quant_summary AS (
    SELECT
        COALESCE(q.product_id, im.product_id, om.product_id) AS product_id,
            COALESCE(q.location_id, im.location_dest_id, om.location_id) AS location_id,
            COALESCE(q.lot_id, im.lot_id, om.lot_id) AS lot_id,
            COALESCE(q.package_id, im.package_id, om.package_id) AS package_id,
            q.quantity,
            COALESCE(q.owner_id, im.owner_id, om.owner_id) AS owner_id,
            im.qty_done AS quantity_in, om.qty_done AS quantity_out,
            COALESCE(q.quantity, 0) - (COALESCE(im.qty_done, 0)
                - COALESCE(om.qty_done, 0)) AS quantity_error
    FROM quants q
    FULL OUTER JOIN incoming_moves im ON
    q.product_id = im.product_id AND q.location_id = im.location_dest_id
    AND (q.lot_id = im.lot_id OR (q.lot_id IS NULL AND im.lot_id IS NULL))
    AND (q.package_id = im.package_id
        OR (q.package_id IS NULL AND im.package_id IS NULL))
    AND (q.owner_id = im.owner_id OR (q.owner_id IS NULL AND im.owner_id IS NULL))
    FULL OUTER JOIN outgoing_moves om ON
    q.product_id = om.product_id AND q.location_id = om.location_id
    AND (q.lot_id = om.lot_id OR (q.lot_id IS NULL AND om.lot_id IS NULL))
    AND (q.package_id = om.package_id
        OR (q.package_id IS NULL AND om.package_id IS NULL))
    AND (q.owner_id = om.owner_id OR (q.owner_id IS NULL AND om.owner_id IS NULL))
)
SELECT
    qs.product_id,
    qs.location_id,
    qs.package_id,
    qs.owner_id,
    qs.lot_id,
    COUNT(*) as kount,
    SUM(quantity) AS quant_quantity,
    SUM(quantity_in) AS quantity_in, SUM(quantity_out) AS quantity_out,
    SUM(quantity_error) AS quantity_error
    FROM quant_summary qs
    JOIN stock_location sl
    ON qs.location_id = sl.id
    WHERE quantity_error > 0.01
    AND sl.usage = 'internal'
    GROUP BY qs.location_id, qs.product_id, qs.package_id, qs.owner_id, qs.lot_id
    ORDER BY qs.location_id, product_id, qs.package_id, qs.owner_id, qs.lot_id
"""

RESERVED_STATEMENT = """
SELECT SUM(product_qty) AS reserved_in_moves
 FROM stock_move_line
 WHERE location_id = %(location_id)s
   AND product_id = %(product_id)s
"""


class StockQuant(models.Model):
    _inherit = "stock.quant"

    quantity_error = fields.Float(
        "Quantity",
        help="Difference between computed and actual quantity",
        readonly=True,
    )
    quantity_computed = fields.Float(
        "Quantity",
        help="Difference between computed and actual quantity",
        readonly=True,
    )

    @api.constrains("product_id", "reserved_quantity")
    def check_reserved_quantity(self):
        """Check the consistency of reservations.

        - reservations can only be done on physical locations;
        - the sum of reservations for a product on a location, must match the
          move lines having that location as a source location.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for quant in self:
            reserved_quantity = quant.reserved_quantity or 0.0
            location = quant.location_id
            if reserved_quantity > 0.0 and location.usage != "internal":
                raise ValidationError(
                    _(
                        "Invalid attempt to reserve product %s"
                        " for a location with usage %s."
                    )
                    % (quant.product_id.display_name, location.usage,)
                )
            if location.usage != "internal":
                continue
            # Compare reserved quantity in quant with moves for the location.
            parameters = {
                "location_id": self.location_id.id,
                "product_id": self.product_id.id,
            }
            self.env.cr.execute(RESERVED_STATEMENT, parameters)
            reserved_in_moves = self.env.cr.fetchone()
            comparison = float_compare(
                reserved_quantity, reserved_in_moves[0], precision_digits=precision
            )
            if comparison == 0:
                continue
            # We detected a mismatch between moves and quants.
            raise ValidationError(
                _(
                    "Mismatch between reserved product quantity according to"
                    " quants %s and accourding to moves %s for product %s"
                    " in location %s."
                )
                % (
                    reserved_quantity,
                    reserved_in_moves,
                    quant.product_id.display_name,
                    location.complete_name,
                )
            )

    @api.model
    def cron_check_quant_consistency(self):
        """Check consistency of quants when compared with stock move lines."""
        cursor = self.env.cr
        # First check wether quants have unique keys.
        quants_unique = True
        cursor.execute(UNIQUE_QUANTS_STATEMENT)
        for row in cursor.fetchall():
            quants_unique = False
            _logger.error(_("Duplicate quant keys %s"), str(row))
        if not quants_unique:
            raise UserError(_("Cron to check quants aborted because of duplicat keys"))
        # Continue checking quants for mismatches.
        cursor.execute(STOCK_STATEMENT)
        for row in cursor.fetchall():
            _logger.error(_("Mismatch in stock %s"), str(row))
            self._do_repair(row)

    def _do_repair(self, row):
        """Repair (or create) stock_quant, based on stock moves."""
