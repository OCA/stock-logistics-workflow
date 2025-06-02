This module avoids to reserve goods having an expiration time prior
to the customer's planned consumed date.

.. note::

    This module du not change the fefo strategy implementation and won't
    optimized reservations. First order still reserve the first Expired goods
    even the expected consumed date is later.