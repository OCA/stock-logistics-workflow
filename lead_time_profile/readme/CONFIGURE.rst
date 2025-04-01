To configure this module, you must first properly set up your lead time profiles:

1. Go to *Inventory > Configuration > Settings*. Find the section Lead Time
   Settings, and update the factors of warehouse, country, state and partner according
   to your specific requirements. Setting 0.0 means that matches of the corresponding
   field will not be counted in score calculation of the lead time profile.
2. Navigate to *Inventory > Configuration > Lead Time Profiles*, and create records
   based on your operational lead time requirements.

Example of how most matched lead time profile is determined for sales order:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When there are lead time profile records like this, and you have an order to deliver
from Main WH to Cust A:

+---------+-------+---------+-----------+------------+------------------+
| Country | State | Partner | Warehouse |   Model    | Lead Time (Days) |
+=========+=======+=========+===========+============+==================+
| Japan   | Tokyo | Cust A  |           | sale.order |              3.0 |
+---------+-------+---------+-----------+------------+------------------+
| Japan   | Tokyo |         | Main WH   | sale.order |              5.0 |
+---------+-------+---------+-----------+------------+------------------+
| Japan   | Tokyo |         | 2nd WH    | sale.order |              7.0 |
+---------+-------+---------+-----------+------------+------------------+

If the factors are configured to be like this:

- Country: 1.0
- State: 1.0
- Partner: 1.0
- Warehouse: 2.0

The scores of each profile will be calculated as follows:

+---------+-------+---------+-----------+------------------+------------+-------------------------------+
| Country | State | Partner | Warehouse | Lead Time (Days) | Model      | Score Calculation             |
+=========+=======+=========+===========+==================+============================================+
| Japan   | Tokyo | Cust A  |           |              3.0 | sale.order | 1.0 + 1.0 + 1.0 + 0.0 = 3.0   |
+---------+-------+---------+-----------+------------------+--------------------------------------------+
| Japan   | Tokyo |         | Main WH   |              5.0 | sale.order | 1.0 + 1.0 + 0.0 + 2.0 = 4.0   |
+---------+-------+---------+-----------+------------------+--------------------------------------------+
| Japan   | Tokyo |         | 2nd WH    |              7.0 | sale.order | N/A for warehouse mismatch    |
+---------+-------+---------+-----------+------------------+--------------------------------------------+

The profile with the highest score is considered the best match.

In a tie-breaking situation, the lead time profile with the lowest lead time will be chosen.
