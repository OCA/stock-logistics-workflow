Stock Disallow Negative
=======================

By default, Odoo allows negative stock. The advantage of negative stock is that, if some stock levels are wrong in the ERP, you will not be blocked when validating the picking for a customer... so you will still be able to ship the products on time (it's an example !). The problem is that, after you forced the stock level to negative, you are supposed to fix the stock level later via an inventory ; but this action is often forgotten by users, so you end up with negative stock levels in your ERP and it can stay like this forever (or at least until the next full inventory).

If you disallow negative stock in Odoo with this module, you will be blocked when trying to validate a stock operation that will set the stock level of a product as negative. So you will have to fix the wrong stock level of that product without delay, in order to validate the stock operation in Odoo... you can't forget it anymore !

Configuration
=============

By default, the stockable products will not be allowed to have a negative stock. If you want to make some exceptions for some products or some product categories, you can activate the option *Allow Negative Stock* on some products or some products categories.

Usage
=====

When you validate a stock operation (a stock move, a picking, etc...) that will set the stock level of a stockable product as negative, you will be blocked by an error message. The consumable products can still have a negative stock level.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
