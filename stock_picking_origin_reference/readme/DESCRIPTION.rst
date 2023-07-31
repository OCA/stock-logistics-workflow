The Source Document contains a text referencing to the Odoo document from which
the transfer has been created. This module replaces the Source Document field for a
field with the same label which is clickable and redirects the user to the document.

If there is an existing Odoo document with the same name as the value in the Source
Document, the Odoo field is hidden, and the new field is shown by default. Otherwise, it's left as it is.

It also adds the base strucuture in order to reference documents from different Odoo
models.
