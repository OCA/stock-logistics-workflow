# Copyright 2026 ADHOC SA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Re-link deliveries that point to the credit note instead of the invoice.

    The link was written as `out_refund` whenever the move had `to_refund` set,
    and since 19.0 `stock_account` sets that field by `default=True` on every
    move. So an outgoing move of an order that has a credit note was linked to
    the credit note, and the invoice was left with no pickings. The code no
    longer does that, but the rows already written stay wrong.

    A move refunds only when it comes back from the customer, so a link is
    wrong when the move leaves to a customer location and the line belongs to
    an `out_refund`. Those links move to the lines of the `out_invoice` of the
    same sale order line.
    """
    cr.execute(
        """
        SELECT rel.move_id, rel.invoice_line_id
          FROM stock_move_invoice_line_rel rel
          JOIN stock_move sm ON sm.id = rel.move_id
          JOIN stock_location src ON src.id = sm.location_id
          JOIN stock_location dst ON dst.id = sm.location_dest_id
          JOIN account_move_line aml ON aml.id = rel.invoice_line_id
          JOIN account_move am ON am.id = aml.move_id
         WHERE am.move_type = 'out_refund'
           AND dst.usage = 'customer'
           AND src.usage != 'customer'
           AND sm.sale_line_id IS NOT NULL
        """
    )
    wrong_links = cr.fetchall()
    if not wrong_links:
        return

    move_ids = tuple({move_id for move_id, __ in wrong_links})
    cr.execute(
        """
        DELETE FROM stock_move_invoice_line_rel
         WHERE (move_id, invoice_line_id) IN %s
        """,
        (tuple(wrong_links),),
    )
    cr.execute(
        """
        INSERT INTO stock_move_invoice_line_rel (move_id, invoice_line_id)
             SELECT sm.id, aml.id
               FROM stock_move sm
               JOIN sale_order_line_invoice_rel rel
                 ON rel.order_line_id = sm.sale_line_id
               JOIN account_move_line aml ON aml.id = rel.invoice_line_id
               JOIN account_move am ON am.id = aml.move_id
              WHERE sm.id IN %s
                AND am.move_type = 'out_invoice'
                AND am.state != 'cancel'
        ON CONFLICT DO NOTHING
        """,
        (move_ids,),
    )
    relinked = cr.rowcount
    cr.execute(
        """
        SELECT count(*)
          FROM stock_move sm
         WHERE sm.id IN %s
           AND NOT EXISTS (
               SELECT 1
                 FROM stock_move_invoice_line_rel rel
                WHERE rel.move_id = sm.id
           )
        """,
        (move_ids,),
    )
    orphans = cr.fetchone()[0]
    _logger.info(
        "sale_stock_picking_invoice_link: %s wrong links removed from credit "
        "notes, %s links written to the invoice, %s moves left with no invoice "
        "line of their own",
        len(wrong_links),
        relinked,
        orphans,
    )
