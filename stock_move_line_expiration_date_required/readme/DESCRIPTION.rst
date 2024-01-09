This module causes Stock Move Lines with products that have been configured to use an
expiration date and have the expiration time set to 0 days after receipt to
have their expiration date filled in manually and not be auto-calculated.

Expiration date on product that have been configured to use an expiration date will be a required field.

If you configure a product to use an expiration date and you do not set the expiration time (0 days after receipt)
then you will be required to manually enter the expiration date on the stock move line, otherwise, expiration date will be auto-calculated as usual.

Pickings with products configured with an expiration date will not be allowed to be confirmed if any of his stock move lines (related to products with expiration date) have an empty expiration date.
