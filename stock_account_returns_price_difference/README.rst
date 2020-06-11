.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

===================================
Price Difference Account in Returns
===================================

Records the "cost" difference when returning goods to customer or suppliers to a separate general account.
Usefull to limits the ocurrence of unbalanced stock accounts due alterations of the cost of the product 
(for example due to new purchases) before the return.
Note that equivalente feature is available in anglo-saxon accounting, this module extends it to continental accounting. 

Usage
=====

1. Install this module
2. Configure the product category with average price and perpetual inventory, and of course a price differene account (which usually is an expense account).
3. And ready to go!... the accounting entry will be automatically generated when a difference occurs (you can test it by changing the product cost just before the return).

Known issues / Roadmap
======================

 * No improvement is anticipated


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistic-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/stock-logistic-workflow/issues/new?body=module:%20auditlog%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Andres Calle <andres.calle@trescloud.com>
* Jose M Rivero <jose.rivero@trescloud.com>
* Several others who contributed to the stock_account module

Images
------

* Odoo Community Association: 'Icon <https://freeicons.io/email-icons03/email-icon-28814>'_.

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
