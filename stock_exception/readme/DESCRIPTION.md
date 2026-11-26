This module adds exception rules to transfers, built on `base_exception`.
A rule describes a situation that needs attention before a transfer goes
ahead: a delivery without contact, a quantity that is too large, a product
without data needed for shipping, and so on.

Rules can check the transfer (`stock.picking`) or its stock moves
(`stock.move`); an exception found on a move is shown on its transfer. They
are checked:

- when the transfer is confirmed, including when another document confirms
  it, such as a sale or purchase order;
- when the transfer is validated;
- by the scheduled action *Stock: Test Draft Pickings Exception*, for draft
  transfers (inactive by default).

A rule either **warns** (the user can ignore it and go on) or **blocks**
(*Is Blocking*: the transfer cannot be validated until the cause is fixed).
