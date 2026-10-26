This module allows you to define whether a Serial Number/lot is blocked
or not. The default value can be set on the Product Category, in the
field "Block new Serial Numbers/lots". It's possible to specify in a
location if locked lots are allowed to move there.

Additionally, locked lots are automatically excluded from stock reservations,
preventing them from being allocated to outgoing orders. This ensures that
blocked inventory cannot be accidentally reserved or shipped. The reservation
exclusion can be bypassed using the 'force_allow_locked_lots' context when
explicitly needed.
