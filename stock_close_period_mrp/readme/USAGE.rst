Close period production recompute
=================================

In the close period record there is a new button to recompute product prices on BOM values and time spent:

.. image:: ../static/description/compute_production_price.png
    :alt: Compute BOM prices

This value is computed with this formula:

- duration expected = time start + time stop + (sum of time cycle * time efficiency / 100)
- price of operations = duration expected / 60 * hour cost of workcenter
- price of components = sum of components * quantity * price (recursive)
- total price = price of operations + price of components

It is possible to get product prices from standard price, without computation, by flagging the option "Force Standard Price":

.. image:: ../static/description/force_standard_price.png
    :alt: Force Standard Price
