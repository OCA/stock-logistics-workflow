Sale Stock Partner Delivery Window
==================================

This module extends Sales and Inventory to respect the customer’s
delivery schedule preferences when computing delivery dates.

When a Sales Order line computes its expected delivery date, the module
checks the customer’s *Delivery schedule preference* and automatically
adjusts the date to the next valid delivery slot.

Supported delivery preferences include:

* **Anytime**
  
  Deliveries can occur at any date and time.

* **Workdays only**
  
  Deliveries are automatically postponed to the next weekday if the
  computed date falls on a weekend.

* **Configured delivery time windows**
  
  Deliveries are restricted to specific weekdays and time ranges defined
  on the customer record.

  If the computed expected date does not match an allowed window, the
  module selects the next available delivery slot.

Additional features:

* Delivery windows are evaluated in the customer’s timezone.
* The adjusted expected date is propagated to generated delivery orders.
* A warning is displayed on the Sales Order when the manually selected
  commitment date does not match the customer’s delivery preferences.

This ensures that promised delivery dates remain aligned with customer
logistics constraints and preferred receiving schedules.
