This module adds the field `Bypass if stock exists` on stock rule of type `Buy`.

When a procurement is run and there is available stock for the related product,
the stock rules with this flag set will be discarded by the system and the next
rule will be applied.
