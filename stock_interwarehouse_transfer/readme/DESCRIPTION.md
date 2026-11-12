This module adds an **Inter-Warehouse Transfer** document that lets users
explicitly push stock from one warehouse to another within the same company.

Confirming a transfer creates exactly two pickings (OUT at the source warehouse,
IN at the destination warehouse) connected through the company's internal transit
location. The document state is automatically derived from the underlying picking
states and supports backorders.

To keep this the only path for moving stock across warehouses, the module also
blocks any **internal** stock move whose source and destination locations belong
to different warehouses, forcing users through the Inter-Warehouse Transfer
document.
