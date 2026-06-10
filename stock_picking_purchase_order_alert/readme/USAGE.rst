To configure the alert threshold:

#. Go to *Inventory > Configuration > Operation Types*
#. First, enable the "Display Quantity Alert" option
#. Set your desired threshold percentage (default is 30%)
#. You may optionally specify groups permitted to bypass the alert. If no groups are defined, the alert can be bypassed by any user.
#. Click *Save*

To use the module:

#. Create a purchase order and confirm it
#. When receiving products in the generated receipt:
   * If the quantity being received exceeds the ordered quantity by more than the configured threshold, a warning banner will appear above the product lines
   * The warning will show each product that exceeds the threshold, including the ordered quantity, received quantity, and excess percentage
   * The system will prevent validation of the receipt until the quantities are corrected to be within the acceptable threshold

How to handle quantities that exceed the threshold:

#. If the quantity is incorrect, adjust it to match the ordered quantity
#. If the quantity is correct and you need to accept it, you have two options:
   * Temporarily increase the threshold percentage in the settings
   * Temporarily disable the quantity alerts by unchecking "Display Quantity Alert Percentage"
   * Change the quantity on the purchase line to match the receipt value

Notes:

* The alert works with different units of measure between purchase order and receipt
* Setting the threshold to 0 will disable the threshold alerts, but the main feature must still be enabled via the checkbox
* Unchecking "Display Quantity Alert Percentage" will completely disable the feature
* The module is especially useful when receiving products in different units than ordered (e.g., ordered in dozens but received in units)
