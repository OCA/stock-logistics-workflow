This module adds alert notifications when the quantity being received in purchase receipts
exceeds the ordered quantity by more than a configurable threshold percentage (default 30%).

Often warehouse staff receive products in different units of measure than ordered,
which can lead to input errors. For example, if 6,000 units were ordered but the
staff tries to receive 60,000 units, this module will display a warning.

The module provides:

* A warning banner in the receipt form when quantities exceed the threshold
* A configurable feature that can be enabled/disabled via settings
* A configurable percentage threshold for when alerts should appear
* Proper handling of different units of measure between order and receipt
* Prevents validation of receipts when quantities exceed the threshold percentage
* Forces users to review and correct quantities before validating the receipt
