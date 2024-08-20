Let's imagine you have a parcel forwarding business.
You receive small packages from your customer pack them into bigger ones and forward afterwards.

To complete this operation using the standard Odoo flow:

- Create a new picking
- Add each item of the "Source package" to the list of operations
- Manually set the "Destination package" for each line
- Validate
- Items from the source package are moved to the destination package

This is really time consuming and not convenient because you just want to move the entire package at once. Especially if you want to move multiple packages at once each of them containing multiple items.

With this module you get the following:

- Create a new picking
- Add packages directly in the "Move packages" list
- Define the "Destination package"
- Validate
- Items from the source package are moved to the destination package


Pros: instead of scanning each package item separately and configuring a destination for it we can do the same operation on the package level much faster and more convenient.
