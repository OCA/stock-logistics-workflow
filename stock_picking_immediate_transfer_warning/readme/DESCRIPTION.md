In Odoo < 17, when validating a stock transfer where all lines had reserved
quantities but no done quantities were recorded, a wizard would warn the user
that all reserved quantities would be processed, giving them the option to
cancel or proceed.

Since Odoo >= 17, the `qty_done` field was replaced by a `picked` boolean on stock
moves. However, when no move has been explicitly marked as picked, Odoo
silently marks all moves as picked and processes the transfer without any
warning.

This module restores the previous behavior by showing a confirmation wizard
when validating a transfer where no moves have been explicitly picked. The user
can then choose to proceed with processing all reserved quantities or discard
the operation. We only show the wizard when the validation is done from the UI, to prevent other logics to fail.
