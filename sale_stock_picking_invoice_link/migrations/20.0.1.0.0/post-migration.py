# Copyright 2026 ADHOC SA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import SUPERUSER_ID, api

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

    Reversing an invoice copies its links to the credit note on purpose
    (`stock_picking_invoice_link`), so the move stays linked to the reversed
    invoice too. The bug replaced the links instead, so a move that is still
    linked to the reversed invoice is left as it is.

    `account.move.picking_ids` is stored and computed from these links, so it
    is recomputed for every invoice and credit note touched.
    """
    cr.execute(
        """
        SELECT rel.move_id, rel.invoice_line_id, am.id
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
           AND NOT EXISTS (
               SELECT 1
                 FROM stock_move_invoice_line_rel rel2
                 JOIN account_move_line aml2 ON aml2.id = rel2.invoice_line_id
                WHERE rel2.move_id = rel.move_id
                  AND aml2.move_id = am.reversed_entry_id
           )
        """
    )
    rows = cr.fetchall()
    if not rows:
        return

    wrong_links = tuple((move_id, line_id) for move_id, line_id, __ in rows)
    move_ids = tuple({move_id for move_id, __, __ in rows})
    account_move_ids = {am_id for __, __, am_id in rows}
    cr.execute(
        """
        DELETE FROM stock_move_invoice_line_rel
         WHERE (move_id, invoice_line_id) IN %s
        """,
        (wrong_links,),
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
          RETURNING (
              SELECT move_id FROM account_move_line WHERE id = invoice_line_id
          )
        """,
        (move_ids,),
    )
    relinked = cr.fetchall()
    account_move_ids |= {am_id for (am_id,) in relinked}
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

    env = api.Environment(cr, SUPERUSER_ID, {})
    account_moves = env["account.move"].browse(account_move_ids)
    env.add_to_compute(env["account.move"]._fields["picking_ids"], account_moves)
    env.flush_all()
    _logger.info(
        "sale_stock_picking_invoice_link: %s wrong links removed from credit "
        "notes, %s links written to the invoice, %s moves left with no invoice "
        "line of their own, %s invoices and credit notes recomputed",
        len(wrong_links),
        len(relinked),
        orphans,
        len(account_moves),
    )
