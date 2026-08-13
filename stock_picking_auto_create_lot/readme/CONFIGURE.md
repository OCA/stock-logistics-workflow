To use the auto-create feature you need to enable tracking by lots/serial numbers:

1.  Go to "Inventory > Configuration > Settings" and scroll down to the "Traceability" section;
2.  Enable the "Lots & Serial Numbers" setting;
3.  You can select the number of trailing zeroes for the SKU-based lots/serial numbers in the "SKU Based Numbers Trailing" field located in the same section. Default value is "0".

Configure the operation types:

1.  Go to  "Inventory > Configuration > Operation Types";
2.  Enable the "Auto Create Lot" setting located in the "Lots/Serial numbers" section.

Configure the products you want to enable lot/serial number auto-creation:

1.  Open the product form;
2.  Activate the "Track Inventory" setting and select either "By Unique Serial Number" or "By Lots" option;
3.  Select an option you would like to use for creating lots/serial numbers for this product in the "Auto Create Lot" field. Default options are:
    1.  Odoo sequence. Will use default Odoo sequence for newly created lots;
    2.  SKU based. Will use product reference as a base of the sequence and a number as a suffix joined by the "-" symbol. Eg for product with SKU "CHAIR-L-R" serial numbers will be "CHAIR-L-R-1", "CHAIR-L-R-2" etc. Note: if a product doesn't have an SKU default Odoo sequence will be used.
