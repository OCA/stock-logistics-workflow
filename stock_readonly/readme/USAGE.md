To grant read-only access to the stock documents, select *Readonly*
under the *Inventory* privilege in the user form (Settings / Users).

Holding the *Readonly* option grants read-only access to the stock
documents on the user, with no create, write or unlink right.

Users holding the group get:

* read access to transfers, moves, lots, scraps, reordering rules,
  package types and the traceability report;
* the *Operations* menus of the Inventory application: *Transfers*
  (*Receipts* and *Deliveries*) and *Adjustments* (*Physical Inventory*
  and *Scrap*).

Notes:

* The *Reporting* and *Configuration* menus remain reserved for
  Inventory administrators, and feature submenus still depend on their
  dedicated groups (e.g. *Internal* transfers require the *Manage
  Multiple Stock Locations* option, and *Lots/Serial Numbers* the
  corresponding option).
* Action buttons on the documents (e.g. validating a picking) are still
  displayed but raise an access error for users holding only this group.
