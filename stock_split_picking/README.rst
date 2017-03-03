.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Split picking
-------------

This module adds a "Split" button on the outgoing pickings form.

It will split the current picking so that any amounts you've selected on the picking operations will remain on this picking, while the rest are transferred to the new picking.

If the current picking is Partially Available, the split will work even if no amounts are processed, by leaving the current unprocessed operations on this picking and moving the rest to a new picking.

Installation
============

This module only needs `stock` module.

Known issues / Roadmap
======================

* This code relies on the context flag `do_only_split` to work properly. Comments in the code suggest Odoo SA may remove it in future, as the core Odoo funtionality does not make use of it
* Not possible currently to split a picking that is Awaiting Availability
* Tests are in yml, and should be ported to pure Python, since yml support is planned to be dropped in future Odoo versions
* German translations not updated for version 10.0

Credits
=======

Contributors
------------

* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Atte Isopuro <atte.isopuro@avoin.systems>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
