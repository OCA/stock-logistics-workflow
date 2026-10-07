When the *Email Confirmation* option of Inventory is enabled, Odoo sends the delivery
confirmation email while the transfer is being validated. Rendering the delivery slip
attached to that email can take a few seconds, and the user has to wait for it before
the validation finishes.

This module posts that email in a queue job instead, so the validation does not wait for
the PDF. Everything else done when a transfer is validated (for example, the shipping
label requested to the carrier) still runs as usual.
