# Stock Picking Bill Matching

This module bridges the gap between Accounting and Warehouse operations in Odoo by allowing users to match Vendor Bills directly against Incoming Stock Pickings, bypassing the need for a Purchase Order.

It brings a paradigm native to Odoo 18.0 (Bill Matching) into Odoo 16 but elevates it by matching against `stock.move` lines instead of `purchase.order.line`.

## Key Features
* **Unified Matching Interface:** A single screen (SQL View) showing unmatched Vendor Bill lines and Incoming Receipt lines side-by-side.
* **Many-to-Many Linking:** Leverages the `stock_picking_invoice_link` OCA module to allow complex many-to-many relationships (e.g., partial billing, consolidated billing).
* **Smart Auto-Reception:** Matching bill lines with pending receipts automatically validates the receipt and handles backorders safely using native Odoo logic.
* **Small Shop Replenishment:** Easily generate brand-new Incoming Receipts straight from a drafted Vendor Bill with a single click.
* **Extensibility:** Built with an extensible matching hook (`_get_matching_pairs`) to allow localization modules (like the Brazilian NFe `xPed`/`nItemPed`) to override the default product-based matching behavior.
* **Compatibility:** If the `stock_picking_invoicing` module is installed, matching or unmatching lines automatically updates the invoice state (`invoiced` / `2binvoiced`) on stock moves and pickings.
