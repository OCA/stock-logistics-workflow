This module avoid to reserve goods if the planned consumed date by
the customer is after expiration time.

.. note::

    This module du not change the fefo strategy implementation and won't
    optimized reservations. First order still reserve the first Expired goods
    even the expected consumed date is later.
