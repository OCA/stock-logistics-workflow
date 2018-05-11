.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=================================================
Stock Picking Restrict Cancel With Original Moves
=================================================

This module restricts the cancelation of stock picking, if any move is linked
to a previous move, which is not canceled or done yet.

Usage
=====

Odoo allows to cancel any picking in a chain of moves between locations, and
will automatically cancel the ensuing moves but leaves the previous ones in
their actual state.

This module restricts this possibility and displays an error to the user,
listing all the stock pickings containing stock moves linked to the picking the
user is trying to cancel, so he can delete the original, ensuring all the
following pickings will be canceled as well.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock_logistics_workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Vincent Renaville <vincent.renaville@camptocamp.com>
* Akim Juillerat <akim.juillerat@camptocamp.com>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
