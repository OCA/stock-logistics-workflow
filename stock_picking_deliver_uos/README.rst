.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Stock Picking Deliver UOS
=========================

This module adds two fields, uos and uos quantity on Stock Transfer Details
wizard allowing the user to use the uos quantity (instead of the standard uom)
to specify the quantity to be delivered.

For example if i have to deliver 3 tables (uos qty=3 uos=pz) each one of 1,5 m²
(uom=m², line uom qty=4,5), I can make a transfer specifying 2 pieces (the
system computes the internal uom qty:  3 m²)

Credits
=======

Contributors
------------

* Alex Comba <alex.comba@agilebg.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
